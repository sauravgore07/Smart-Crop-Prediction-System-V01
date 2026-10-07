
# =========================================================
# NEXT SEASON ROTATION ENGINE
# =========================================================
#
# FLOW:
#
# Find nearest district
# ↓
# Get next season
# ↓
# Fetch next-season crops from CSV
# ↓
# Apply rotation filtering
# ↓
# Return ranked crops
#
# =========================================================

import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# LOAD DATASET
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR / "final_3season_dataset.csv"
)

_dataset = pd.read_csv(DATASET_PATH)

_dataset.columns = [
    str(col).strip()
    for col in _dataset.columns
]

# =========================================================
# NEXT SEASON MAP
# =========================================================

NEXT_SEASON_MAP = {

    "Kharif": "Rabi",

    "Rabi": "Summer",

    "Summer": "Kharif",
}

# =========================================================
# ROTATION RULES
# =========================================================

ROTATION_RULES = {

    "Rice": {

        "goodAfter": [

            "Gram",
            "Groundnut",
            "Mustard",
        ],

        "avoid": [

            "Rice"
        ]
    },

    "Wheat": {

        "goodAfter": [

            "Soyabean",
            "Gram",
        ],

        "avoid": [

            "Wheat"
        ]
    },

    "Groundnut": {

        "goodAfter": [

            "Cotton",
            "Rice",
        ],

        "avoid": [

            "Groundnut",
            "Soyabean",
        ]
    },

    "Cotton": {

        "goodAfter": [

            "Gram",
            "Wheat",
        ],

        "avoid": [

            "Cotton"
        ]
    },
}

# =========================================================
# CROP FAMILIES
# =========================================================

CROP_FAMILIES = {

    "Rice": "Poaceae",

    "Wheat": "Poaceae",

    "Maize": "Poaceae",

    "Groundnut": "Fabaceae",

    "Soyabean": "Fabaceae",

    "Gram": "Fabaceae",

    "Cotton": "Malvaceae",

    "Mustard": "Brassicaceae",

    "Sugarcane": "Poaceae",
}

# =========================================================
# NUTRIENT DEMAND
# =========================================================

NUTRIENT_DEMAND = {

    "Rice": "High",

    "Wheat": "High",

    "Sugarcane": "High",

    "Cotton": "Medium",

    "Groundnut": "Low",

    "Gram": "Low",

    "Soyabean": "Low",
}

# =========================================================
# NORMALIZE
# =========================================================

def normalize_crop_name(crop):

    crop = str(crop).strip()

    crop = crop.replace("_", " ")

    crop = crop.replace("-", " ")

    crop = " ".join(crop.split())

    crop = crop.title()

    return crop

# =========================================================
# DISTANCE
# =========================================================

def calculate_distance(

    lat1,
    lon1,
    lat2,
    lon2
):

    return np.sqrt(

        (lat1 - lat2) ** 2

        +

        (lon1 - lon2) ** 2
    )

# =========================================================
# GET NEXT SEASON
# =========================================================

def get_next_season(current_season):

    current_season = str(
        current_season
    ).strip().title()

    return NEXT_SEASON_MAP.get(
        current_season
    )

# =========================================================
# GET SEASON COLUMN
# =========================================================

def get_season_column(season):

    return f"Main_{season}"

# =========================================================
# EXTRACT CROPS
# =========================================================

def extract_crops(value):

    if pd.isna(value):

        return []

    crops = []

    for crop in str(value).split(","):

        crop = normalize_crop_name(crop)

        if crop:

            crops.append(crop)

    # Remove duplicates

    unique = []

    seen = set()

    for crop in crops:

        key = crop.lower()

        if key not in seen:

            unique.append(crop)

            seen.add(key)

    return unique

# =========================================================
# MAIN FUNCTION
# =========================================================

def get_next_season_rotation(

    latitude,
    longitude,

    current_season,

    previous_crop,
):

    # =====================================================
    # DETECT NEXT SEASON
    # =====================================================

    next_season = get_next_season(
        current_season
    )

    if not next_season:

        return {

            "error": "Invalid current season"
        }

    season_column = get_season_column(
        next_season
    )

    # =====================================================
    # FILTER VALID COORDINATES
    # =====================================================

    df = _dataset.dropna(

        subset=["Latitude", "Longitude"]

    ).copy()

    # =====================================================
    # CALCULATE DISTANCE
    # =====================================================

    df["distance"] = df.apply(

        lambda row: calculate_distance(

            latitude,
            longitude,

            row["Latitude"],
            row["Longitude"],
        ),

        axis=1
    )

    # =====================================================
    # NEAREST DISTRICT
    # =====================================================

    nearest_row = (

        df.sort_values("distance")

        .iloc[0]
    )

    district = nearest_row["District"]

    state = nearest_row["State"]

    distance = round(
        nearest_row["distance"],
        4
    )

    # =====================================================
    # FETCH NEXT SEASON CROPS
    # =====================================================

    next_crops = extract_crops(

        nearest_row.get(
            season_column,
            ""
        )
    )

    # =====================================================
    # ROTATION FILTERING
    # =====================================================

    previous_crop = normalize_crop_name(
        previous_crop
    )

    previous_family = CROP_FAMILIES.get(
        previous_crop
    )

    rotation_rules = ROTATION_RULES.get(

        previous_crop,

        {}
    )

    avoid_crops = rotation_rules.get(
        "avoid",
        []
    )

    good_after = rotation_rules.get(
        "goodAfter",
        []
    )

    ranked = []

    for crop in next_crops:

        score = 50

        crop_family = CROP_FAMILIES.get(
            crop
        )

        nutrient = NUTRIENT_DEMAND.get(
            crop,
            "Medium"
        )

        # -------------------------------------------------
        # AVOID SAME CROP
        # -------------------------------------------------

        if crop == previous_crop:

            score -= 50

        # -------------------------------------------------
        # AVOID SAME FAMILY
        # -------------------------------------------------

        if (

            previous_family

            and crop_family

            and previous_family == crop_family
        ):

            score -= 30

        # -------------------------------------------------
        # AVOID ROTATION CONFLICTS
        # -------------------------------------------------

        if crop in avoid_crops:

            score -= 25

        # -------------------------------------------------
        # GOOD AFTER BONUS
        # -------------------------------------------------

        if crop in good_after:

            score += 35

        # -------------------------------------------------
        # LOW NUTRIENT BONUS
        # -------------------------------------------------

        if nutrient == "Low":

            score += 10

        # -------------------------------------------------
        # HIGH NUTRIENT PENALTY
        # -------------------------------------------------

        if nutrient == "High":

            score -= 10

        ranked.append({

            "crop": crop,

            "score": score,

            "family": crop_family,

            "nutrientDemand": nutrient,
        })

    # =====================================================
    # SORT BEST FIRST
    # =====================================================

    ranked = sorted(

        ranked,

        key=lambda x: x["score"],

        reverse=True
    )

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return {

        "district": district,

        "state": state,

        "distance": distance,

        "currentSeason": current_season,

        "nextSeason": next_season,

        "previousCrop": previous_crop,

        "recommendedRotation": ranked[:5]
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    result = get_next_season_rotation(

        latitude=18.5204,
        longitude=73.8567,

        current_season="Summer",

        previous_crop="Groundnut",
    )

    from pprint import pprint

    pprint(result)

