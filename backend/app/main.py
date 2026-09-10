from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import os
import shutil
import uuid
import requests
import cloudinary
import cloudinary.uploader

from .config import APP_NAME
from .db import get_database
from .models import Field, FieldCreate

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    description="TerraLens Khet Diary API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cloudinary — permanent photo storage (Render ka local disk restart pe khaali ho jaata hai, isliye photos yahan rakhte hain)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {
        "name": "TerraLens",
        "message": "TerraLens API is running 🚀",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    db = get_database()

    if db is None:
        return {
            "status": "ok",
            "api": "online",
            "database": "not configured",
        }

    try:
        db.command("ping")
        database_status = "connected"
    except Exception as e:
        print("MONGO ERROR:", e)
        database_status = "unavailable"

    return {
        "status": "ok",
        "api": "online",
        "database": database_status,
    }


@app.post("/fields", response_model=Field)
def create_field(field_data: FieldCreate):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    new_field = Field(**field_data.dict())
    db["fields"].insert_one(new_field.dict())
    return new_field


@app.get("/fields", response_model=List[Field])
def list_fields(user_id: Optional[str] = None):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    query = {"user_id": user_id} if user_id else {}
    fields = list(db["fields"].find(query, {"_id": 0}))
    return fields


@app.get("/fields/{field_id}", response_model=Field)
def get_field(field_id: str):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    field = db["fields"].find_one({"id": field_id}, {"_id": 0})
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


@app.delete("/fields/{field_id}")
def delete_field(field_id: str):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    result = db["fields"].delete_one({"id": field_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Field not found")
    return {"status": "deleted", "id": field_id}


@app.post("/fields/{field_id}/photo")
def upload_field_photo(field_id: str, request: Request, file: UploadFile = File(...)):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    field = db["fields"].find_one({"id": field_id})
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")

    result = cloudinary.uploader.upload(file.file, folder="terralens/fields", public_id=field_id, overwrite=True)
    photo_url = result["secure_url"]

    db["fields"].update_one({"id": field_id}, {"$set": {"photo_url": photo_url}})

    return {"status": "uploaded", "photo_url": photo_url}


# ============================================================
#  Naya code — Khet ki Diary, Real Weather, User profile
# ============================================================

# ---------- Weather helper (Open-Meteo — free, no API key needed) ----------

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog", 51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 71: "Light snow", 73: "Snow",
    75: "Heavy snow", 80: "Rain showers", 81: "Rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def fetch_weather(latitude: float, longitude: float):
    """Real current weather from Open-Meteo. Returns (temp, description) or (None, None) on failure."""
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": latitude, "longitude": longitude, "current_weather": True},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json().get("current_weather", {})
        temp = data.get("temperature")
        code = data.get("weathercode")
        desc = WEATHER_CODES.get(code)
        return temp, desc
    except Exception as e:
        print("WEATHER ERROR:", e)
        return None, None


# ---------- Khet ki Diary (field updates) ----------

@app.get("/fields/{field_id}/updates")
def list_field_updates(field_id: str):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    updates = list(
        db["field_updates"].find({"field_id": field_id}, {"_id": 0}).sort("created_at", -1)
    )
    return updates


@app.post("/fields/{field_id}/updates")
def create_field_update(field_id: str, request: Request, file: UploadFile = File(...), note: Optional[str] = Form(None)):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    field = db["fields"].find_one({"id": field_id})
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")

    update_id = str(uuid.uuid4())
    result = cloudinary.uploader.upload(file.file, folder="terralens/diary", public_id=update_id, overwrite=True)
    photo_url = result["secure_url"]

    # Field's saved location se real weather uthao (Open-Meteo)
    weather_temp, weather_desc = None, None
    location = field.get("location") or {}
    lat, lon = location.get("latitude"), location.get("longitude")
    if lat is not None and lon is not None:
        weather_temp, weather_desc = fetch_weather(lat, lon)

    update_doc = {
        "id": update_id,
        "field_id": field_id,
        "user_id": field.get("user_id"),
        "photo_url": photo_url,
        "note": note,
        "weather_temp": weather_temp,
        "weather_desc": weather_desc,
        "created_at": datetime.utcnow().isoformat(),
    }
    db["field_updates"].insert_one(dict(update_doc))
    return update_doc


@app.get("/updates/recent")
def recent_updates(limit: int = 5, user_id: Optional[str] = None):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    query = {"user_id": user_id} if user_id else {}
    updates = list(
        db["field_updates"].find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    )
    for u in updates:
        field = db["fields"].find_one({"id": u.get("field_id")}, {"_id": 0, "name": 1})
        u["field_name"] = field["name"] if field else ""
    return updates


# ---------- User profile (naam + language) ----------

class UserProfile(BaseModel):
    name: str
    language: str
    user_id: Optional[str] = None


@app.get("/user")
def get_user(user_id: Optional[str] = None):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    key = user_id or "singleton"
    user = db["user"].find_one({"id": key}, {"_id": 0})
    if user is None:
        raise HTTPException(status_code=404, detail="No user saved yet")
    return user


@app.post("/user")
def save_user(user: UserProfile):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    key = user.user_id or "singleton"
    db["user"].update_one(
        {"id": key},
        {"$set": {"id": key, "name": user.name, "language": user.language}},
        upsert=True,
    )
    return {"name": user.name, "language": user.language}
