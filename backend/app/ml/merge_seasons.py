
"""
merge_seasons.py

Convert:
-------------------------------------------------
Kharif + Autumn      -> Main_Kharif
Rabi + Winter        -> Main_Rabi
Summer + Whole Year  -> Main_Summer

Also:
-------------------------------------------------
✓ Removes duplicate crops
✓ Removes generic useless categories
✓ Cleans crop names
✓ Handles missing columns safely
✓ Preserves original dataset
"""

import pandas as pd
from pathlib import Path

# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = Path(__file__).parent

INPUT_CSV = (
    BASE_DIR / "district_with_coordinates.csv"
)

OUTPUT_CSV = (
    BASE_DIR / "final_3season_dataset.csv"
)

# =========================================================
# LOAD DATASET
# =========================================================

print("Loading dataset...")

df = pd.read_csv(INPUT_CSV)

print(f"Rows loaded: {len(df)}")

# =========================================================
# CLEAN GENERIC / USELESS CATEGORIES
# =========================================================

REMOVE_CROPS = {

    # Generic placeholders
    "Other Cereals",
    "Other Kharif Pulses",
    "Other Rabi Pulses",
    "Other Summer Pulses",
    "Other Oilseeds",
    "Other Summer Oilseeds",
    "Other Fresh Fruits",
    "Other Vegetables",

    # Noise categories
    "Other Crops",
    "Other Fibres",
    "Other Dry Fruit",
    "Other Citrus Fruit",

    # Invalid / vague
    "Total",
    "Unknown",
    "Others",
    "Other",

    # Dataset garbage
    "All",
    "Mixed",
}

# =========================================================
# NORMALIZE CROP NAME
# =========================================================

def normalize_crop(crop):

    crop = str(crop).strip()

    crop = crop.replace("_", " ")

    crop = crop.replace("-", " ")

    crop = " ".join(crop.split())

    crop = crop.title()

    return crop

# =========================================================
# CLEAN CROPS
# =========================================================

def clean_crop_list(crop_string):

    if pd.isna(crop_string):
        return []

    crops = []

    for crop in str(crop_string).split(","):

        crop = normalize_crop(crop)

        if not crop:
            continue

        # Remove useless categories
        if crop in REMOVE_CROPS:
            continue

        crops.append(crop)

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    unique_crops = []

    seen = set()

    for crop in crops:

        key = crop.lower()

        if key not in seen:

            unique_crops.append(crop)

            seen.add(key)

    return unique_crops

# =========================================================
# MERGE SEASON COLUMNS
# =========================================================

def merge_columns(row, columns):

    merged = []

    for col in columns:

        if col not in row.index:
            continue

        crops = clean_crop_list(row[col])

        merged.extend(crops)

    # -----------------------------------------------------
    # REMOVE DUPLICATES AGAIN
    # -----------------------------------------------------

    final = []

    seen = set()

    for crop in merged:

        key = crop.lower()

        if key not in seen:

            final.append(crop)

            seen.add(key)

    return ",".join(final)

# =========================================================
# CREATE MAIN SEASONS
# =========================================================

print("\nCreating merged seasons...")

# ---------------------------------------------------------
# KHARIF
# ---------------------------------------------------------

df["Main_Kharif"] = df.apply(

    lambda row: merge_columns(
        row,
        [
            "Kharif",
            "Autumn",
        ]
    ),

    axis=1
)

# ---------------------------------------------------------
# RABI
# ---------------------------------------------------------

df["Main_Rabi"] = df.apply(

    lambda row: merge_columns(
        row,
        [
            "Rabi",
            "Winter",
        ]
    ),

    axis=1
)

# ---------------------------------------------------------
# SUMMER
# ---------------------------------------------------------

df["Main_Summer"] = df.apply(

    lambda row: merge_columns(
        row,
        [
            "Summer",
            "Whole Year",
        ]
    ),

    axis=1
)

# =========================================================
# OPTIONAL:
# REMOVE OLD SEASON COLUMNS
# =========================================================

OLD_SEASONS = [

    "Kharif",
    "Autumn",

    "Rabi",
    "Winter",

    "Summer",
    "Whole Year",
]

existing_old = [
    col
    for col in OLD_SEASONS
    if col in df.columns
]

df = df.drop(
    columns=existing_old,
    errors="ignore"
)

# =========================================================
# COLUMN ORDER
# =========================================================

priority_cols = [

    "State",
    "District",

    "Latitude",
    "Longitude",

    "Main_Kharif",
    "Main_Rabi",
    "Main_Summer",
]

existing_priority = [
    col
    for col in priority_cols
    if col in df.columns
]

other_cols = [
    col
    for col in df.columns
    if col not in existing_priority
]

df = df[
    existing_priority + other_cols
]

# =========================================================
# SAVE
# =========================================================

df.to_csv(
    OUTPUT_CSV,
    index=False
)

# =========================================================
# REPORT
# =========================================================

print("\n===================================")
print("SEASON MERGING COMPLETE")
print("===================================")

print(f"\nSaved dataset:")
print(OUTPUT_CSV)

print("\nPreview:")

print(
    df[
        [
            "District",
            "Main_Kharif",
            "Main_Rabi",
            "Main_Summer",
        ]
    ].head()
)

print("\nFinal columns:")

print(df.columns.tolist())

print(f"\nTotal rows: {len(df)}")
