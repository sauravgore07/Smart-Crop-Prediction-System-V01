import httpx

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
DAYS_IN_MONTH = {
    "JAN": 31, "FEB": 28, "MAR": 31, "APR": 30, "MAY": 31, "JUN": 30,
    "JUL": 31, "AUG": 31, "SEP": 30, "OCT": 31, "NOV": 30, "DEC": 31
}

async def fetch_nasa_climate(lat: float, lng: float) -> dict:
    """
    Fetches 30-year historical rainfall averages from NASA POWER API.
    Returns annual total (mm) and the 3 rainiest months.
    """
    url = (
        f"https://power.larc.nasa.gov/api/temporal/climatology/point"
        f"?parameters=PRECTOTCORR&community=AG"
        f"&longitude={lng}&latitude={lat}&format=JSON&start=2000&end=2020"
    )
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return _parse_nasa_response(data)
    except Exception:
        return _regional_fallback(lat, lng)


def _parse_nasa_response(payload: dict) -> dict:
    params = payload.get("properties", {}).get("parameter", {})
    prectot = params.get("PRECTOTCORR", {})

    monthly_totals = []
    for m in MONTHS:
        raw = prectot.get(m, 0)
        if isinstance(raw, dict):
            raw = raw.get("mean", raw.get("value", 0))
        mean_per_day = float(raw or 0)
        monthly_mm = mean_per_day * DAYS_IN_MONTH[m]
        monthly_totals.append({"month": m, "mm": round(monthly_mm, 1)})

    annual_mm = sum(x["mm"] for x in monthly_totals)

    rainy_months = sorted(monthly_totals, key=lambda x: x["mm"], reverse=True)[:3]
    rainy_month_names = [x["month"] for x in rainy_months]

    return {
        "annualRainfall": round(annual_mm),
        "rainyMonths": rainy_month_names,
        "monthlyData": monthly_totals,
        "source": "NASA POWER API",
    }


def _regional_fallback(lat: float, lng: float) -> dict:
    """India regional rainfall estimates when NASA API is unreachable."""
    if lng < 75:
        pattern = {"annual": 500, "rainy": ["JUL", "AUG"]}
    elif lng > 88:
        pattern = {"annual": 1800, "rainy": ["JUN", "JUL", "AUG"]}
    elif lat < 15:
        pattern = {"annual": 1200, "rainy": ["JUN", "JUL", "OCT"]}
    elif lat > 28:
        pattern = {"annual": 800, "rainy": ["JUL", "AUG", "SEP"]}
    else:
        pattern = {"annual": 1000, "rainy": ["JUN", "JUL", "AUG"]}

    return {
        "annualRainfall": pattern["annual"],
        "rainyMonths": pattern["rainy"],
        "monthlyData": [],
        "source": "Regional estimate (NASA API unavailable)",
    }
