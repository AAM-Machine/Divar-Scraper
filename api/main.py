from fastapi import FastAPI
from api.ads import router as ads_router
from core.database import init_db

# ایجاد اپلیکیشن FastAPI
app = FastAPI(
    title="Divar Ads API",
    description="API to access scraped Divar ads.",
    version="1.0.0",
)

# مقداردهی دیتابیس با env
init_db()

# ثبت router آگهی‌ها
app.include_router(ads_router)
