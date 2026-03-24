"""Seed reviews for all restaurants from a specific user."""
import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import engine

REVIEWER_EMAIL = "harika.ganna1@gmail.com"

REVIEW_TEMPLATES = {
    5: [
        "Absolutely amazing! The food was outstanding and the service was top-notch.",
        "Best dining experience I've had in a while. Highly recommend!",
        "Incredible flavors and a wonderful atmosphere. Will definitely come back!",
    ],
    4: [
        "Really enjoyed the meal. Great food and friendly staff.",
        "Solid restaurant with delicious dishes. Would visit again.",
        "Very good experience overall. The menu has great variety.",
    ],
    3: [
        "Decent food and okay service. Nothing extraordinary but not bad either.",
        "Average experience. Some dishes were good, others were just okay.",
        "It was fine. Good for a casual meal but wouldn't go out of my way.",
    ],
}

with engine.connect() as conn:
    row = conn.execute(
        text("SELECT id FROM users WHERE email = :e"), {"e": REVIEWER_EMAIL}
    ).fetchone()
    if not row:
        print(f"ERROR: User '{REVIEWER_EMAIL}' not found.")
        sys.exit(1)
    uid = row[0]

    restaurants = conn.execute(text("SELECT id, name FROM restaurants")).fetchall()
    if not restaurants:
        print("No restaurants found in the database.")
        sys.exit(0)

    added = 0
    for rid, rname in restaurants:
        exists = conn.execute(
            text("SELECT id FROM reviews WHERE user_id = :u AND restaurant_id = :r"),
            {"u": uid, "r": rid},
        ).fetchone()
        if exists:
            continue
        rating = random.choice([3, 4, 4, 5, 5])
        comment = random.choice(REVIEW_TEMPLATES[rating])
        conn.execute(
            text(
                "INSERT INTO reviews (rating, comment, user_id, restaurant_id) "
                "VALUES (:rating, :comment, :uid, :rid)"
            ),
            {"rating": rating, "comment": comment, "uid": uid, "rid": rid},
        )
        added += 1

    conn.commit()

print(f"Done! Added {added} reviews for user '{REVIEWER_EMAIL}' ({len(restaurants) - added} already existed).")
