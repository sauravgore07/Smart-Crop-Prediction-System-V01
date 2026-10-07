
"""
predictor.py

FINAL HYBRID AGRICULTURAL RECOMMENDATION ENGINE
------------------------------------------------------------

Architecture:
------------------------------------------------------------

User Lat/Lon
    ↓
Nearest District Retrieval
    ↓
Fetch Main Season Crops
    ↓
Apply:
    - Crop Rotation
    - Previous Crop Soil Memory
    - Soil Compatibility
    ↓
Final Ranked Recommendations

------------------------------------------------------------
Uses:
    Main_Kharif
    Main_Rabi
    Main_Summer
------------------------------------------------------------
"""

import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# LOAD DATASET
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR.parent.parent.parent
    / "ml_training"
    / "final_3season_dataset.csv"
)

print(f"\nLoading dataset:\n{DATASET_PATH}")

_dataset = pd.read_csv(DATASET_PATH)

print(f"Dataset shape: {_dataset.shape}")

# =========================================================
# CLEAN COLUMNS
# =========================================================

_dataset.columns = [
    str(col).strip()
    for col in _dataset.columns
]

# =========================================================
# SEASON MAPPING
# =========================================================

SEASON_MAPPING = {

    "Kharif": "Main_Kharif",

    "Rabi": "Main_Rabi",

    "Summer": "Main_Summer",
}

# =========================================================
# ROTATION RULES
# =========================================================

ROTATION_RULES = {

    "Rice": {
        "prefer": ["Gram", "Wheat"],
        "avoid": ["Rice"],
    },

    "Wheat": {
        "prefer": ["Soyabean", "Gram"],
        "avoid": ["Wheat"],
    },

    "Cotton": {
        "prefer": ["Groundnut"],
        "avoid": ["Cotton"],
    },

    "Sugarcane": {
        "prefer": ["Gram"],
        "avoid": ["Sugarcane"],
    },
}

# =========================================================
# PREVIOUS CROP EFFECTS
# =========================================================

PREVIOUS_CROP_EFFECTS = {

    "Gram": {
        "nitrogen": +15,
    },

    "Rice": {
        "nitrogen": -10,
    },

    "Sugarcane": {
        "nitrogen": -20,
        "potassium": -15,
    },

    "Cotton": {
        "potassium": -10,
    },
}

# =========================================================
# NORMALIZE CROP NAME
# =========================================================

def normalize_crop_name(crop):

    crop = str(crop).strip()

    crop = crop.replace("_", " ")

    crop = crop.replace("-", " ")

    crop = " ".join(crop.split())

    crop = crop.title()

    return crop

# =========================================================
# DISTANCE CALCULATION
# =========================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    return np.sqrt(
        (lat1 - lat2) ** 2
        + (lon1 - lon2) ** 2
    )

# =========================================================
# APPLY PREVIOUS CROP EFFECTS
# =========================================================

def apply_previous_crop_effects(data):

    adjusted = {

        "nitrogen": data.nitrogen,

        "phosphorus": data.phosphorus,

        "potassium": data.potassium,
    }

    previous_crop = getattr(
        data,
        "previous_crop",
        None
    )

    if not previous_crop:
        return adjusted

    previous_crop = normalize_crop_name(
        previous_crop
    )

    effects = PREVIOUS_CROP_EFFECTS.get(
        previous_crop
    )

    if not effects:
        return adjusted

    for key, value in effects.items():

        adjusted[key] += value

    return adjusted

# =========================================================
# EXTRACT CROPS
# =========================================================

def extract_season_crops(row, season_column):

    if season_column not in row.index:
        return []

    value = row[season_column]

    if pd.isna(value):
        return []

    crops = [

        normalize_crop_name(crop)

        for crop in str(value).split(",")

        if crop.strip()
    ]

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
# SOIL SCORE
# =========================================================

def get_soil_score(crop, soil):

    score = 0

    nitrogen = soil["nitrogen"]

    potassium = soil["potassium"]

    phosphorus = soil["phosphorus"]

    # -----------------------------------------------------
    # Nitrogen-demanding crops
    # -----------------------------------------------------

    if crop in ["Wheat", "Rice"]:

        if nitrogen >= 50:
            score += 12
        else:
            score -= 8

    # -----------------------------------------------------
    # Pulses for low nitrogen
    # -----------------------------------------------------

    if crop in [

        "Gram",
        "Moong(Green Gram)",
        "Urad",
        "Peas & Beans (Pulses)",
    ]:

        if nitrogen < 50:
            score += 18

    # -----------------------------------------------------
    # Potassium demanding
    # -----------------------------------------------------

    if crop == "Sugarcane":

        if potassium >= 50:
            score += 12

    # -----------------------------------------------------
    # Oilseed preference
    # -----------------------------------------------------

    if crop in [

        "Groundnut",
        "Sunflower",
        "Sesamum",
    ]:

        if phosphorus >= 40:
            score += 10

    return score

# =========================================================
# ROTATION SCORE
# =========================================================

def get_rotation_score(
    crop,
    previous_crop
):

    if not previous_crop:
        return 0

    previous_crop = normalize_crop_name(
        previous_crop
    )

    rules = ROTATION_RULES.get(
        previous_crop
    )

    if not rules:
        return 0

    score = 0

    # Prefer crops
    if crop in rules.get("prefer", []):

        score += 20

    # Avoid same crop repetition
    if crop in rules.get("avoid", []):

        score -= 25

    return score

# =========================================================
# SUITABILITY LABEL
# =========================================================

def get_suitability_label(confidence):

    if confidence >= 80:
        return "Highly Suitable"

    elif confidence >= 60:
        return "Suitable"

    elif confidence >= 40:
        return "Moderately Suitable"

    return "Low Suitable"

# =========================================================
# MAIN PREDICTION FUNCTION
# =========================================================

def predict_crops(data):

    # =====================================================
    # NORMALIZE SEASON
    # =====================================================

    user_season = str(
        data.season
    ).strip().title()

    # =====================================================
    # MAP TO MAIN SEASON
    # =====================================================

    season_column = SEASON_MAPPING.get(
        user_season
    )

    if not season_column:

        print(f"Invalid season: {user_season}")

        return []

    print(
        f"\nUser Season: {user_season}"
    )

    print(
        f"Mapped Season Column: {season_column}"
    )

    # =====================================================
    # APPLY SOIL MEMORY
    # =====================================================

    adjusted_soil = apply_previous_crop_effects(
        data
    )

    # =====================================================
    # FILTER VALID COORDINATES
    # =====================================================

    df = _dataset.dropna(
        subset=["Latitude", "Longitude"]
    ).copy()

    # =====================================================
    # DISTANCE CALCULATION
    # =====================================================

    df["distance"] = df.apply(

        lambda row: calculate_distance(

            data.latitude,
            data.longitude,

            row["Latitude"],
            row["Longitude"],
        ),

        axis=1
    )

    # =====================================================
    # USE ONLY NEAREST DISTRICT
    # =====================================================

    nearest_row = (

        df.sort_values("distance")

        .iloc[0]
    )

    nearest_district = nearest_row["District"]

    nearest_state = nearest_row["State"]

    nearest_distance = round(
        nearest_row["distance"],
        4
    )

    print(
        f"\nNearest District:"
        f" {nearest_district},"
        f" {nearest_state}"
    )

    print(
        f"Distance: {nearest_distance}"
    )

    # =====================================================
    # FETCH CROPS DIRECTLY
    # =====================================================

    season_crops = extract_season_crops(

        nearest_row,

        season_column
    )

    print(
        f"\nSeason Crops ({season_column}):"
    )

    print(season_crops)

    # =====================================================
    # EMPTY CHECK
    # =====================================================

    if not season_crops:

        print("No crops found.")

        return []

    # =====================================================
    # LIGHTWEIGHT SCORING
    # =====================================================

    crop_scores = []

    for rank, crop in enumerate(season_crops):

        # -------------------------------------------------
        # BASE SCORE FROM CSV PRIORITY
        # -------------------------------------------------

        score = 100 - (rank * 8)

        # -------------------------------------------------
        # ROTATION SCORE
        # -------------------------------------------------

        score += get_rotation_score(

            crop,

            getattr(
                data,
                "previous_crop",
                None
            )
        )

        # -------------------------------------------------
        # SOIL SCORE
        # -------------------------------------------------

        score += get_soil_score(

            crop,

            adjusted_soil
        )

        # -------------------------------------------------
        # DISTANCE PENALTY
        # -------------------------------------------------

        score -= nearest_distance * 2

        # -------------------------------------------------
        # CLAMP SCORE
        # -------------------------------------------------

        score = max(
            0,
            min(score, 100)
        )

        crop_scores.append({

            "crop": crop,

            "raw_score": score
        })

    # =====================================================
    # SORT RESULTS
    # =====================================================

    crop_scores = sorted(

        crop_scores,

        key=lambda x: x["raw_score"],

        reverse=True
    )

    # =====================================================
# FINAL RESPONSE
# =====================================================

    results = []

    for item in crop_scores[:10]:

        crop = item["crop"]

        confidence = float(
            round(
                item["raw_score"],
                2
            )
        )

        suitability_label = get_suitability_label(
            confidence
        )

        results.append({

            "crop": crop,

            "confidence": confidence,

            # Numeric value for UI %
            "suitability": confidence,

            # Text label
            "suitability_label": suitability_label,
        })

    print("\nFinal Recommendations:")

    for result in results:

        print(result)

    return results