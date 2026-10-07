from datetime import datetime
from app.database import SessionLocal
from app.models.farm import MarketCache

import random
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------
# Government MSP baselines (Rs/quintal)
# ---------------------------------------------------

BASE_PRICES = {
    "Rice": 2183,
    "Wheat": 2275,
    "Maize": 1870,
    "Sorghum": 3180,
    "Pearl Millet": 2500,
    "Barley": 1735,
    "Chickpea": 5440,
    "Kidneybeans": 6000,
    "Pigeonpea": 7000,
    "Blackgram": 7400,
    "Mungbean": 8558,
    "Lentil": 6000,
    "Mothbeans": 5500,
    "Soyabean": 4300,
    "Groundnut": 6377,
    "Sunflower": 6400,
    "Sesame": 8635,
    "Mustard": 5650,
    "Cotton": 6620,
    "Sugarcane": 340,
    "Jute": 5050,
    "Coffee": 12000,
}

# ---------------------------------------------------
# data.gov.in API KEY
# ---------------------------------------------------

API_KEY = os.getenv("MARKET_API_KEY")

# ---------------------------------------------------
# LIVE FETCH
# ---------------------------------------------------

async def fetch_live_price(crop_name: str):

    try:

        url = (
            "https://api.data.gov.in/resource/"
            "9ef84268-d588-465a-a308-a864a43d0070"
        )

        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": 1,
            "filters[commodity]": crop_name,
        }

        async with httpx.AsyncClient(timeout=10) as client:

            response = await client.get(
                url,
                params=params
            )

        data = response.json()

        records = data.get("records", [])

        if not records:
            return None

        record = records[0]

        modal_price = record.get("modal_price")

        if not modal_price:
            return None

        return {
            "price": float(modal_price),
            "source": "Agmarknet",
            "trend": random.choice([
                "up",
                "down",
                "stable"
            ]),
        }

    except Exception as e:

        print(f"Live fetch failed for {crop_name}: {e}")

        return None

# ---------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------

async def get_market_prices(crop_names: list[str]) -> dict:
    """
    Returns today's cached prices.
    If today's price does not exist:
        -> fetch from live API
        -> fallback to MSP simulation
    """

    results = {}

    db = SessionLocal()

    today = datetime.utcnow().date()

    try:

        for name in crop_names:

            # ---------------------------------------------------
            # CHECK TODAY CACHE
            # ---------------------------------------------------

            cached = (
                db.query(MarketCache)
                .filter(
                    MarketCache.crop_name == name,
                    MarketCache.fetched_at >= datetime.combine(
                        today,
                        datetime.min.time()
                    )
                )
                .first()
            )

            # ---------------------------------------------------
            # RETURN CACHE
            # ---------------------------------------------------

            if cached:

                results[name] = {
                    "price": cached.price,
                    "unit": cached.unit,
                    "source": cached.source,
                    "updated": cached.fetched_at.isoformat(),
                    "cached": True,
                }

            # ---------------------------------------------------
            # FETCH NEW DATA
            # ---------------------------------------------------

            else:

                live_data = await fetch_live_price(name)

                # ---------------------------------------------------
                # LIVE PRICE SUCCESS
                # ---------------------------------------------------

                if live_data:

                    price = live_data["price"]
                    source = live_data["source"]
                    trend = live_data["trend"]

                # ---------------------------------------------------
                # FALLBACK MSP SIMULATION
                # ---------------------------------------------------

                else:

                    base = BASE_PRICES.get(name, 3000)

                    price = round(
                        base * random.uniform(0.95, 1.05),
                        2
                    )

                    source = "MSP baseline"

                    trend = random.choice([
                        "up",
                        "down",
                        "stable"
                    ])

                # ---------------------------------------------------
                # UPSERT CACHE
                # ---------------------------------------------------

                entry = (
                    db.query(MarketCache)
                    .filter(MarketCache.crop_name == name)
                    .first()
                )

                if entry:

                    entry.price = price
                    entry.source = source
                    entry.fetched_at = datetime.utcnow()

                else:

                    entry = MarketCache(
                        crop_name=name,
                        price=price,
                        source=source,
                    )

                    db.add(entry)

                db.commit()

                results[name] = {
                    "price": price,
                    "unit": "Rs/quintal",
                    "source": source,
                    "trend": trend,
                    "updated": datetime.utcnow().isoformat(),
                    "cached": False,
                }

    finally:

        db.close()

    return results