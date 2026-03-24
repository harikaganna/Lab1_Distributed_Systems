from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from langchain_community.chat_models import ChatOllama
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from ..config import settings
from ..deps import get_db
from .. import schemas, crud, models
from ..auth import get_current_user

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])

CHAT_MODEL = "phi3:mini"

# using ollama locally so we dont need an openai key
llm = ChatOllama(model=CHAT_MODEL, base_url="http://localhost:11434", temperature=0.7)

# tavily for web search enrichment (optional, needs api key)
tavily_search = None
if settings.TAVILY_API_KEY:
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        tavily_search = TavilySearchResults(max_results=3, tavily_api_key=settings.TAVILY_API_KEY)
    except Exception:
        pass


def build_system_prompt(preferences, restaurants, web_context=""):
    # put together the system prompt with user prefs + restaurant list
    pref_text = "No preferences saved."
    if preferences:
        parts = []
        if preferences.cuisine_preferences:
            parts.append(f"Cuisine: {preferences.cuisine_preferences}")
        if preferences.price_range:
            parts.append(f"Price: {preferences.price_range}")
        if preferences.dietary_needs:
            parts.append(f"Dietary: {preferences.dietary_needs}")
        if preferences.ambiance_preferences:
            parts.append(f"Ambiance: {preferences.ambiance_preferences}")
        if preferences.preferred_location:
            parts.append(f"Location: {preferences.preferred_location}")
        if parts:
            pref_text = "; ".join(parts)

    restaurant_text = "No restaurants in database."
    if restaurants:
        lines = []
        for r in restaurants:
            rating = f"{r.avg_rating}★" if r.avg_rating else "No ratings"
            price = r.price_range or "N/A"
            desc = r.description or "No description"
            lines.append(f"- ID:{r.id} {r.name} ({r.cuisine_type}, {price}, {rating}, {r.city}): {desc}")
        restaurant_text = "\n".join(lines)

    web_section = ""
    if web_context:
        web_section = f"\n\nAdditional web context (from Tavily search):\n{web_context}"

    return f"""You are a helpful restaurant recommendation assistant for a Yelp-like app.
User preferences: {pref_text}

Available restaurants:
{restaurant_text}{web_section}

Instructions:
- Recommend restaurants from the list above based on the user's query and preferences.
- Be conversational and explain why each recommendation matches.
- Always mention the restaurant name, cuisine, price range, and rating.
- If nothing matches well, say so honestly and suggest alternatives.
- Keep responses concise (3-5 sentences per recommendation)."""


def tavily_enrich(query: str) -> str:
    # try to get some extra context from the web using tavily
    if not tavily_search:
        return ""
    try:
        results = tavily_search.invoke(query)
        if results:
            snippets = [r.get("content", "")[:200] for r in results[:3] if isinstance(r, dict)]
            return "\n".join(snippets)
    except Exception:
        pass
    return ""


@router.post("/chat", response_model=schemas.ChatResponse)
def chat(
    payload: schemas.ChatRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    try:
        # grab user prefs and all restaurants from db
        preferences = crud.get_preferences(db, user.id)
        all_restaurants = crud.list_restaurants(db, 0, 200)

        # see if tavily can give us anything useful
        web_context = tavily_enrich(payload.message)

        system_prompt = build_system_prompt(preferences, all_restaurants, web_context)

        # build up the conversation for langchain
        messages = [SystemMessage(content=system_prompt)]
        for msg in (payload.conversation_history or []):
            role = msg.get("role")
            if role == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif role == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=payload.message))

        # send to ollama via langchain
        response = llm.invoke(messages)
        reply = response.content

        # check which restaurants got mentioned so we can show cards
        recommendations = []
        for restaurant in all_restaurants:
            if restaurant.name.lower() in reply.lower():
                recommendations.append({
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "cuisine": restaurant.cuisine_type,
                    "rating": restaurant.avg_rating,
                    "price": restaurant.price_range,
                    "city": restaurant.city,
                })

        return {"response": reply, "recommendations": recommendations[:5]}

    except Exception as e:
        # fallback if ollama isn't running
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            return keyword_fallback(db, user, payload.message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


def keyword_fallback(db: Session, user: models.User, message: str):
    # basic keyword matching when the llm is down
    keywords = message.lower().split()
    all_restaurants = crud.list_restaurants(db, 0, 200)

    matches = []
    for restaurant in all_restaurants:
        searchable_text = " ".join([
            restaurant.name, restaurant.cuisine_type,
            restaurant.description or "", restaurant.city,
            restaurant.ambiance or "",
        ]).lower()
        if any(keyword in searchable_text for keyword in keywords):
            matches.append({
                "id": restaurant.id,
                "name": restaurant.name,
                "cuisine": restaurant.cuisine_type,
                "rating": restaurant.avg_rating,
                "price": restaurant.price_range,
                "city": restaurant.city,
            })

    if matches:
        names = ", ".join(m["name"] for m in matches[:5])
        response_text = f"Based on your query, I found these restaurants: {names}. Would you like more details on any of them?"
    else:
        response_text = "I couldn't find restaurants matching your query. Try searching by cuisine type or city name."

    return {"response": response_text, "recommendations": matches[:5]}
