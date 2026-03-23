"""Seed the database with restaurants from Milpitas and San Jose."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base
from app.models import User
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

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

with engine.connect() as conn:
    # Ensure seed user exists
    row = conn.execute(text("SELECT id FROM users WHERE email = 'seed@yelp.com'")).fetchone()
    if row:
        uid = row[0]
    else:
        conn.execute(text(
            "INSERT INTO users (name, email, hashed_password, role) VALUES (:n, :e, :p, 'user')"
        ), {"n": "Yelp Seed", "e": "seed@yelp.com", "p": "$2b$12$seedhashplaceholdervalue000000000000000000000000000"})
        conn.commit()
        uid = conn.execute(text("SELECT id FROM users WHERE email = 'seed@yelp.com'")).fetchone()[0]

    added = 0
    for name, cuisine, city, state, price, ambiance, desc in restaurants:
        exists = conn.execute(text(
            "SELECT id FROM restaurants WHERE name = :n AND city = :c"
        ), {"n": name, "c": city}).fetchone()
        if not exists:
            conn.execute(text(
                "INSERT INTO restaurants (name, cuisine_type, city, state, price_range, ambiance, description, created_by) "
                "VALUES (:name, :cuisine, :city, :state, :price, :ambiance, :desc, :uid)"
            ), {"name": name, "cuisine": cuisine, "city": city, "state": state, "price": price, "ambiance": ambiance, "desc": desc, "uid": uid})
            added += 1

    conn.commit()

print(f"Done! Added {added} restaurants ({len(restaurants) - added} already existed).")
