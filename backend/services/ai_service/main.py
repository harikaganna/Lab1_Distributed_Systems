import os
import re
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

STOP_WORDS = {"a", "an", "the", "and", "or", "for", "to", "in", "at", "of", "me",
              "good", "great", "best", "find", "recommend", "want", "like", "near",
              "restaurant", "restaurants", "food", "place", "places", "some", "any",
              "i", "can", "you", "with", "get", "give", "show", "tonight", "today"}

FILLER_STARTS = (
    "here are", "i've", "i have", "based on", "these are", "these places",
    "these recommendations", "they also", "all of", "let me", "sure", "great",
    "of course", "below are", "the following",
)


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


def find_relevant_restaurants(query: str, restaurants: list, db, top_n=3) -> list:
    keywords = [w for w in query.lower().split() if w not in STOP_WORDS and len(w) > 2]
    scored = []
    for r in restaurants:
        text = " ".join([
            r.get("name", ""), r.get("cuisine_type", ""), r.get("description", ""),
            r.get("city", ""), r.get("ambiance", ""), r.get("amenities", ""),
        ]).lower()
        score = sum(text.count(kw) for kw in keywords)
        if score > 0:
            avg, _ = get_review_stats(db, r["id"])
            scored.append((score, avg or 0, r, avg))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [
        {"id": r["id"], "name": r["name"], "cuisine": r.get("cuisine_type"),
         "rating": avg, "price": r.get("price_range"), "city": r.get("city"),
         "description": r.get("description", "")}
        for _, _, r, avg in scored[:top_n]
    ]


def build_system_prompt(candidates: list) -> str:
    if not candidates:
        restaurant_list = "None"
    else:
        lines = [f"- {r['name']}: {r.get('description') or r.get('cuisine') or ''}" for r in candidates]
        restaurant_list = "\n".join(lines)

    return f"""You are a restaurant recommendation assistant. Restaurant cards with full details are shown to the user separately — do NOT repeat prices, ratings, cuisines, or locations.

Matching restaurants:
{restaurant_list}

Write 1-3 plain sentences (no lists, no bullet points, no bold, no formatting) explaining why these restaurants suit the user's request. Name each restaurant once. Nothing else."""


def truncate_reply(text: str, candidate_names: list, max_sentences: int = 3) -> str:
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'-\s+', '', text)
    text = re.sub(r'\s{2,}', ' ', text).strip()

    all_sentences = re.split(r'(?<=[.!?])\s+', text)
    names_lower = [n.lower() for n in candidate_names]

    restaurant_sentences = [
        s for s in all_sentences
        if any(name in s.lower() for name in names_lower)
    ]
    if restaurant_sentences:
        return " ".join(restaurant_sentences[:max_sentences])

    non_filler = [s for s in all_sentences if not s.lower().startswith(FILLER_STARTS)]
    return " ".join((non_filler or all_sentences)[:max_sentences])


def extract_description(reply: str, restaurant_name: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', reply)
    name_lower = restaurant_name.lower()
    for sentence in sentences:
        if name_lower in sentence.lower():
            return sentence.strip()
    return ""


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

        if any(kw in text for kw in keywords):
            avg, _ = get_review_stats(db, r["id"])
        if keywords and any(kw in text for kw in keywords):
            avg, count = get_review_stats(db, r["id"])
            matches.append({
                "id": r["id"], "name": r["name"],
                "cuisine": r.get("cuisine_type"), "rating": avg,
                "price": r.get("price_range"), "city": r.get("city"),
                "description": "",
            })


    if matches:
        names = ", ".join(m["name"] for m in matches[:3])
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

    return {"response": response_text, "recommendations": matches[:3]}


@app.post("/ai-assistant/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, user=Depends(get_current_user)):
    db = get_db()
    restaurants = get_restaurants(db)
    candidates = find_relevant_restaurants(payload.message, restaurants, db)

    try:
        llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.7, num_predict=120)
        system_prompt = build_system_prompt(candidates)

        messages = [SystemMessage(content=system_prompt)]
        for msg in (payload.conversation_history or []):
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=payload.message))

        response = llm.invoke(messages)
        reply = truncate_reply(response.content, [r["name"] for r in candidates])

        for r in candidates:
            r["description"] = extract_description(reply, r["name"])

        return {"response": reply, "recommendations": candidates}

    except Exception as e:
        error_str = str(e).lower()
        if any(w in error_str for w in ["connection", "refused", "connect", "timeout"]):
            return keyword_fallback(payload.message, restaurants, db)
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@app.get("/")
def health():
    return {"status": "ok", "service": "ai", "model": OLLAMA_MODEL, "ollama": OLLAMA_BASE_URL}
