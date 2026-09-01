from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import uuid
import shutil

from .config import APP_NAME
from .db import get_database
from .models import Field, FieldCreate

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    description="TerraLens Farm Memory + Future Risk Prediction API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
def list_fields():
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    fields = list(db["fields"].find({}, {"_id": 0}))
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
def upload_field_photo(field_id: str, file: UploadFile = File(...)):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    field = db["fields"].find_one({"id": field_id})
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")

    ext = os.path.splitext(file.filename)[1]
    filename = f"{field_id}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    photo_url = f"http://127.0.0.1:8000/uploads/{filename}"
    db["fields"].update_one({"id": field_id}, {"$set": {"photo_url": photo_url}})

    return {"status": "uploaded", "photo_url": photo_url}