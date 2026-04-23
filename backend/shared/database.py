from pymongo import MongoClient
from .config import MONGO_URL, MONGO_DB

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URL)
    return _client[MONGO_DB]
