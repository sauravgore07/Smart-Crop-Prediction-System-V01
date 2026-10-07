
"""
Create district-season ranked crop dataset.

INPUT:
CSV containing columns like:
- State_Name
- District_Name
- Season
- Crop
- Area
- Production
- Yield

OUTPUT:
State,District,Kharif,Rabi,Zaid

Example:
Maharashtra,Pune,"Rice,Maize,Cotton","Wheat,Gram","Watermelon,Cucumber"
"""

import pandas as pd
import numpy as np
import pathlib

# =========================================================
# CONFIG
# =========================================================
BASE_DIR = pathlib.Path(__file__).parent


INPUT_CSV = BASE_DIR /"Indian_crop_production_yield_dataset.csv"
OUTPUT_CSV = "district_season_crop_ranking.csv"

# Top crops to keep per season
TOP_N = 10

# =========================================================
# LOAD CSV
# =========================================================

print("Loading dataset...")

df = pd.read_csv(INPUT_CSV)

print(f"Loaded {len(df)} rows")

# =========================================================
# COLUMN DETECTION
# =========================================================

COLUMN_PATTERNS = {
    "state": [
        "state",
        "state_name",
        "state name",
    ],

    "district": [
        "district",
        "district_name",
        "district name",
    ],

    "season": [
        "season",
    ],

    "crop": [
        "crop",
        "crop_name",
        "crop name",
    ],

    "area": [
        "area",
    ],

    "production": [
        "production",
    ],

    "yield": [
        "yield",
    ]
}


def normalize_col(col):
    return str(col).strip().lower()


normalized_columns = {
    normalize_col(col): col
    for col in df.columns
}

detected = {}

for key, patterns in COLUMN_PATTERNS.items():

    found = None

    for pattern in patterns:

        if pattern in normalized_columns:
            found = normalized_columns[pattern]
            break

    if not found:
        raise ValueError(
            f"Could not detect required column: {key}"
        )

    detected[key] = found

print("\nDetected columns:")
for k, v in detected.items():
    print(f"{k} -> {v}")

# =========================================================
# CLEAN DATA
# =========================================================

required_cols = [
    detected["state"],
    detected["district"],
    detected["season"],
    detected["crop"],
    detected["area"],
    detected["production"],
    detected["yield"],
]

df = df[required_cols].copy()

df.columns = [
    "State",
    "District",
    "Season",
    "Crop",
    "Area",
    "Production",
    "Yield",
]

# Remove missing values
df = df.dropna(
    subset=[
        "State",
        "District",
        "Season",
        "Crop",
    ]
)

# =========================================================
# CLEAN NUMERIC VALUES
# =========================================================

for col in ["Area", "Production", "Yield"]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    df[col] = df[col].fillna(0)

# =========================================================
# NORMALIZATION
# =========================================================

def minmax(series):

    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return pd.Series(
            [1] * len(series),
            index=series.index
        )

    return (
        (series - min_val)
        / (max_val - min_val)
    )


# Normalize globally
df["Area_Norm"] = minmax(df["Area"])
df["Production_Norm"] = minmax(df["Production"])
df["Yield_Norm"] = minmax(df["Yield"])

# =========================================================
# SCORE CALCULATION
# =========================================================

"""
Balanced score:
- Area importance
- Production importance
- Yield importance
"""

df["Score"] = (
    df["Area_Norm"] * 0.35
    + df["Production_Norm"] * 0.40
    + df["Yield_Norm"] * 0.25
)

# =========================================================
# GROUPING + RANKING
# =========================================================

print("\nGenerating seasonal rankings...")

grouped = df.groupby(
    ["State", "District", "Season"]
)

records = []

season_data = {}

for (state, district, season), group in grouped:

    # Aggregate crop scores
    crop_scores = (
        group.groupby("Crop")["Score"]
        .mean()
        .sort_values(ascending=False)
    )

    ranked_crops = list(crop_scores.index[:TOP_N])

    crops_string = ",".join(ranked_crops)

    key = (state, district)

    if key not in season_data:
        season_data[key] = {
            "State": state,
            "District": district,
        }

    season_data[key][season] = crops_string

# =========================================================
# CREATE FINAL DATAFRAME
# =========================================================

final_df = pd.DataFrame(
    list(season_data.values())
)
# =========================================================
# SAFE COLUMN ORDERING
# =========================================================

preferred_order = [
    "State",
    "District",
    "Kharif",
    "Rabi",
    "Zaid",
]

# Keep only columns that actually exist
existing_priority_cols = [
    col
    for col in preferred_order
    if col in final_df.columns
]

# Remaining dynamic columns
other_cols = [
    col
    for col in final_df.columns
    if col not in existing_priority_cols
]

# Final ordering
final_df = final_df[
    existing_priority_cols + other_cols
]


# =========================================================
# SAVE OUTPUT
# =========================================================

final_df.to_csv(
    OUTPUT_CSV,
    index=False
)

print("\n=================================================")
print("DONE")
print("=================================================")

print(f"\nOutput saved to:")
print(OUTPUT_CSV)

print("\nPreview:")
print(final_df.head())

print("\nTotal districts processed:")
print(len(final_df))
