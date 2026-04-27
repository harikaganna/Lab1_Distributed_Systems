import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from langchain_community.chat_models import ChatOllama
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from shared.database import get_db
from shared.auth import get_current_user

app = FastAPI(title="AI Assistant Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    recommendations: List[dict] = []


def get_restaurants(db):
    restaurants = list(db.restaurants.find({}, {"_id": 1, "name": 1, "cuisine_type": 1,
                                                 "city": 1, "price_range": 1, "description": 1,
                                                 "ambiance": 1, "amenities": 1}))
    for r in restaurants:
        r["id"] = str(r.pop("_id"))
    return restaurants


def get_review_stats(db, restaurant_id):
    pipeline = [
        {"$match": {"restaurant_id": restaurant_id}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}},
    ]
    result = list(db.reviews.aggregate(pipeline))
    if result:
        return round(result[0]["avg_rating"], 1), result[0]["count"]
    return None, 0


def build_system_prompt(restaurants, db):
    lines = []
    for r in restaurants:
        avg, count = get_review_stats(db, r["id"])
        rating_str = f"{avg}★ ({count} reviews)" if avg else "No ratings yet"
        amenities = f", amenities: {r['amenities']}" if r.get("amenities") else ""
        lines.append(
            f"- {r['name']} | {r.get('cuisine_type','').title()} | {r.get('city','')} | "
            f"{r.get('price_range','N/A')} | {rating_str}{amenities}"
        )

    restaurant_list = "\n".join(lines) if lines else "No restaurants available."

    return f"""You are a friendly restaurant recommendation assistant for a Yelp-like app.

Available restaurants:
{restaurant_list}

Instructions:
- Recommend restaurants from the list above based on the user's query.
- Be conversational and explain why each recommendation fits.
- Mention the restaurant name, cuisine, price range, and rating when recommending.
- If asked about amenities like wifi, outdoor seating, or parking, use the amenities data.
- If nothing matches well, say so honestly.
- Keep responses concise and helpful."""


MEAL_KEYWORDS = {"dinner", "lunch", "breakfast", "brunch", "eat", "food", "meal", "tonight",
                  "restaurant", "place", "find", "recommend", "suggestion", "hungry", "want"}

def keyword_fallback(message: str, restaurants: list, db) -> dict:
    keywords = [w for w in message.lower().split() if w not in MEAL_KEYWORDS]
    matches = []
    for r in restaurants:
        text = " ".join([
            r.get("name", ""), r.get("cuisine_type", ""),
            r.get("description", ""), r.get("city", ""),
            r.get("ambiance", ""), r.get("amenities", ""),
        ]).lower()
        if keywords and any(kw in text for kw in keywords):
            avg, count = get_review_stats(db, r["id"])
            matches.append({
                "id": r["id"], "name": r["name"],
                "cuisine": r.get("cuisine_type"), "rating": avg,
                "price": r.get("price_range"), "city": r.get("city"),
            })

    # no keyword matches — return top-rated restaurants as a general suggestion
    if not matches:
        all_rated = []
        for r in restaurants:
            avg, count = get_review_stats(db, r["id"])
            if avg:
                all_rated.append({
                    "id": r["id"], "name": r["name"],
                    "cuisine": r.get("cuisine_type"), "rating": avg,
                    "price": r.get("price_range"), "city": r.get("city"),
                })
        matches = sorted(all_rated, key=lambda x: x["rating"] or 0, reverse=True)[:5]
        names = ", ".join(m["name"] for m in matches)
        response_text = (f"Here are some of our top-rated restaurants: {names}. "
                         f"You can also search by cuisine (e.g. 'Mexican', 'Chinese'), city, or amenity (e.g. 'wifi', 'outdoor seating').")
    else:
        names = ", ".join(m["name"] for m in matches[:5])
        response_text = f"Based on your query, here are some matches: {names}. Would you like more details on any of them?"

    return {"response": response_text, "recommendations": matches[:5]}


@app.post("/ai-assistant/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, user=Depends(get_current_user)):
    db = get_db()
    restaurants = get_restaurants(db)

    try:
        llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.7)
        system_prompt = build_system_prompt(restaurants, db)

        messages = [SystemMessage(content=system_prompt)]
        for msg in (payload.conversation_history or []):
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=payload.message))

        response = llm.invoke(messages)
        reply = response.content

        recommendations = []
        for r in restaurants:
            if r["name"].lower() in reply.lower():
                avg, _ = get_review_stats(db, r["id"])
                recommendations.append({
                    "id": r["id"], "name": r["name"],
                    "cuisine": r.get("cuisine_type"), "rating": avg,
                    "price": r.get("price_range"), "city": r.get("city"),
                })

        return {"response": reply, "recommendations": recommendations[:5]}

    except Exception as e:
        error_str = str(e).lower()
        if any(w in error_str for w in ["connection", "refused", "connect", "timeout"]):
            return keyword_fallback(payload.message, restaurants, db)
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@app.get("/")
def health():
    return {"status": "ok", "service": "ai", "model": OLLAMA_MODEL, "ollama": OLLAMA_BASE_URL}
