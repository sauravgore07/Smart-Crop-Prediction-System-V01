
import pandas as pd
import time
from pathlib import Path
from geopy.geocoders import Nominatim

# =========================================================
# FILES
# =========================================================

BASE_DIR = Path(__file__).parent

INPUT_CSV = BASE_DIR / "district_season_crop_ranking.csv"

OUTPUT_CSV = BASE_DIR / "district_with_coordinates.csv"
 
# =========================================================
# LOAD DATA
# =========================================================

print("Loading dataset...")

df = pd.read_csv(INPUT_CSV)

print(f"Rows loaded: {len(df)}")

# =========================================================
# VALIDATION
# =========================================================

required_cols = ["State", "District"]

for col in required_cols:

    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# =========================================================
# GEOCODER
# =========================================================

geolocator = Nominatim(
    user_agent="crop_recommendation_system"
)

# =========================================================
# CACHE
# =========================================================

geo_cache = {}

# =========================================================
# RESULT STORAGE
# =========================================================

latitudes = []
longitudes = []

# =========================================================
# GEOCODING
# =========================================================

print("\nStarting geocoding...\n")

for index, row in df.iterrows():

    state = str(row["State"]).strip()

    district = str(row["District"]).strip()

    query = f"{district}, {state}, India"

    # -----------------------------------------------------
    # CACHE HIT
    # -----------------------------------------------------

    if query in geo_cache:

        lat, lon = geo_cache[query]

        latitudes.append(lat)

        longitudes.append(lon)

        print(f"[CACHE] {query}")

        continue

    # -----------------------------------------------------
    # GEOCODE
    # -----------------------------------------------------

    try:

        location = geolocator.geocode(
            query,
            timeout=10
        )

        if location:

            lat = location.latitude

            lon = location.longitude

            print(
                f"[OK] {query} -> "
                f"{lat}, {lon}"
            )

        else:

            lat = None

            lon = None

            print(f"[NOT FOUND] {query}")

        geo_cache[query] = (lat, lon)

        latitudes.append(lat)

        longitudes.append(lon)

        # Respect API limits
        time.sleep(1)

    except Exception as e:

        print(f"[ERROR] {query} -> {e}")

        latitudes.append(None)

        longitudes.append(None)

# =========================================================
# ADD TO DATAFRAME
# =========================================================

df["Latitude"] = latitudes

df["Longitude"] = longitudes

# =========================================================
# COLUMN ORDER
# =========================================================

priority_cols = [
    "State",
    "District",
    "Latitude",
    "Longitude",
]

other_cols = [
    col
    for col in df.columns
    if col not in priority_cols
]

df = df[
    priority_cols + other_cols
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

matched = df["Latitude"].notna().sum()

missing = df["Latitude"].isna().sum()

print("\n====================================")
print("GEOCODING COMPLETE")
print("====================================")

print(f"\nMatched districts: {matched}")

print(f"Missing districts: {missing}")

print(f"\nSaved output:")
print(OUTPUT_CSV)

print("\nPreview:")
print(df.head())
