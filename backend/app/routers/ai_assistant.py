import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from langchain_community.chat_models import ChatOllama
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from ..config import settings
from ..deps import get_db
from .. import schemas, crud, models
from ..auth import get_current_user

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])

CHAT_MODEL = "llama3.1:latest"
STOP_WORDS = {"a", "an", "the", "and", "or", "for", "to", "in", "at", "of", "me",
              "good", "great", "best", "find", "recommend", "want", "like", "near",
              "restaurant", "restaurants", "food", "place", "places", "some", "any",
              "i", "can", "you", "with", "get", "give", "show", "tonight", "today"}

llm = ChatOllama(model=CHAT_MODEL, base_url="http://localhost:11434", temperature=0.7, num_predict=120)

tavily_search = None
if settings.TAVILY_API_KEY:
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        tavily_search = TavilySearchResults(max_results=3, tavily_api_key=settings.TAVILY_API_KEY)
    except Exception:
        pass


def select_candidates(query: str, restaurants, top_n=3) -> list:
    keywords = [w for w in query.lower().split() if w not in STOP_WORDS and len(w) > 2]
    scored = []
    for r in restaurants:
        text = " ".join([
            r.name, r.cuisine_type or "", r.description or "",
            r.city or "", r.ambiance or "",
        ]).lower()
        score = sum(text.count(kw) for kw in keywords)
        if score > 0:
            scored.append((score, r.avg_rating or 0, r))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [r for _, _, r in scored[:top_n]]


def build_system_prompt(preferences, candidates, web_context=""):
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

    if candidates:
        lines = [f"- {r.name}: {r.description or r.cuisine_type}" for r in candidates]
        restaurant_text = "\n".join(lines)
    else:
        restaurant_text = "None"

    return f"""You are a restaurant recommendation assistant. Restaurant cards with full details are shown to the user separately — do NOT repeat prices, ratings, cuisines, or locations.

User preferences: {pref_text}
Matching restaurants:
{restaurant_text}

Write 1-3 plain sentences (no lists, no bullet points, no bold, no formatting) explaining why these restaurants suit the user's request. Name each restaurant once. Nothing else."""


FILLER_STARTS = (
    "here are", "i've", "i have", "based on", "these are", "these places",
    "these recommendations", "they also", "all of", "let me", "sure", "great",
    "of course", "below are", "the following",
)

def truncate_reply(text: str, candidate_names: list[str], max_sentences: int = 3) -> str:
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'-\s+', '', text)
    text = re.sub(r'\s{2,}', ' ', text).strip()

    all_sentences = re.split(r'(?<=[.!?])\s+', text)
    names_lower = [n.lower() for n in candidate_names]

    # Prefer sentences that mention a restaurant; fall back to any non-filler sentence
    restaurant_sentences = [
        s for s in all_sentences
        if any(name in s.lower() for name in names_lower)
    ]
    if restaurant_sentences:
        return " ".join(restaurant_sentences[:max_sentences])

    non_filler = [
        s for s in all_sentences
        if not s.lower().startswith(FILLER_STARTS)
    ]
    return " ".join((non_filler or all_sentences)[:max_sentences])


def extract_description(reply: str, restaurant_name: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', reply)
    name_lower = restaurant_name.lower()
    for sentence in sentences:
        if name_lower in sentence.lower():
            return sentence.strip()
    return ""


def tavily_enrich(query: str) -> str:
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
        preferences = crud.get_preferences(db, user.id)
        all_restaurants = crud.list_restaurants(db, 0, 200)
        candidates = select_candidates(payload.message, all_restaurants)

        web_context = tavily_enrich(payload.message)
        system_prompt = build_system_prompt(preferences, candidates, web_context)

        messages = [SystemMessage(content=system_prompt)]
        for msg in (payload.conversation_history or []):
            role = msg.get("role")
            if role == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif role == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=payload.message))

        response = llm.invoke(messages)
        reply = truncate_reply(response.content, [r.name for r in candidates])

        recommendations = [
            {
                "id": r.id,
                "name": r.name,
                "cuisine": r.cuisine_type,
                "rating": r.avg_rating,
                "price": r.price_range,
                "city": r.city,
                "description": extract_description(reply, r.name),
            }
            for r in candidates
        ]

        return {"response": reply, "recommendations": recommendations}

    except Exception as e:
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            return keyword_fallback(db, user, payload.message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


def keyword_fallback(db: Session, user: models.User, message: str):
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
                "description": "",
            })

    if matches:
        names = ", ".join(m["name"] for m in matches[:3])
        response_text = f"Based on your query, here are some matches: {names}. Would you like more details on any of them?"
    else:
        response_text = "I couldn't find restaurants matching your query. Try searching by cuisine type or city name."

    return {"response": response_text, "recommendations": matches[:3]}
