from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


# ---------- Sub-models (nested data) ----------

class Location(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    village: Optional[str] = None
    district: Optional[str] = None


class ScanRecord(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None
    ai_analysis: Optional[str] = None


class FertilizerRecord(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    product: Optional[str] = None
    quantity: Optional[str] = None
    notes: Optional[str] = None


class IrrigationRecord(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    method: Optional[str] = None
    notes: Optional[str] = None


class WeatherSnapshot(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall_mm: Optional[float] = None
    notes: Optional[str] = None


class PreviousSeason(BaseModel):
    year: Optional[int] = None
    season: Optional[str] = None
    crop: Optional[str] = None
    yield_status: Optional[str] = None


class RiskEvent(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    risk_type: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    action_taken: Optional[str] = None


class FarmerObservation(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    text: Optional[str] = None
    source: Optional[str] = "voice"


# ---------- Main Field model ----------

class FieldCreate(BaseModel):
    """What the farmer fills in when creating a new field (simple form)."""
    name: str
    location: Location
    area: float
    crop: str
    season: str

    # Har device/farmer ko private rakhne ke liye — frontend se automatically bhejta hai
    user_id: Optional[str] = None

    soil_type: Optional[str] = None
    irrigation_method: Optional[str] = None
    sowing_date: Optional[datetime] = None


class Field(FieldCreate):
    """Full field document as stored in MongoDB."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    photo_url: Optional[str] = None

    crop_health: Optional[str] = "Unknown"
    risk_level: Optional[str] = "Unknown"

    farmer_observations: List[FarmerObservation] = []
    scans: List[ScanRecord] = []
    fertilizer_history: List[FertilizerRecord] = []
    irrigation_history: List[IrrigationRecord] = []
    weather_history: List[WeatherSnapshot] = []
    previous_seasons: List[PreviousSeason] = []
    risk_history: List[RiskEvent] = []
