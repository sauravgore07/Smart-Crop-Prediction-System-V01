from fastapi import APIRouter, HTTPException
from app.services.weather_service import fetch_current_weather
from app.services.nasa_service import fetch_nasa_climate

router = APIRouter()

@router.get("")
async def get_weather(lat: float, lng: float):
    """Current temperature, humidity, precipitation from Open-Meteo."""
    try:
        return await fetch_current_weather(lat, lng)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {str(e)}")

@router.get("/nasa")
async def get_nasa(lat: float, lng: float):
    """30-year historical rainfall from NASA POWER API."""
    try:
        return await fetch_nasa_climate(lat, lng)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"NASA API error: {str(e)}")
