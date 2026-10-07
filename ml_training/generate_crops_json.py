
"""
generate_crops_json.py

SMART Crop JSON Generator
---------------------------------------------------------

Features:
---------------------------------------------------------
✓ Auto detects crops from CSV
✓ Removes garbage categories
✓ Smart category detection
✓ Smart season assignment
✓ Smart emoji assignment
✓ Smart profitability
✓ Smart nutrient demand
✓ Smart water needs
✓ Smart crop duration
✓ Smart rotation rules
✓ Updates placeholder crops
✓ Creates backups automatically
✓ Deduplicates crops

---------------------------------------------------------
OUTPUT:
backend/app/data/crops.json
---------------------------------------------------------
"""

import json
import pathlib
import pandas as pd

# =========================================================
# IMPORT HELPERS
# =========================================================

from train_model import (

    split_crop_field,

    normalize_crop_name,
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = pathlib.Path(__file__).parent

CSV_PATH = (
    BASE_DIR / "final_3season_dataset.csv"
)

CROPS_JSON_PATH = (

    BASE_DIR.parent

    / "backend"

    / "app"

    / "data"

    / "crops.json"
)

BACKUP_JSON_PATH = (

    BASE_DIR.parent

    / "backend"

    / "app"

    / "data"

    / "crops_backup.json"
)

# =========================================================
# REMOVE INVALID CATEGORIES
# =========================================================

REMOVE_CROPS = {

    "Other Cereals",
    "Other Oilseeds",
    "Other Summer Pulses",
    "Other Summer Oilseeds",
    "Other Kharif Pulses",
    "Other Rabi Pulses",
    "Other Crops",
    "Other",
    "Others",
    "Unknown",
    "Total",
    "Mixed",
}

# =========================================================
# CATEGORY MAPS
# =========================================================

CEREALS = {

    "Rice",
    "Wheat",
    "Maize",
    "Barley",
    "Pearl Millet",
    "Finger Millet",
    "Sorghum",
    "Bajra",
    "Jowar",
}

PULSES = {

    "Gram",
    "Chickpea",
    "Blackgram",
    "Mungbean",
    "Urad",
    "Peas & Beans (Pulses)",
    "Lentil",
}

OILSEEDS = {

    "Groundnut",
    "Mustard",
    "Sesamum",
    "Sunflower",
    "Soybean",
    "Castor Seed",
    "Linseed",
}

FRUITS = {

    "Mango",
    "Banana",
    "Pomegranate",
    "Grapes",
    "Apple",
    "Orange",
    "Watermelon",
    "Pineapple",
}

VEGETABLES = {

    "Tomato",
    "Potato",
    "Onion",
    "Garlic",
    "Chilli",
    "Cabbage",
    "Cauliflower",
    "Brinjal",
}

# =========================================================
# IMAGE MAP
# =========================================================

IMAGE_MAP = {

    "Rice": "🌾",
    "Wheat": "🌾",
    "Maize": "🌽",
    "Sugarcane": "🎋",
    "Cotton": "☁️",

    "Groundnut": "🥜",
    "Sunflower": "🌻",

    "Banana": "🍌",
    "Mango": "🥭",
    "Watermelon": "🍉",
    "Pineapple": "🍍",
    "Apple": "🍏",
    "Orange": "🍊",
    "Grapes": "🍇",

    "Onion": "🧅",
    "Tomato": "🍅",
    "Potato": "🥔",
    "Garlic": "🧄",
    "Chilli": "🌶️",

    "Soybean": "🌱",
    "Mustard": "🌼",
}

# =========================================================
# SEASON MAP
# =========================================================

SEASON_MAP = {

    "Rice": ["Main_Kharif"],

    "Wheat": ["Main_Rabi"],

    "Groundnut": [
        "Main_Kharif",
        "Main_Summer"
    ],

    "Sugarcane": [
        "Main_Summer"
    ],

    "Cotton": [
        "Main_Kharif"
    ],

    "Gram": [
        "Main_Rabi"
    ],

    "Watermelon": [
        "Main_Summer"
    ],
}

# =========================================================
# PROFIT MAP
# =========================================================

HIGH_PROFIT = {

    "Sugarcane",
    "Banana",
    "Cotton",
    "Grapes",
    "Pomegranate",
}

MEDIUM_PROFIT = {

    "Rice",
    "Wheat",
    "Groundnut",
    "Tomato",
    "Onion",
    "Potato",
}

# =========================================================
# ROTATION RULES
# =========================================================

ROTATION_RULES = {

    "Rice": {
        "goodAfter": [
            "Gram",
            "Groundnut"
        ],
        "avoid": [
            "Rice"
        ]
    },

    "Wheat": {
        "goodAfter": [
            "Soybean",
            "Gram"
        ],
        "avoid": [
            "Wheat"
        ]
    },

    "Cotton": {
        "goodAfter": [
            "Groundnut"
        ],
        "avoid": [
            "Cotton"
        ]
    },
}

# =========================================================
# LOAD EXISTING JSON
# =========================================================

with open(
    CROPS_JSON_PATH,
    "r",
    encoding="utf-8"
) as f:

    crops = json.load(f)

# =========================================================
# BACKUP
# =========================================================

with open(
    BACKUP_JSON_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        crops,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"\nBackup created:")
print(BACKUP_JSON_PATH)

# =========================================================
# LOAD CSV
# =========================================================

df = pd.read_csv(CSV_PATH)

# =========================================================
# DETECT SEASON COLUMNS
# =========================================================

SEASON_COLUMNS = [

    "Main_Kharif",
    "Main_Rabi",
    "Main_Summer",
]

# =========================================================
# EXTRACT CROPS
# =========================================================

all_csv_crops = set()

crop_seasons = {}

for season_col in SEASON_COLUMNS:

    if season_col not in df.columns:
        continue

    for value in df[season_col].dropna():

        split_crops = split_crop_field(value)

        for crop in split_crops:

            normalized = normalize_crop_name(crop)

            if not normalized:
                continue

            if normalized in REMOVE_CROPS:
                continue

            all_csv_crops.add(normalized)

            if normalized not in crop_seasons:

                crop_seasons[normalized] = set()

            crop_seasons[normalized].add(
                season_col
            )

print(
    f"\nFound "
    f"{len(all_csv_crops)} "
    f"valid crops"
)

# =========================================================
# CREATE SMART TEMPLATE
# =========================================================

def create_crop_template(name, crop_id):

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    category = "Cash Crops"

    if name in CEREALS:
        category = "Cereals"

    elif name in PULSES:
        category = "Pulses"

    elif name in OILSEEDS:
        category = "Oilseeds"

    elif name in FRUITS:
        category = "Fruits"

    elif name in VEGETABLES:
        category = "Vegetables"

    # -----------------------------------------------------
    # IMAGE
    # -----------------------------------------------------

    image = IMAGE_MAP.get(name, "🌱")

    # -----------------------------------------------------
    # SEASONS
    # -----------------------------------------------------

    seasons = list(

        crop_seasons.get(
            name,
            ["Main_Kharif"]
        )
    )

    # -----------------------------------------------------
    # PROFIT
    # -----------------------------------------------------

    profit = 30000

    if name in HIGH_PROFIT:

        profit = 120000

    elif name in MEDIUM_PROFIT:

        profit = 60000

    # -----------------------------------------------------
    # WATER NEEDS
    # -----------------------------------------------------

    water_needs = "Medium"

    if name in [

        "Rice",
        "Sugarcane",
        "Banana",
    ]:

        water_needs = "High"

    elif name in [

        "Groundnut",
        "Sesamum",
        "Mustard",
    ]:

        water_needs = "Low"

    # -----------------------------------------------------
    # NUTRIENT DEMAND
    # -----------------------------------------------------

    nutrient_demand = "Medium"

    if name in [

        "Rice",
        "Wheat",
        "Sugarcane",
    ]:

        nutrient_demand = "High"

    # -----------------------------------------------------
    # DURATION
    # -----------------------------------------------------

    duration = "90-120 days"

    if name == "Sugarcane":

        duration = "10-18 months"

    elif name in [

        "Watermelon",
        "Moong(Green Gram)",
    ]:

        duration = "60-90 days"

    # -----------------------------------------------------
    # ROTATION
    # -----------------------------------------------------

    rotation = ROTATION_RULES.get(

        name,

        {
            "goodAfter": [],
            "goodBefore": [],
            "avoid": [name]
        }
    )

    # -----------------------------------------------------
    # TEMPLATE
    # -----------------------------------------------------

    return {

        "id": crop_id,

        "name": name,

        "scientificName": "",

        "category": category,

        "image": image,

        "duration": duration,

        "yield": "2-5 tons/hectare",

        "investment": "Medium",

        "season": seasons,

        "requirements": {

            "tempMin": 20,

            "tempMax": 35,

            "rainfallMin": 500,

            "rainfallMax": 1500,

            "soilTypes": [
                "Loamy"
            ],

            "phMin": 5.5,

            "phMax": 7.5,

            "waterNeeds": water_needs,
        },

        "profitability": {

            "costPerHectare": int(profit * 0.4),

            "revenuePerHectare": int(profit * 1.4),

            "profitPerHectare": profit,

            "riskLevel": "Medium",

            "marketDemand": "Medium",

            "priceTrend": "Stable",
        },

        "description": (
            f"{name} is an important crop "
            f"suitable for Indian agriculture."
        ),

        "tips": [

            "Use quality seeds",

            "Monitor irrigation regularly",

            "Follow crop rotation practices",
        ],

        "family": "",

        "nutrientDemand": nutrient_demand,

        "rootDepth": "Medium",

        "rotation": rotation,
    }

# =========================================================
# ADD / UPDATE CROPS
# =========================================================

next_id = max(
    crop["id"]
    for crop in crops
) + 1

added = 0
updated = 0

for crop_name in sorted(all_csv_crops):

    existing_crop = next(

        (
            c for c in crops

            if c["name"].strip().lower()

            == crop_name.strip().lower()
        ),

        None
    )

    # -----------------------------------------------------
    # UPDATE PLACEHOLDERS
    # -----------------------------------------------------

    if existing_crop:

        is_placeholder = (

            existing_crop.get("image") == "🌱"

            or existing_crop.get("category")
            == "Unknown"

            or existing_crop.get("yield")
            in ["Unknown", "—", None]
        )

        if is_placeholder:

            improved = create_crop_template(

                crop_name,

                existing_crop["id"]
            )

            improved["id"] = existing_crop["id"]

            improved["name"] = existing_crop["name"]

            existing_crop.update(improved)

            updated += 1

            print(f"Updated: {crop_name}")

    # -----------------------------------------------------
    # ADD NEW CROPS
    # -----------------------------------------------------

    else:

        crops.append(

            create_crop_template(

                crop_name,

                next_id
            )
        )

        print(f"Added: {crop_name}")

        next_id += 1

        added += 1

# =========================================================
# SORT BY ID
# =========================================================

crops = sorted(

    crops,

    key=lambda x: x["id"]
)

# =========================================================
# SAVE JSON
# =========================================================

with open(
    CROPS_JSON_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(

        crops,

        f,

        indent=2,

        ensure_ascii=False
    )

# =========================================================
# REPORT
# =========================================================

print("\n===================================")
print("CROPS JSON GENERATION COMPLETE")
print("===================================")

print(f"\nAdded crops   : {added}")

print(f"Updated crops : {updated}")

print(f"\nSaved JSON:")
print(CROPS_JSON_PATH)

print(
    f"\nTotal crops:"
    f" {len(crops)}"
)

