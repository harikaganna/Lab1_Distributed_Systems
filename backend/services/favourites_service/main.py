import os
import sys
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.database import get_db
from shared.auth import get_current_user

app = FastAPI(title="Favourites Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


@app.post("/favourites/{restaurant_id}", status_code=201)
def add_favourite(restaurant_id: str, user=Depends(get_current_user)):
    db = get_db()
    try:
        rest = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    except Exception:
        raise HTTPException(404, "Restaurant not found")
    if not rest:
        raise HTTPException(404, "Restaurant not found")
    existing = db.favourites.find_one({"user_id": user["id"], "restaurant_id": restaurant_id})
    if existing:
        raise HTTPException(409, "Already in favourites")
    fav = {
        "user_id": user["id"],
        "restaurant_id": restaurant_id,
        "created_at": datetime.now(timezone.utc),
    }
    result = db.favourites.insert_one(fav)
    return {
        "id": str(result.inserted_id),
        "restaurant_id": restaurant_id,
        "restaurant_name": rest.get("name"),
        "created_at": fav["created_at"].isoformat(),
    }


@app.get("/favourites")
def list_favourites(user=Depends(get_current_user)):
    db = get_db()
    favs = list(db.favourites.find({"user_id": user["id"]}))
    result = []
    for fav in favs:
        rest = db.restaurants.find_one({"_id": ObjectId(fav["restaurant_id"])}) if fav.get("restaurant_id") else None
        result.append({
            "id": str(fav["_id"]),
            "restaurant_id": fav["restaurant_id"],
            "restaurant_name": rest["name"] if rest else None,
            "created_at": fav.get("created_at", datetime.now(timezone.utc)).isoformat() if isinstance(fav.get("created_at"), datetime) else str(fav.get("created_at", "")),
        })
    return result


@app.delete("/favourites/{restaurant_id}", status_code=204)
def remove_favourite(restaurant_id: str, user=Depends(get_current_user)):
    db = get_db()
    result = db.favourites.delete_one({"user_id": user["id"], "restaurant_id": restaurant_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Favourite not found")


@app.get("/")
def health():
    return {"status": "ok", "service": "favourites"}
