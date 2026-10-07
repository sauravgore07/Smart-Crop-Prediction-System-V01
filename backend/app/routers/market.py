from fastapi import APIRouter
from app.services.market_service import get_market_prices

router = APIRouter()

@router.get("/prices")
async def market_prices(crops: str = ""):
    """
    Returns current market prices for given crop names (comma-separated).
    Example: /api/market/prices?crops=Rice,Wheat,Cotton
    Prices served from cache (24h TTL) or regenerated from MSP baselines.
    """
    crop_list = [c.strip() for c in crops.split(",") if c.strip()]
    if not crop_list:
        # Return all crops if none specified
        from app.services.market_service import BASE_PRICES
        crop_list = list(BASE_PRICES.keys())
    return await get_market_prices(crop_list)
