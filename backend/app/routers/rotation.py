
from fastapi import APIRouter

from app.ml.rotation_engine import (
    get_next_season_rotation
)

router = APIRouter()

# =====================================================
# NEXT SEASON ROTATION API
# =====================================================

@router.post("/next-season")

def next_season_rotation(data: dict):

    result = get_next_season_rotation(

        latitude=data["latitude"],

        longitude=data["longitude"],

        current_season=data["currentSeason"],

        previous_crop=data["previousCrop"],
    )

    return result

