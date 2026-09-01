import certifi
from pymongo import MongoClient
from .config import MONGODB_URI, MONGODB_DATABASE


_client = None
_db = None

def get_database():
    global _client, _db

    if not MONGODB_URI:
        return None

    if _db is None:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
        _db = _client[MONGODB_DATABASE]

    return _db
