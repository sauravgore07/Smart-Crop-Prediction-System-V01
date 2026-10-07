from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

from app.services.market_service import get_market_prices

router = APIRouter()

# =====================================================
# LOAD DATA
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MANDI_CSV = BASE_DIR / "data" / "mandis_with_coordinates.csv"

try:

    mandi_df = pd.read_csv(MANDI_CSV)

    print(f"Loaded mandis: {len(mandi_df)}")

except Exception as e:

    print(f"Market Info Load Error: {e}")

    mandi_df = pd.DataFrame()

# =====================================================
# HAVERSINE DISTANCE (KM)
# =====================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))

    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c

# =====================================================
# FIND NEAREST MARKETS
# =====================================================

def get_nearest_markets(
    latitude,
    longitude,
    limit=5
):

    if mandi_df.empty:
        return []

    df = mandi_df.copy()

    df = df.dropna(
        subset=[
            "Latitude",
            "Longitude"
        ]
    )

    if len(df) == 0:
        return []

    df["distance"] = df.apply(

        lambda row: calculate_distance(

            latitude,
            longitude,

            row["Latitude"],
            row["Longitude"]

        ),

        axis=1
    )

    nearest = (

    df.sort_values(
        "distance"
    )

    .head(limit)
)

    print("\n=== NEAREST MARKETS DEBUG ===")

    for _, row in nearest.iterrows():

        print(
            "Market:", row["Market"],
            "| District:", row["District"],
            "| Lat:", row["Latitude"],
            "| Lon:", row["Longitude"],
            "| Distance:", row["distance"]
        )


    markets = []

    for _, row in nearest.iterrows():

        markets.append({

            "market":
                str(row["Market"]),

            "district":
                str(row["District"]),

            "state":
                str(row["State"]),

            "distance":
                round(
                    float(row["distance"]),
                    2
                )

        })

    return markets

# =====================================================
# API
# =====================================================

@router.post("/info")
async def get_market_info(
    data: dict
):

    try:

        crop = data.get("crop")

        latitude = float(
            data.get("latitude")
        )

        longitude = float(
            data.get("longitude")
        )

        if not crop:

            raise HTTPException(

                status_code=400,

                detail="Crop required"
            )

        # -----------------------------------------
        # NEAREST MARKETS
        # -----------------------------------------

        nearest_markets = get_nearest_markets(

            latitude,

            longitude,

            limit=5
        )
        
        # -----------------------------------------
        # PRICE
        # -----------------------------------------

        prices = await get_market_prices(
            [crop]
        )

        price_info = prices.get(
            crop,
            {}
        )

        return {

            "crop":
                crop,

            "nearest_markets":
                nearest_markets,

            "market_count":
                len(nearest_markets),

            "price":
                price_info.get(
                    "price",
                    0
                ),

            "unit":
                price_info.get(
                    "unit",
                    "Rs/quintal"
                ),

            "trend":
                price_info.get(
                    "trend",
                    "stable"
                ),

            "source":
                price_info.get(
                    "source",
                    "Unknown"
                ),

            "updated":
                price_info.get(
                    "updated"
                )
        }

    except Exception as e:

        print(
            f"Market Info Error: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )