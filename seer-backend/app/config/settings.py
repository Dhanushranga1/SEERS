import os
from pathlib import Path
from dotenv import load_dotenv

# Get absolute path of the backend folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file from the backend root directory
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Add SECRET_KEY
    ALGORITHM = os.getenv("ALGORITHM", "HS256")  # JWT Algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # Token expiry in minutes

    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL is not set! Check your .env file.")

settings = Settings()
