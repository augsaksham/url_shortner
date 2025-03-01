from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
import redis.asyncio as redis
from typing import List
from ... import models, schemas
from ...database import get_db
from ...redis import get_redis_connection
from ...services import url
from ..deps import get_current_active_user

router = APIRouter()

@router.post("/shorten", response_model=schemas.URLResponse)
async def create_short_url(
    url_data: schemas.URLCreate,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_connection),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a shortened URL
    """
    return await url.create_short_url(db, redis_client, url_data, current_user.id)

@router.get("/{short_code}", include_in_schema=False)
async def redirect_to_url(
    short_code: str,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_connection)
):
    """
    Redirect to the original URL
    """
    original_url = await url.get_original_url(db, redis_client, short_code)
    return Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": original_url})

@router.get("/info/{short_code}", response_model=schemas.URLInfo)
async def get_url_info(
    short_code: str,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_connection),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get information about a shortened URL
    """
    return await url.get_url_info(db, redis_client, short_code, current_user.id)

@router.get("/urls/me", response_model=List[schemas.URLInfo])
def get_user_urls(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all URLs for the current user
    """
    urls = url.get_user_urls(db, current_user.id, skip, limit)
    return urls