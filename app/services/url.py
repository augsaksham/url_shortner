import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import redis.asyncio as redis
from .. import models, schemas
from ..config import settings

# Generate a random short code
def generate_short_code(length=settings.SHORT_URL_LENGTH):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Create a new shortened URL
async def create_short_url(
    db: Session, 
    redis_client: redis.Redis, 
    url_data: schemas.URLCreate, 
    user_id: int
):
    # Check if the URL already exists for this user
    existing_url = db.query(models.URL).filter(
        models.URL.original_url == url_data.original_url,
        models.URL.user_id == user_id,
        models.URL.expires_at > datetime.utcnow()
    ).first()
    
    if existing_url:
        # URL already exists, return the existing short URL
        short_url = f"{settings.BASE_URL}/{existing_url.short_code}"
        return schemas.URLResponse(
            original_url=existing_url.original_url,
            short_url=short_url,
            expires_at=existing_url.expires_at,
            created_at=existing_url.created_at,
            access_count=existing_url.access_count
        )
    
    # Generate a unique short code
    while True:
        short_code = generate_short_code()
        # Check if the short code already exists in the database
        exists_in_db = db.query(models.URL).filter(models.URL.short_code == short_code).first()
        # Check if the short code already exists in Redis
        exists_in_redis = await redis_client.exists(f"short_url:{short_code}")
        
        if not exists_in_db and not exists_in_redis:
            break
    
    # Calculate expiration date
    expires_at = datetime.utcnow() + timedelta(days=url_data.expires_in_days)
    
    # Create a new URL record in the database
    db_url = models.URL(
        original_url=url_data.original_url,
        short_code=short_code,
        user_id=user_id,
        expires_at=expires_at,
        access_count=0
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    # Store the URL mapping in Redis
    # Set TTL to match expiration date (in seconds)
    ttl = int((expires_at - datetime.utcnow()).total_seconds())
    await redis_client.set(f"short_url:{short_code}", url_data.original_url, ex=ttl)
    
    # Create the full short URL
    short_url = f"{settings.BASE_URL}/{short_code}"
    
    return schemas.URLResponse(
        original_url=db_url.original_url,
        short_url=short_url,
        expires_at=db_url.expires_at,
        created_at=db_url.created_at,
        access_count=db_url.access_count
    )

# Get the original URL from a short code
async def get_original_url(db: Session, redis_client: redis.Redis, short_code: str):
    # Try to get the URL from Redis first
    original_url = await redis_client.get(f"short_url:{short_code}")
    
    if not original_url:
        # If not in Redis, get it from the database
        db_url = db.query(models.URL).filter(
            models.URL.short_code == short_code,
            models.URL.expires_at > datetime.utcnow()
        ).first()
        
        if not db_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL not found or expired"
            )
        
        original_url = db_url.original_url
        
        # Update the cache
        ttl = int((db_url.expires_at - datetime.utcnow()).total_seconds())
        await redis_client.set(f"short_url:{short_code}", original_url, ex=ttl)
    
    # Increment access count in database asynchronously
    db_url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if db_url:
        db_url.access_count += 1
        db.commit()
    
    # Increment access count in Redis
    await redis_client.incr(f"access_count:{short_code}")
    
    return original_url

# Get URL information
async def get_url_info(db: Session, redis_client: redis.Redis, short_code: str, user_id: int):
    # Get URL from database
    db_url = db.query(models.URL).filter(
        models.URL.short_code == short_code,
        models.URL.user_id == user_id
    ).first()
    
    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found or you don't have permission to access it"
        )
    
    # Check if access count is in Redis
    access_count = await redis_client.get(f"access_count:{short_code}")
    if access_count:
        # Use Redis count if available (more up-to-date)
        db_url.access_count = int(access_count)
    
    # Create the full short URL
    short_url = f"{settings.BASE_URL}/{short_code}"
    
    return schemas.URLInfo(
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=short_url,
        expires_at=db_url.expires_at,
        created_at=db_url.created_at,
        access_count=db_url.access_count
    )

# Get all URLs for a user
def get_user_urls(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    db_urls = db.query(models.URL).filter(models.URL.user_id == user_id).offset(skip).limit(limit).all()
    # Convert db_urls to schemas.URLInfo
    url_infos = []
    for db_url in db_urls:
        short_url = f"{settings.BASE_URL}/{db_url.short_code}"
        url_info = schemas.URLInfo(
            original_url=db_url.original_url,
            short_code=db_url.short_code,
            short_url=short_url,
            expires_at=db_url.expires_at,
            created_at=db_url.created_at,
            access_count=db_url.access_count
        )
        url_infos.append(url_info)
    
    return url_infos