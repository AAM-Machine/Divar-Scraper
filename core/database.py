import os
from sqlalchemy import create_engine, Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# بارگذاری تنظیمات محیطی
load_dotenv()

# اتصال به دیتابیس
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME]):
    raise RuntimeError("All DB_* variables must be set in .env file")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# مدل داده آگهی دیوار
class DivarAd(Base):
    __tablename__ = "divar_ads"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256))
    date = Column(String(64), nullable=True)
    meter = Column(String(32), nullable=True)
    year = Column(String(32), nullable=True)
    room = Column(String(32), nullable=True)
    total_price = Column(String(64), nullable=True)
    meter_price = Column(String(64), nullable=True)
    floor = Column(String(32), nullable=True)
    amenities = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(128), nullable=True)
    images = Column(Text, nullable=True)
    link = Column(String(512), unique=True, nullable=False)
    __table_args__ = (UniqueConstraint("link", name="uq_divar_link"),)


# ایجاد جداول دیتابیس
def init_db():
    Base.metadata.create_all(engine)
