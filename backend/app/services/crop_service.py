import json
import pathlib
from app.schemas.crop import CropRequest, CropResponse

CROPS_PATH = pathlib.Path(__file__).parent.parent / "data" / "crops.json"

def rule_based_recommendations(data: CropRequest) -> list[CropResponse]:
    """
    Scores every crop against the request parameters using weighted rules.
    Used as fallback when model.pkl is not available.
    """
    crops = json.loads(CROPS_PATH.read_text(encoding="utf-8"))
    scored = []

    for crop in crops:
        score = _score_crop(crop, data)
        if score >= 40:
            scored.append(CropResponse(
                crop=crop["name"],
                confidence=round(score / 100, 4),
                suitability=round(score, 1),
            ))

    scored.sort(key=lambda x: x.suitability, reverse=True)
    return scored[:8]


def _score_crop(crop: dict, data: CropRequest) -> float:
    req = crop.get("requirements", {})
    score = 0.0

    # Temperature (30 pts)
    t_min = req.get("tempMin", 0)
    t_max = req.get("tempMax", 50)
    t_mid = (t_min + t_max) / 2
    t_range = max(t_max - t_min, 1)
    deviation = abs(data.temperature - t_mid) / (t_range / 2)
    score += max(0, 30 - deviation * 30)

    # Rainfall (25 pts)
    r_min = req.get("rainfallMin", 0)
    r_max = req.get("rainfallMax", 3000)
    if r_min <= data.rainfall <= r_max:
        score += 25
    elif data.rainfall < r_min:
        deficit = (r_min - data.rainfall) / max(r_min, 1)
        score += max(0, 25 - deficit * 50)
    else:
        excess = (data.rainfall - r_max) / max(r_max, 1)
        score += max(0, 25 - excess * 30)

    # Soil pH (20 pts)
    ph_min = req.get("phMin", 5.0)
    ph_max = req.get("phMax", 8.5)
    if ph_min <= data.ph <= ph_max:
        score += 20
    else:
        dev = min(abs(data.ph - ph_min), abs(data.ph - ph_max))
        score += max(0, 20 - dev * 8)

    # Humidity (15 pts)
    water = req.get("waterNeeds", "Medium")
    if water == "High" and data.humidity >= 70:
        score += 15
    elif water == "Low" and data.humidity <= 55:
        score += 15
    elif water == "Medium" and 50 <= data.humidity <= 75:
        score += 15
    else:
        score += 6

    # Season match (10 pts)
    if data.season:
        seasons = crop.get("season", [])
        if data.season in seasons or "Year-round" in seasons:
            score += 10

    return min(100.0, score)
