"""Seed MongoDB with sample restaurants, owners, reviewers, and reviews."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from shared.database import get_db
from shared.auth import hash_password
from datetime import datetime, timezone

db = get_db()

def upsert_user(name, email, role):
    u = db.users.find_one({"email": email})
    if not u:
        result = db.users.insert_one({
            "name": name, "email": email,
            "hashed_password": hash_password("password123"),
            "role": role,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        return str(result.inserted_id)
    return str(u["_id"])

# --- Owners ---
owners = [
    ("Marco Rossi",     "marco@owner.com"),
    ("Linda Chen",      "linda@owner.com"),
    ("Carlos Vega",     "carlos@owner.com"),
    ("Priya Sharma",    "priya@owner.com"),
    ("James Nguyen",    "james@owner.com"),
]
owner_ids = [upsert_user(name, email, "owner") for name, email in owners]

# --- Reviewers ---
reviewers = [
    ("Alice Kim",       "alice@dev.com"),
    ("Bob Patel",       "bob@dev.com"),
    ("Carol Torres",    "carol@dev.com"),
    ("David Lee",       "david@dev.com"),
    ("Emma Wilson",     "emma@dev.com"),
    ("Frank Okafor",    "frank@dev.com"),
    ("Grace Liu",       "grace@dev.com"),
    ("Henry Morales",   "henry@dev.com"),
]
reviewer_ids = [upsert_user(name, email, "user") for name, email in reviewers]

# --- Restaurants (name, cuisine, city, state, price, ambiance, desc, amenities, owner_idx) ---
restaurants = [
    # Milpitas
    ("GAO's Kabob & Crab",          "mediterranean", "Milpitas", "CA", "$$",   "casual",          "Highly rated casual spot for kebabs and fresh seafood.",                              "wifi, outdoor seating, takeout, parking",                     0),
    ("Pho Mai",                     "other",         "Milpitas", "CA", "$",    "casual",          "Top choice for Vietnamese pho with a rich, slow-cooked broth.",                      "takeout, delivery, parking",                                  1),
    ("Pho Saigon",                  "other",         "Milpitas", "CA", "$",    "casual",          "Popular Vietnamese noodle soup with generous toppings.",                             "takeout, parking",                                            1),
    ("Darda Seafood Restaurant",    "chinese",       "Milpitas", "CA", "$$",   "casual",          "Popular for Halal Chinese food and handmade noodles.",                               "halal, parking, takeout",                                     2),
    ("Dishdash Middle Eastern Grill","mediterranean","Milpitas", "CA", "$$",   "casual",          "Renowned for fresh Mediterranean cuisine and warm hospitality.",                     "wifi, outdoor seating, takeout, parking",                     0),
    ("Chil Garden",                 "chinese",       "Milpitas", "CA", "$$",   "casual",          "Known for authentic Chinese dishes and a cozy atmosphere.",                          "wifi, hot pot, parking",                                      2),
    ("El Torito",                   "mexican",       "Milpitas", "CA", "$$",   "family_friendly", "Classic Tex-Mex with generous portions and festive vibes.",                          "full bar, outdoor seating, parking, happy hour",              3),
    ("Casa Azteca",                 "mexican",       "Milpitas", "CA", "$$",   "family_friendly", "Family-run Mexican kitchen with homemade salsas and tortillas.",                    "family friendly, takeout, parking",                           3),
    ("Chengdu Memory",              "chinese",       "Milpitas", "CA", "$$",   "casual",          "Authentic Sichuan cuisine with bold flavors and numbing heat.",                      "wifi, takeout, spicy, parking",                               2),
    ("Sakura Sushi Bar",            "japanese",      "Milpitas", "CA", "$$$",  "casual",          "Fresh nigiri and creative rolls in a clean, modern setting.",                        "wifi, sake bar, reservations, parking",                       4),
    ("Spice Route Indian Kitchen",  "indian",        "Milpitas", "CA", "$$",   "casual",          "Rich curries and tandoor dishes inspired by Northern India.",                        "halal, lunch buffet, takeout, parking",                       3),
    ("Thai Basil",                  "thai",          "Milpitas", "CA", "$$",   "casual",          "Fragrant pad thai, green curry, and fresh spring rolls.",                            "wifi, outdoor seating, takeout, parking",                     4),
    # San Jose
    ("Luna Mexican Kitchen",        "mexican",       "San Jose",  "CA", "$$$", "fine_dining",     "Michelin-recognized upscale Mexican food with fresh tortillas.",                     "full bar, reservations, valet parking, romantic",             3),
    ("Petiscos Portuguese Tapas",   "mediterranean", "San Jose",  "CA", "$$$", "fine_dining",     "Upscale Portuguese tapas from the team behind the former Adega.",                    "wine bar, reservations, outdoor seating, parking",            0),
    ("Zeni Ethiopian Restaurant",   "other",         "San Jose",  "CA", "$$",  "casual",          "Highly recommended for injera, rich stews, and communal dining.",                   "vegetarian friendly, takeout, parking",                       1),
    ("Back A Yard Caribbean Grill", "other",         "San Jose",  "CA", "$$",  "casual",          "Authentic Caribbean food with jerk chicken and fried plantains.",                    "outdoor seating, takeout, parking",                           1),
    ("Good Karma Vegan Cafe",       "american",      "San Jose",  "CA", "$",   "casual",          "Popular vegan spot in downtown San Jose with creative bowls.",                       "wifi, vegan, vegetarian, outdoor seating, bike parking",      4),
    ("Fogo de Chao",                "other",         "San Jose",  "CA", "$$$$","fine_dining",     "High-end Brazilian churrasco steakhouse on Santana Row.",                            "full bar, valet parking, reservations, private dining",       0),
    ("Left Bank Brasserie",         "french",        "San Jose",  "CA", "$$$", "fine_dining",     "Classic French brasserie with duck confit and a stellar wine list.",                 "wine bar, outdoor seating, reservations, parking, romantic",  0),
    ("Kovai Cafe",                  "indian",        "San Jose",  "CA", "$",   "casual",          "Known for South Indian dosas, idlis, and freshly ground chutneys.",                  "vegetarian, takeout, parking",                                3),
    ("SGD Tofu House",              "other",         "San Jose",  "CA", "$",   "casual",          "Authentic Korean soon tofu stew and handmade dumplings.",                            "takeout, parking",                                            2),
    ("Lanzhou Hand Pulled Noodles", "chinese",       "San Jose",  "CA", "$",   "casual",          "Famous for hand-pulled beef noodles made fresh to order.",                           "takeout, parking",                                            2),
    ("Adega",                       "mediterranean", "San Jose",  "CA", "$$$$","romantic",        "Two Michelin-starred Portuguese fine dining, exceptional tasting menu.",              "wine cellar, valet parking, reservations required, romantic", 0),
    ("Olla Cocina",                 "mexican",       "San Jose",  "CA", "$$",  "casual",          "Modern Mexican street food with creative tacos and mezcal cocktails.",               "full bar, outdoor seating, happy hour, parking",              3),
    ("Smoking Pig BBQ",             "american",      "San Jose",  "CA", "$$",  "casual",          "Award-winning BBQ joint with slow-smoked brisket and ribs.",                         "outdoor seating, takeout, parking, catering",                 4),
    ("Kazoo Sushi",                 "japanese",      "San Jose",  "CA", "$$",  "casual",          "Neighborhood sushi spot with reliable rolls and daily specials.",                    "wifi, sake bar, happy hour, parking",                         4),
]

added = 0
updated_amenities = 0
rest_ids = {}
for name, cuisine, city, state, price, ambiance, desc, amenities, owner_idx in restaurants:
    existing = db.restaurants.find_one({"name": name, "city": city})
    if existing:
        rest_ids[name] = str(existing["_id"])
        if not existing.get("amenities"):
            db.restaurants.update_one(
                {"_id": existing["_id"]},
                {"$set": {"amenities": amenities, "updated_at": datetime.now(timezone.utc)}}
            )
            updated_amenities += 1
    else:
        result = db.restaurants.insert_one({
            "name": name, "cuisine_type": cuisine, "city": city, "state": state,
            "price_range": price, "ambiance": ambiance, "description": desc,
            "amenities": amenities,
            "created_by": owner_ids[owner_idx],
            "owner_id": owner_ids[owner_idx],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        rest_ids[name] = str(result.inserted_id)
        added += 1

print(f"Added {added} restaurants ({len(restaurants) - added} already existed, {updated_amenities} updated with amenities).")

# --- Reviews (restaurant name, reviewer index, rating, comment) ---
review_data = [
    ("GAO's Kabob & Crab",          0, 5, "The lamb kebabs were incredible, perfectly charred and seasoned."),
    ("GAO's Kabob & Crab",          1, 4, "Great food and lively atmosphere. The crab was fresh."),
    ("GAO's Kabob & Crab",          2, 5, "Best kebabs I've had outside of the Middle East."),
    ("GAO's Kabob & Crab",          3, 3, "Good but service was slow on a busy Friday night."),

    ("Pho Mai",                     0, 5, "Best pho in the South Bay, hands down. The broth is unreal."),
    ("Pho Mai",                     4, 4, "Rich broth and generous portions, great value for the price."),
    ("Pho Mai",                     5, 5, "I come here every week. Perfectly consistent every time."),

    ("Pho Saigon",                  1, 4, "Solid pho with great toppings. The brisket was tender."),
    ("Pho Saigon",                  6, 3, "Good but Pho Mai down the street is better."),

    ("Darda Seafood Restaurant",    2, 5, "Incredible handmade noodles, the most authentic flavors."),
    ("Darda Seafood Restaurant",    3, 4, "Halal Chinese done right. The fish dishes were excellent."),
    ("Darda Seafood Restaurant",    7, 5, "The lamb noodle soup is a must-order every single time."),

    ("Dishdash Middle Eastern Grill", 0, 4, "Freshest falafel I have found in the Bay Area."),
    ("Dishdash Middle Eastern Grill", 5, 5, "The hummus and shawarma plate is absolutely perfect."),
    ("Dishdash Middle Eastern Grill", 6, 4, "Great spot for a casual Mediterranean dinner."),

    ("Chil Garden",                 1, 4, "Dependable Chinese food, love the hot pot options."),
    ("Chil Garden",                 7, 3, "Decent food but nothing that stands out from the crowd."),

    ("El Torito",                   2, 4, "Great margaritas and solid enchiladas. Fun for groups."),
    ("El Torito",                   3, 3, "Classic Tex-Mex, nothing fancy but always reliable."),

    ("Casa Azteca",                 4, 5, "The homemade salsas are incredible, best chips in Milpitas."),
    ("Casa Azteca",                 0, 4, "Friendly family vibe and delicious carnitas tacos."),
    ("Casa Azteca",                 6, 5, "Hidden gem. The mole sauce is extraordinary."),

    ("Chengdu Memory",              1, 5, "Legit Sichuan heat. The mapo tofu was absolutely outstanding."),
    ("Chengdu Memory",              5, 4, "Authentic flavors and the dan dan noodles are addictive."),
    ("Chengdu Memory",              7, 5, "Finally real Chengdu food in the Bay. The cumin lamb is fire."),

    ("Sakura Sushi Bar",            2, 5, "Super fresh fish. The omakase is worth every penny."),
    ("Sakura Sushi Bar",            3, 4, "Clean and modern, great date night spot."),
    ("Sakura Sushi Bar",            6, 4, "The spicy tuna roll and miso soup combo never disappoints."),

    ("Spice Route Indian Kitchen",  0, 5, "The butter chicken here is rich, creamy, and authentic."),
    ("Spice Route Indian Kitchen",  4, 4, "Great lunch buffet with a wide variety of curries."),
    ("Spice Route Indian Kitchen",  7, 5, "The biryani is fragrant and perfectly spiced, best in Milpitas."),

    ("Thai Basil",                  1, 4, "The green curry is perfectly balanced, not too sweet."),
    ("Thai Basil",                  5, 5, "Best pad see ew I have had, the noodles have great wok char."),
    ("Thai Basil",                  6, 4, "Solid neighborhood Thai, the mango sticky rice is divine."),

    ("Luna Mexican Kitchen",        0, 5, "Michelin-worthy tacos and the freshest handmade tortillas."),
    ("Luna Mexican Kitchen",        2, 4, "Upscale Mexican that actually delivers on the hype."),
    ("Luna Mexican Kitchen",        4, 5, "The tableside guacamole and mezcal cocktails are spectacular."),
    ("Luna Mexican Kitchen",        7, 4, "Beautiful presentation and complex flavors throughout."),

    ("Petiscos Portuguese Tapas",   1, 5, "The bacalhau fritters and port wine pairing were sublime."),
    ("Petiscos Portuguese Tapas",   3, 4, "Elegant tapas and a fantastic curated wine list."),
    ("Petiscos Portuguese Tapas",   5, 5, "A gem of a restaurant, every dish was thoughtfully crafted."),

    ("Zeni Ethiopian Restaurant",   2, 5, "Incredible injera with rich, complex stews. Go hungry."),
    ("Zeni Ethiopian Restaurant",   6, 4, "A wonderful communal dining experience, very authentic."),
    ("Zeni Ethiopian Restaurant",   7, 5, "The lamb tibs and lentil dishes are absolutely outstanding."),

    ("Back A Yard Caribbean Grill", 0, 4, "Jerk chicken is smoky and flavorful, great with rice and peas."),
    ("Back A Yard Caribbean Grill", 3, 5, "The oxtail stew is slow-cooked to perfection. Highly recommend."),
    ("Back A Yard Caribbean Grill", 4, 4, "Authentic Caribbean soul food, the plantains are amazing."),

    ("Good Karma Vegan Cafe",       1, 4, "Surprisingly filling vegan options that even meat-eaters enjoy."),
    ("Good Karma Vegan Cafe",       5, 5, "The acai bowl and avocado toast are both incredible."),
    ("Good Karma Vegan Cafe",       7, 4, "Great smoothies and a warm, welcoming atmosphere downtown."),

    ("Fogo de Chao",                2, 5, "The churrasco experience here is absolutely unmatched."),
    ("Fogo de Chao",                4, 4, "Pricey but worth every bite for a truly special occasion."),
    ("Fogo de Chao",                6, 5, "The picanha and lamb chops were cooked to absolute perfection."),
    ("Fogo de Chao",                0, 3, "Food is great but felt very rushed by the servers."),

    ("Left Bank Brasserie",         1, 5, "Duck confit was perfect and the wine list is exceptional."),
    ("Left Bank Brasserie",         3, 4, "Classic French bistro atmosphere, very romantic for a date."),
    ("Left Bank Brasserie",         7, 5, "The steak frites and crème brûlée were both flawless."),
    ("Left Bank Brasserie",         5, 4, "Excellent French onion soup. Feels like Paris on Santana Row."),

    ("Kovai Cafe",                  0, 5, "The masala dosa here rivals anything I have had in Chennai."),
    ("Kovai Cafe",                  2, 4, "Authentic South Indian flavors at a genuinely great price."),
    ("Kovai Cafe",                  4, 5, "The filter coffee and idli sambar combo is a perfect breakfast."),
    ("Kovai Cafe",                  6, 4, "Freshly ground chutneys make all the difference here."),

    ("SGD Tofu House",              1, 5, "The spicy soon tofu is deeply comforting and very authentic."),
    ("SGD Tofu House",              3, 4, "Handmade dumplings are excellent, the broth is outstanding."),
    ("SGD Tofu House",              5, 4, "Great Korean comfort food at a very fair price point."),

    ("Lanzhou Hand Pulled Noodles", 0, 5, "Watching them pull noodles fresh is half the fun of dining here."),
    ("Lanzhou Hand Pulled Noodles", 2, 4, "The beef broth is clear but incredibly flavorful and rich."),
    ("Lanzhou Hand Pulled Noodles", 7, 5, "The best hand-pulled noodles outside of Lanzhou itself."),

    ("Adega",                       1, 5, "A two Michelin star experience that exceeded every expectation."),
    ("Adega",                       4, 5, "The tasting menu is a stunning journey through Portuguese cuisine."),
    ("Adega",                       6, 4, "Exceptional food and service, a true special occasion restaurant."),

    ("Olla Cocina",                 0, 4, "Creative tacos and excellent mezcal selection, very trendy spot."),
    ("Olla Cocina",                 3, 5, "The birria tacos with consommé are absolutely life-changing."),
    ("Olla Cocina",                 5, 4, "Modern Mexican done right, love the atmosphere on weekends."),

    ("Smoking Pig BBQ",             2, 5, "The brisket is perfectly smoked and just melts in your mouth."),
    ("Smoking Pig BBQ",             4, 5, "Best BBQ in San Jose, the ribs and burnt ends are incredible."),
    ("Smoking Pig BBQ",             7, 4, "Authentic Texas-style BBQ, the pulled pork sandwich is massive."),
    ("Smoking Pig BBQ",             1, 4, "Lines can be long but totally worth the wait every single time."),

    ("Kazoo Sushi",                 3, 4, "Reliable neighborhood sushi, the daily specials are always fresh."),
    ("Kazoo Sushi",                 6, 5, "The chef's special roll changes weekly and is always creative."),
    ("Kazoo Sushi",                 0, 4, "Great value for the quality. A solid go-to for sushi night."),
]

added_reviews = 0
for rest_name, user_idx, rating, comment in review_data:
    rid = rest_ids.get(rest_name)
    if not rid:
        continue
    uid = reviewer_ids[user_idx]
    if not db.reviews.find_one({"restaurant_id": rid, "user_id": uid}):
        db.reviews.insert_one({
            "restaurant_id": rid, "user_id": uid,
            "rating": rating, "comment": comment,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        added_reviews += 1

print(f"Added {added_reviews} reviews.")

# --- Indexes ---
db.users.create_index("email", unique=True)
db.sessions.create_index("expires_at", expireAfterSeconds=0)
db.sessions.create_index("user_id")
db.reviews.create_index("restaurant_id")
db.reviews.create_index("user_id")
db.favourites.create_index([("user_id", 1), ("restaurant_id", 1)], unique=True)

print("MongoDB indexes created.")
print("\nOwner accounts (password: password123):")
for name, email in owners:
    print(f"  {email}")
print("\nReviewer accounts (password: password123):")
for name, email in reviewers:
    print(f"  {email}")
