from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, Base

from app.routers import (
    auth,
    crops,
    farms,
    weather,
    market,
    rotation,
    market_info
)


# Auto-create all SQLite tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CropPredict API",
    description="Smart crop recommendation API with ML predictions and market prices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,    prefix="/api/auth",    tags=["Auth"])
app.include_router(crops.router,   prefix="/api/crops",   tags=["Crops"])
app.include_router(farms.router,   prefix="/api/farms",   tags=["Farms"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(market.router,  prefix="/api/market",  tags=["Market"])
app.include_router(rotation.router,prefix="/rotation",tags=["Rotation"])
app.include_router(market_info.router,prefix="/api/market_info",tags=["Market_Info"])


@app.get("/")
def root():
    return {"message": "CropPredict API is running", "docs": "/docs"}
