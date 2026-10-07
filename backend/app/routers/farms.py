from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.farm import Farm
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[FarmOut])
def list_farms(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Farm).filter(Farm.owner_id == user.id).all()

@router.post("/", response_model=FarmOut, status_code=201)
def create_farm(
    body: FarmCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    farm = Farm(**body.model_dump(), owner_id=user.id)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm

@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.owner_id == user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm

@router.patch("/{farm_id}", response_model=FarmOut)
def update_farm(
    farm_id: int,
    body: FarmUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.owner_id == user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(farm, field, value)
    db.commit()
    db.refresh(farm)
    return farm

@router.delete("/{farm_id}", status_code=204)
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.owner_id == user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    db.delete(farm)
    db.commit()
