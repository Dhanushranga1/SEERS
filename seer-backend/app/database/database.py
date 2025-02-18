from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

DATABASE_URL = settings.DATABASE_URL

# Create Database Engine
engine = create_engine(DATABASE_URL)

# Create Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Metadata and Base
metadata = MetaData()
Base = declarative_base()  # ✅ This is the missing part
