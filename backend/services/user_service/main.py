import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.database import get_db
from shared.auth import (
    hash_password, verify_password, create_access_token, get_current_user, oauth2_scheme,
)
from shared.config import ACCESS_TOKEN_EXPIRE_MINUTES
from shared.kafka_producer import publish_event

app = FastAPI(title="User Service")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


# --- Schemas ---
class UserSignup(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: str = "user"

class OwnerSignup(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    restaurant_location: str = Field(min_length=1, max_length=255)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    about_me: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    languages: Optional[str] = None
    gender: Optional[str] = None

class UserPreferenceUpdate(BaseModel):
    cuisine_preferences: Optional[str] = None
    price_range: Optional[str] = None
    preferred_location: Optional[str] = None
    search_radius: Optional[int] = None
    dietary_needs: Optional[str] = None
    ambiance_preferences: Optional[str] = None
    sort_preference: Optional[str] = None


def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role", "user"),
        "phone": user.get("phone"),
        "about_me": user.get("about_me"),
        "city": user.get("city"),
        "state": user.get("state"),
        "country": user.get("country"),
        "languages": user.get("languages"),
        "gender": user.get("gender"),
        "profile_picture": user.get("profile_picture"),
        "created_at": user.get("created_at", datetime.now(timezone.utc)).isoformat(),
    }


# --- Auth ---
@app.post("/auth/signup", status_code=201)
def signup(payload: UserSignup):
    db = get_db()
    if db.users.find_one({"email": payload.email}):
        raise HTTPException(409, "Email already registered")
    user = {
        "name": payload.name,
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "role": payload.role,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = db.users.insert_one(user)
    user["_id"] = result.inserted_id
    publish_event("user.created", {"action": "created", "user_id": str(result.inserted_id), "email": payload.email})
    return serialize_user(user)


@app.post("/auth/signup/owner", status_code=201)
def owner_signup(payload: OwnerSignup):
    db = get_db()
    if db.users.find_one({"email": payload.email}):
        raise HTTPException(409, "Email already registered")
    user = {
        "name": payload.name,
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "role": "owner",
        "restaurant_location": payload.restaurant_location,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = db.users.insert_one(user)
    user["_id"] = result.inserted_id
    publish_event("user.created", {"action": "created", "user_id": str(result.inserted_id), "email": payload.email, "role": "owner"})
    return serialize_user(user)


@app.post("/auth/login")
def login(payload: LoginRequest):
    db = get_db()
    user = db.users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(401, "Invalid email or password")
    user_id = str(user["_id"])
    token = create_access_token(user_id, user.get("role", "user"))
    # store session in MongoDB
    db.sessions.insert_one({
        "user_id": user_id,
        "token": token,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    })
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/logout", status_code=200)
def logout(token: str = Depends(oauth2_scheme)):
    db = get_db()
    db.sessions.delete_one({"token": token})
    return {"message": "Logged out successfully"}


# --- User Profile ---
@app.get("/users/me")
def get_profile(user=Depends(get_current_user)):
    return serialize_user(user)


@app.put("/users/me")
def update_profile(payload: UserUpdate, user=Depends(get_current_user)):
    db = get_db()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if updates:
        updates["updated_at"] = datetime.now(timezone.utc)
        db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": updates})
        publish_event("user.updated", {"action": "updated", "user_id": user["id"], "fields": list(updates.keys())})
    updated = db.users.find_one({"_id": ObjectId(user["id"])})
    return serialize_user(updated)


@app.post("/users/me/profile-picture")
async def upload_profile_picture(file: UploadFile = File(...), user=Depends(get_current_user)):
    db = get_db()
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": {"profile_picture": f"/uploads/{filename}"}})
    updated = db.users.find_one({"_id": ObjectId(user["id"])})
    return serialize_user(updated)


# --- Preferences ---
@app.get("/users/me/preferences")
def get_preferences(user=Depends(get_current_user)):
    db = get_db()
    pref = db.user_preferences.find_one({"user_id": user["id"]})
    if not pref:
        return {}
    pref.pop("_id", None)
    pref.pop("user_id", None)
    return pref


@app.put("/users/me/preferences")
def update_preferences(payload: UserPreferenceUpdate, user=Depends(get_current_user)):
    db = get_db()
    updates = payload.model_dump(exclude_unset=True)
    db.user_preferences.update_one(
        {"user_id": user["id"]},
        {"$set": updates},
        upsert=True,
    )
    pref = db.user_preferences.find_one({"user_id": user["id"]})
    pref.pop("_id", None)
    pref.pop("user_id", None)
    return pref


# --- History ---
@app.get("/users/me/history")
def get_history(user=Depends(get_current_user)):
    db = get_db()
    reviews = list(db.reviews.find({"user_id": user["id"]}).sort("created_at", -1))
    for r in reviews:
        r["id"] = str(r["_id"])
        r.pop("_id", None)
        u = db.users.find_one({"_id": ObjectId(r["user_id"])})
        r["user_name"] = u["name"] if u else "User"

    restaurants_added = list(db.restaurants.find({"created_by": user["id"]}).sort("created_at", -1))
    for rest in restaurants_added:
        rest["id"] = str(rest["_id"])
        rest.pop("_id", None)
        stats = _get_review_stats(db, rest["id"])
        rest.update(stats)

    return {"reviews": reviews, "restaurants_added": restaurants_added}


def _get_review_stats(db, restaurant_id):
    pipeline = [
        {"$match": {"restaurant_id": restaurant_id}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "review_count": {"$sum": 1}}},
    ]
    result = list(db.reviews.aggregate(pipeline))
    if result:
        return {"avg_rating": round(result[0]["avg_rating"], 2), "review_count": result[0]["review_count"]}
    return {"avg_rating": None, "review_count": 0}


@app.get("/")
def health():
    return {"status": "ok", "service": "user"}
