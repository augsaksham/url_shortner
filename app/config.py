from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "URL Shortener"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/url_shortener")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "3d2c5de5f3b8a9e93cb9bc88f4ebc490a2fba5dcf1c4a4a6b2592c158b6f8622")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # URL Shortener
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    SHORT_URL_LENGTH: int = 7
    DEFAULT_URL_EXPIRY_DAYS: int = 7

settings = Settings()