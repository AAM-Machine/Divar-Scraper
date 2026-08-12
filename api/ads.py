from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from core.database import DivarAd, SessionLocal


# مدل داده برای API
class DivarAdSchema(BaseModel):
    id: int
    title: str | None = None
    date: str | None = None
    meter: str | None = None
    year: str | None = None
    room: str | None = None
    total_price: str | None = None
    meter_price: str | None = None
    floor: str | None = None
    amenities: str | None = None
    description: str | None = None
    location: str | None = None
    images: str | None = None
    link: str

    class Config:
        from_attributes = True


# ایجاد router برای آگهی‌ها
router = APIRouter()


# دریافت session دیتابیس
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# دریافت همه آگهی‌ها
@router.get("/ads/", response_model=List[DivarAdSchema])
def get_ads(db: Session = Depends(get_db)):
    return db.query(DivarAd).all()


# دریافت یک آگهی بر اساس id
@router.get("/ads/{ad_id}", response_model=DivarAdSchema)
def get_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = db.query(DivarAd).filter(DivarAd.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad
