from pydantic import BaseModel
from typing import List, Any, Optional
from datetime import datetime

class FarmCreate(BaseModel):
    name: str
    lat: float
    lng: float
    location_name: str = ""
    soil_type: str = "Loamy"
    soil_ph: float = 6.5
    land_area: float = 2.0
    season: str = "Kharif"
    saved_crops: List[Any] = []

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None
    land_area: Optional[float] = None
    season: Optional[str] = None
    saved_crops: Optional[List[Any]] = None

class FarmOut(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    location_name: str
    soil_type: str
    soil_ph: float
    land_area: float
    season: str
    saved_crops: List[Any]
    created_at: datetime

    class Config:
        from_attributes = True
