"""Seed MongoDB with sample restaurants from Milpitas and San Jose."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from shared.database import get_db
from shared.auth import hash_password
from datetime import datetime, timezone

db = get_db()

# Ensure seed user exists
seed_user = db.users.find_one({"email": "seed@yelp.com"})
if not seed_user:
    result = db.users.insert_one({
        "name": "Yelp Seed",
        "email": "seed@yelp.com",
        "hashed_password": hash_password("seedpassword123"),
        "role": "user",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    uid = str(result.inserted_id)
else:
    uid = str(seed_user["_id"])

restaurants = [
    ("GAO's Kabob & Crab", "mediterranean", "Milpitas", "CA", "$$", "casual", "Highly rated casual spot for kebabs and seafood."),
    ("Pho Mai", "other", "Milpitas", "CA", "$", "casual", "Top choice for Vietnamese pho and noodle soup."),
    ("Pho Saigon", "other", "Milpitas", "CA", "$", "casual", "Popular Vietnamese noodle soup restaurant."),
    ("Darda Seafood Restaurant", "chinese", "Milpitas", "CA", "$$", "casual", "Popular for Halal Chinese food and handmade noodles."),
    ("Dishdash Middle Eastern Grill", "mediterranean", "Milpitas", "CA", "$$", "casual", "Renowned for Mediterranean cuisine."),
    ("Chil Garden", "chinese", "Milpitas", "CA", "$$", "casual", "Known for authentic Chinese dishes."),
    ("El Torito", "mexican", "Milpitas", "CA", "$$", "family_friendly", "Reliable Mexican dining option."),
    ("Casa Azteca", "mexican", "Milpitas", "CA", "$$", "family_friendly", "Reliable Mexican dining option."),
    ("Chengdu Memory", "chinese", "Milpitas", "CA", "$$", "casual", "Authentic Sichuan Chinese cuisine."),
    ("Luna Mexican Kitchen", "mexican", "San Jose", "CA", "$$$", "fine_dining", "Michelin-recognized upscale Mexican food with popular, fresh tortillas."),
    ("Petiscos Portuguese Tapas", "mediterranean", "San Jose", "CA", "$$$", "fine_dining", "Upscale Portuguese tapas from the team behind the former Adega."),
    ("Zeni Ethiopian Restaurant", "other", "San Jose", "CA", "$$", "casual", "Highly recommended for Ethiopian cuisine."),
    ("Back A Yard Caribbean Grill", "other", "San Jose", "CA", "$$", "casual", "Well-regarded for authentic Caribbean food and plantains."),
    ("Good Karma Vegan Cafe", "american", "San Jose", "CA", "$", "casual", "Popular vegan spot in downtown San Jose."),
    ("Fogo de Chao", "other", "San Jose", "CA", "$$$$", "fine_dining", "High-end Brazilian steakhouse on Santana Row."),
    ("Left Bank Brasserie", "french", "San Jose", "CA", "$$$", "fine_dining", "French brasserie dining on Santana Row."),
    ("Kovai Cafe", "indian", "San Jose", "CA", "$", "casual", "Known for South Indian dosas and fried snacks."),
    ("SGD Tofu House", "other", "San Jose", "CA", "$", "casual", "Recommended for authentic Korean dumpling tofu soup."),
    ("Lanzhou Hand Pulled Noodles", "chinese", "San Jose", "CA", "$", "casual", "Famous for hand-pulled beef noodles."),
]

added = 0
for name, cuisine, city, state, price, ambiance, desc in restaurants:
    if not db.restaurants.find_one({"name": name, "city": city}):
        db.restaurants.insert_one({
            "name": name, "cuisine_type": cuisine, "city": city, "state": state,
            "price_range": price, "ambiance": ambiance, "description": desc,
            "created_by": uid,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        added += 1

# Create indexes
db.users.create_index("email", unique=True)
db.sessions.create_index("expires_at", expireAfterSeconds=0)
db.sessions.create_index("user_id")
db.reviews.create_index("restaurant_id")
db.reviews.create_index("user_id")
db.favourites.create_index([("user_id", 1), ("restaurant_id", 1)], unique=True)

print(f"Done! Added {added} restaurants ({len(restaurants) - added} already existed).")
print("MongoDB indexes created.")
