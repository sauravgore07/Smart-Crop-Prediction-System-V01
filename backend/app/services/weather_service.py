import httpx
import random

async def fetch_current_weather(lat: float, lng: float) -> dict:
    """
    Fetches live weather from Open-Meteo (free, no API key needed).
    Falls back to regional estimates if API is unreachable.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lng}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation"
        f"&timezone=auto"
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            current = data["current"]
            return {
                "temperature": current["temperature_2m"],
                "humidity": current["relative_humidity_2m"],
                "precipitation": current["precipitation"],
                "source": "Open-Meteo API",
                "lat": lat,
                "lng": lng,
            }
    except Exception:
        # Estimate based on latitude zone
        return _estimate_weather(lat, lng)


def _estimate_weather(lat: float, lng: float) -> dict:
    """Regional fallback when Open-Meteo is unreachable."""
    if lat > 28:
        temp = random.uniform(15, 30)
        humidity = random.uniform(40, 70)
    elif lat < 15:
        temp = random.uniform(24, 35)
        humidity = random.uniform(60, 90)
    else:
        temp = random.uniform(20, 35)
        humidity = random.uniform(50, 80)

    return {
        "temperature": round(temp, 1),
        "humidity": round(humidity, 1),
        "precipitation": round(random.uniform(0, 3), 2),
        "source": "Regional estimate (API unavailable)",
        "lat": lat,
        "lng": lng,
    }
