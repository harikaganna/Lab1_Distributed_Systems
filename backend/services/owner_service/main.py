import os
import sys
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.database import get_db
from shared.auth import get_current_user
from shared.kafka_producer import publish_event

app = FastAPI(title="Owner Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


def _review_stats(db, restaurant_id: str) -> dict:
    result = list(db.reviews.aggregate([
        {"$match": {"restaurant_id": restaurant_id}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "review_count": {"$sum": 1}}},
    ]))
    if result:
        return {"avg_rating": round(result[0]["avg_rating"], 2), "review_count": result[0]["review_count"]}
    return {"avg_rating": None, "review_count": 0}


def _serialize_restaurant(rest: dict, stats: dict) -> dict:
    return {
        "id": str(rest["_id"]),
        "name": rest.get("name"),
        "city": rest.get("city"),
        "state": rest.get("state"),
        "cuisine": rest.get("cuisine"),
        "price_range": rest.get("price_range"),
        "owner_id": rest.get("owner_id"),
        "created_at": rest.get("created_at", datetime.now(timezone.utc)).isoformat(),
        **stats,
    }


@app.get("/owner/restaurants")
def list_owned_restaurants(user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(403, "Only owners can access this endpoint")
    db = get_db()
    restaurants = list(db.restaurants.find({"owner_id": user["id"]}))
    return [_serialize_restaurant(r, _review_stats(db, str(r["_id"]))) for r in restaurants]


@app.post("/owner/restaurants/{restaurant_id}/claim", status_code=200)
def claim_restaurant(restaurant_id: str, user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(403, "Only owners can claim restaurants")
    db = get_db()
    try:
        rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    except Exception:
        raise HTTPException(400, "Invalid restaurant ID")
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    if rest.get("owner_id"):
        raise HTTPException(409, "Restaurant already claimed")
    db.restaurants.update_one(
        {"_id": ObjectId(restaurant_id)},
        {"$set": {"owner_id": user["id"]}},
    )
    publish_event("restaurant.claimed", {
        "action": "claimed",
        "restaurant_id": restaurant_id,
        "owner_id": user["id"],
    })
    return {"message": "Restaurant claimed successfully", "restaurant_id": restaurant_id}


@app.get("/owner/dashboard")
def owner_dashboard(user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(403, "Only owners can access this endpoint")
    db = get_db()
    restaurants = list(db.restaurants.find({"owner_id": user["id"]}))
    restaurant_list = [_serialize_restaurant(r, _review_stats(db, str(r["_id"]))) for r in restaurants]
    total_reviews = sum(r["review_count"] for r in restaurant_list)
    rated = [r["avg_rating"] for r in restaurant_list if r["avg_rating"] is not None]
    overall_avg = round(sum(rated) / len(rated), 2) if rated else None
    return {
        "owner_id": user["id"],
        "restaurant_count": len(restaurant_list),
        "total_reviews": total_reviews,
        "overall_avg_rating": overall_avg,
        "restaurants": restaurant_list,
    }


@app.get("/")
def health():
    return {"status": "ok", "service": "owner"}
