import os
import sys
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.database import get_db
from shared.auth import get_current_user
from shared.kafka_producer import publish_event
from shared.activity_logger import log_activity

app = FastAPI(title="Review Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    photos: Optional[str] = None

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None
    photos: Optional[str] = None


def serialize_review(db, review):
    review["id"] = str(review["_id"])
    review.pop("_id", None)
    user = db.users.find_one({"_id": ObjectId(review["user_id"])}) if review.get("user_id") else None
    review["user_name"] = user["name"] if user else "User"
    for field in ["created_at", "updated_at"]:
        if isinstance(review.get(field), datetime):
            review[field] = review[field].isoformat()
        elif not review.get(field):
            review[field] = datetime.now(timezone.utc).isoformat()
    return review


# Producer: publishes to Kafka, returns pending status
@app.post("/restaurants/{restaurant_id}/reviews", status_code=201)
def create_review(restaurant_id: str, payload: ReviewCreate, user=Depends(get_current_user)):
    db = get_db()
    try:
        rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    except Exception:
        raise HTTPException(404, "Restaurant not found")
    if not rest:
        raise HTTPException(404, "Restaurant not found")

    review_data = {
        "rating": payload.rating,
        "comment": payload.comment,
        "photos": payload.photos,
        "user_id": user["id"],
        "restaurant_id": restaurant_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "status": "pending",
    }
    result = db.reviews.insert_one(review_data)
    review_data["_id"] = result.inserted_id

    # Publish to Kafka for async processing
    publish_event("review.created", {
        "action": "created",
        "review_id": str(result.inserted_id),
        "restaurant_id": restaurant_id,
        "user_id": user["id"],
        "rating": payload.rating,
        "comment": payload.comment,
    })
    log_activity("review_created", "review", str(result.inserted_id), user["id"],
                 {"restaurant_id": restaurant_id, "rating": payload.rating})

    return serialize_review(db, review_data)


@app.get("/restaurants/{restaurant_id}/reviews")
def list_reviews(restaurant_id: str):
    db = get_db()
    reviews = list(db.reviews.find({"restaurant_id": restaurant_id}).sort("created_at", -1))
    return [serialize_review(db, r) for r in reviews]


@app.put("/restaurants/{restaurant_id}/reviews/{review_id}")
def update_review(restaurant_id: str, review_id: str, payload: ReviewUpdate, user=Depends(get_current_user)):
    db = get_db()
    review = db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(404, "Review not found")
    if review["user_id"] != user["id"]:
        raise HTTPException(403, "Can only edit your own reviews")

    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if updates:
        updates["updated_at"] = datetime.now(timezone.utc)
        db.reviews.update_one({"_id": ObjectId(review_id)}, {"$set": updates})
        publish_event("review.updated", {
            "action": "updated", "review_id": review_id,
            "restaurant_id": restaurant_id, "user_id": user["id"],
            "updates": {k: v for k, v in updates.items() if k != "updated_at"},
        })

    updated = db.reviews.find_one({"_id": ObjectId(review_id)})
    return serialize_review(db, updated)


@app.delete("/restaurants/{restaurant_id}/reviews/{review_id}", status_code=204)
def delete_review(restaurant_id: str, review_id: str, user=Depends(get_current_user)):
    db = get_db()
    review = db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(404, "Review not found")
    if review["user_id"] != user["id"]:
        raise HTTPException(403, "Can only delete your own reviews")
    db.reviews.delete_one({"_id": ObjectId(review_id)})
    publish_event("review.deleted", {
        "action": "deleted", "review_id": review_id,
        "restaurant_id": restaurant_id, "user_id": user["id"],
    })


@app.get("/")
def health():
    return {"status": "ok", "service": "review"}
