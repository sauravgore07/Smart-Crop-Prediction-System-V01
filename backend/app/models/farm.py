from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Farm(Base):
    __tablename__ = "farms"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    owner_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    lat           = Column(Float, nullable=False)
    lng           = Column(Float, nullable=False)
    location_name = Column(String, default="")
    soil_type     = Column(String, default="Loamy")
    soil_ph       = Column(Float, default=6.5)
    land_area     = Column(Float, default=2.0)
    season        = Column(String, default="Kharif")
    saved_crops   = Column(JSON, default=list)   # crop rotation history
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="farms")


class MarketCache(Base):
    __tablename__ = "market_cache"

    id         = Column(Integer, primary_key=True)
    crop_name  = Column(String, unique=True, index=True)
    price      = Column(Float)
    unit       = Column(String, default="Rs/quintal")
    source     = Column(String, default="MSP baseline")
    fetched_at = Column(DateTime, default=datetime.utcnow)
