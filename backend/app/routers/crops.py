from fastapi import APIRouter
from app.schemas.crop import CropRequest, CropResponse
from app.ml.predictor import predict_crops
from app.services.crop_service import rule_based_recommendations
from typing import List
import json, pathlib

router = APIRouter()

@router.post("/recommend", response_model=List[CropResponse])
def recommend(body: CropRequest):
    """
    Returns top crop recommendations.
    Uses ML model if model.pkl exists, falls back to rule-based scoring.
    """
    try:
        return predict_crops(body)
    except FileNotFoundError:
        # model not trained yet — use rule-based
        return rule_based_recommendations(body)
    except Exception as e:
        print(f"ML prediction failed: {e}, using rule-based fallback")
        return rule_based_recommendations(body)

@router.get("/all")
def get_all_crops():
    """Returns the full crop database (22 crops)."""
    crops_path = pathlib.Path(__file__).parent.parent / "data" / "crops.json"
    return json.loads(crops_path.read_text(encoding="utf-8"))

