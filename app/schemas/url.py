from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional
from datetime import datetime, timedelta
from ..config import settings

class URLBase(BaseModel):
    original_url: str
    
    @validator('original_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            return f"https://{v}"
        return v

class URLCreate(URLBase):
    expires_in_days: Optional[int] = Field(default=settings.DEFAULT_URL_EXPIRY_DAYS, ge=1, le=365)

class URLResponse(BaseModel):
    original_url: str
    short_url: str
    expires_at: datetime
    created_at: datetime
    access_count: int = 0

    class Config:
        from_attributes = True

class URLInfo(BaseModel):
    original_url: str
    short_code: str
    short_url: str
    expires_at: datetime
    created_at: datetime
    access_count: int

    class Config:
        from_attributes = True