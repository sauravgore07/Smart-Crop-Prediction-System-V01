from pathlib import Path
import pandas as pd
import requests
import time

# =====================================================
# FILES
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "clean_mandis2.csv"

OUTPUT_FILE = BASE_DIR / "mandis_with_coordinates.csv"
# =====================================================
# LOAD
# =====================================================

if Path(OUTPUT_FILE).exists():
    df = pd.read_csv(OUTPUT_FILE)
    print(f"Resuming existing file: {OUTPUT_FILE}")
else:
    df = pd.read_csv(INPUT_FILE)

    if "Latitude" not in df.columns:
        df["Latitude"] = None

    if "Longitude" not in df.columns:
        df["Longitude"] = None

    print(f"Loaded new file: {INPUT_FILE}")

# =====================================================
# GEOCODER
# =====================================================

HEADERS = {
    "User-Agent": "CropPredict/1.0"
}

def geocode_location(market, district, state):

    queries = [

        f"{market}, {district}, {state}, India",

        f"{market}, {state}, India",

        f"{market}, India"
    ]

    for query in queries:

        try:

            url = "https://nominatim.openstreetmap.org/search"

            params = {
                "q": query,
                "format": "json",
                "limit": 1
            }

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=20
            )

            data = response.json()

            if len(data) > 0:

                return (
                    float(data[0]["lat"]),
                    float(data[0]["lon"])
                )

        except Exception:
            pass

        time.sleep(1)

    return None, None
# =====================================================
# PROCESS
# =====================================================

total = len(df)

for idx, row in df.iterrows():

    # Skip already processed
    if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
        continue

    market = str(row["Market"]).strip()
    district = str(row["District"]).strip()
    state = str(row["State"]).strip()

    query = f"{market}, {district}, {state}, India"

    print(
        f"[{idx+1}/{total}] "
        f"Searching: {query}"
    )

    lat, lon = geocode_location(
    market,
    district,
    state)

    if lat is not None:

        df.at[idx, "Latitude"] = lat
        df.at[idx, "Longitude"] = lon

        print(
            f"Found: {lat}, {lon}"
        )

    else:

        print("Not found")

    # Save after EVERY row
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # Nominatim rate limit
    time.sleep(1)

print("\nDone.")
print(f"Saved -> {OUTPUT_FILE}")