from pymongo import MongoClient, ASCENDING, DESCENDING
from .config import MONGO_URL, MONGO_DB

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URL)
    return _client[MONGO_DB]


def init_indexes():
    """Create MongoDB indexes on first startup."""
    db = get_db()
    db.users.create_index([("email", ASCENDING)], unique=True, background=True)
    db.sessions.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, background=True)
    db.sessions.create_index([("user_id", ASCENDING)], background=True)
    db.reviews.create_index([("restaurant_id", ASCENDING)], background=True)
    db.reviews.create_index([("user_id", ASCENDING)], background=True)
    db.favourites.create_index([("user_id", ASCENDING), ("restaurant_id", ASCENDING)], unique=True, background=True)
    db.activity_logs.create_index([("timestamp", DESCENDING)], background=True)
    db.activity_logs.create_index([("entity_type", ASCENDING), ("entity_id", ASCENDING)], background=True)
