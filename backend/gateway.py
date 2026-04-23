import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from services.user_service.main import app as user_app
from services.restaurant_service.main import app as restaurant_app
from services.review_service.main import app as review_app
from services.favourites_service.main import app as favourites_app

gateway = FastAPI(title="Yelp API Gateway")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
gateway.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

gateway.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Mount each microservice
gateway.mount("/api/users", user_app)
gateway.mount("/api/reviews", review_app)
gateway.mount("/api/favourites", favourites_app)
gateway.mount("/api/restaurants", restaurant_app)


@gateway.get("/")
def health():
    return {"status": "ok", "service": "gateway"}
