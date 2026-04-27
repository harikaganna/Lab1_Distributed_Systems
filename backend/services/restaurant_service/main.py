import os
import sys
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.database import get_db
from shared.auth import get_current_user
from shared.kafka_producer import publish_event

app = FastAPI(title="Restaurant Service")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


# --- Schemas ---
class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    cuisine_type: str
    city: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    price_range: Optional[str] = None
    ambiance: Optional[str] = None
    hours: Optional[str] = None
    photos: Optional[str] = None
    amenities: Optional[str] = None

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    cuisine_type: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    price_range: Optional[str] = None
    ambiance: Optional[str] = None
    hours: Optional[str] = None
    photos: Optional[str] = None
    amenities: Optional[str] = None

class PhotoDeleteRequest(BaseModel):
    photo_url: str


def serialize_restaurant(db, rest):
    rest["id"] = str(rest["_id"])
    rest.pop("_id", None)
    stats = _get_review_stats(db, rest["id"])
    rest.update(stats)
    rest.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    if isinstance(rest.get("created_at"), datetime):
        rest["created_at"] = rest["created_at"].isoformat()
    return rest


def _get_review_stats(db, restaurant_id):
    pipeline = [
        {"$match": {"restaurant_id": restaurant_id}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "review_count": {"$sum": 1}}},
    ]
    result = list(db.reviews.aggregate(pipeline))
    if result:
        return {"avg_rating": round(result[0]["avg_rating"], 2), "review_count": result[0]["review_count"]}
    return {"avg_rating": None, "review_count": 0}


@app.post("/restaurants", status_code=201)
def create_restaurant(payload: RestaurantCreate, user=Depends(get_current_user)):
    db = get_db()
    data = payload.model_dump(exclude_unset=True)
    data["created_by"] = user["id"]
    data["created_at"] = datetime.now(timezone.utc)
    data["updated_at"] = datetime.now(timezone.utc)
    result = db.restaurants.insert_one(data)
    data["_id"] = result.inserted_id
    publish_event("restaurant.created", {
        "action": "created", "restaurant_id": str(result.inserted_id),
        "name": data["name"], "user_id": user["id"],
    })
    return serialize_restaurant(db, data)


@app.get("/restaurants")
def search_restaurants(
    skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200),
    name: str = Query(None), cuisine: str = Query(None),
    city: str = Query(None), keyword: str = Query(None),
):
    db = get_db()
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if cuisine:
        query["cuisine_type"] = cuisine
    if city:
        query["$or"] = [
            {"city": {"$regex": city, "$options": "i"}},
            {"zip_code": {"$regex": city, "$options": "i"}},
        ]
    if keyword:
        kw_regex = {"$regex": keyword, "$options": "i"}
        keyword_or = [
            {"name": kw_regex}, {"description": kw_regex},
            {"amenities": kw_regex}, {"cuisine_type": kw_regex}, {"ambiance": kw_regex},
        ]
        if "$or" in query:
            query["$and"] = [{"$or": query.pop("$or")}, {"$or": keyword_or}]
        else:
            query["$or"] = keyword_or

    restaurants = list(db.restaurants.find(query).skip(skip).limit(limit))
    return [serialize_restaurant(db, r) for r in restaurants]


@app.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: str):
    db = get_db()
    try:
        rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    except Exception:
        raise HTTPException(404, "Restaurant not found")
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    return serialize_restaurant(db, rest)


@app.put("/restaurants/{restaurant_id}")
def update_restaurant(restaurant_id: str, payload: RestaurantUpdate, user=Depends(get_current_user)):
    db = get_db()
    rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    if rest.get("owner_id") != user["id"] and rest.get("created_by") != user["id"]:
        raise HTTPException(403, "Not authorized to update this restaurant")
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if updates:
        updates["updated_at"] = datetime.now(timezone.utc)
        db.restaurants.update_one({"_id": ObjectId(restaurant_id)}, {"$set": updates})
        publish_event("restaurant.updated", {
            "action": "updated", "restaurant_id": restaurant_id, "user_id": user["id"],
            "fields": list(updates.keys()),
        })
    updated = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    return serialize_restaurant(db, updated)


@app.post("/restaurants/{restaurant_id}/claim")
def claim_restaurant(restaurant_id: str, user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(403, "Only owners can claim restaurants")
    db = get_db()
    rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    if rest.get("owner_id"):
        raise HTTPException(409, "Restaurant already claimed")
    db.restaurants.update_one({"_id": ObjectId(restaurant_id)}, {"$set": {"owner_id": user["id"]}})
    publish_event("restaurant.claimed", {
        "action": "claimed", "restaurant_id": restaurant_id, "owner_id": user["id"],
    })
    updated = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    return serialize_restaurant(db, updated)


@app.post("/restaurants/{restaurant_id}/photos")
async def upload_restaurant_photo(restaurant_id: str, file: UploadFile = File(...), user=Depends(get_current_user)):
    db = get_db()
    rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"rest_{restaurant_id[:8]}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    photo_url = f"/uploads/{filename}"
    existing = rest.get("photos", "")
    new_photos = f"{existing},{photo_url}" if existing else photo_url
    db.restaurants.update_one({"_id": ObjectId(restaurant_id)}, {"$set": {"photos": new_photos}})
    updated = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    return serialize_restaurant(db, updated)


@app.post("/restaurants/{restaurant_id}/cover")
async def upload_cover_image(restaurant_id: str, file: UploadFile = File(...), user=Depends(get_current_user)):
    db = get_db()
    rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    if rest.get("owner_id") != user["id"] and rest.get("created_by") != user["id"]:
        raise HTTPException(403, "Only the restaurant owner can set the cover image")
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"cover_{restaurant_id[:8]}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    old_cover = rest.get("cover_image")
    if old_cover:
        old_path = os.path.join(UPLOAD_DIR, os.path.basename(old_cover))
        if os.path.exists(old_path):
            os.remove(old_path)
    db.restaurants.update_one({"_id": ObjectId(restaurant_id)}, {"$set": {"cover_image": f"/uploads/{filename}"}})
    updated = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    return serialize_restaurant(db, updated)


@app.delete("/restaurants/{restaurant_id}/photos")
def delete_restaurant_photo(restaurant_id: str, payload: PhotoDeleteRequest, user=Depends(get_current_user)):
    db = get_db()
    rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    if not user:
        raise HTTPException(403, "Must be logged in to delete photos")
    existing = [p.strip() for p in (rest.get("photos") or "").split(",") if p.strip()]
    if payload.photo_url not in existing:
        raise HTTPException(404, "Photo not found")
    existing.remove(payload.photo_url)
    db.restaurants.update_one({"_id": ObjectId(restaurant_id)}, {"$set": {"photos": ",".join(existing)}})
    filename = os.path.basename(payload.photo_url)
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    updated = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    return serialize_restaurant(db, updated)


@app.delete("/restaurants/{restaurant_id}", status_code=204)
def delete_restaurant(restaurant_id: str, user=Depends(get_current_user)):
    db = get_db()
    rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    if rest.get("owner_id") != user["id"] and rest.get("created_by") != user["id"]:
        raise HTTPException(403, "Not authorized to delete this restaurant")
    db.restaurants.delete_one({"_id": ObjectId(restaurant_id)})


@app.get("/")
def health():
    return {"status": "ok", "service": "restaurant"}
