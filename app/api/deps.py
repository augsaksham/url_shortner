from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import redis.asyncio as redis
from jose import JWTError, jwt
from ..database import get_db
from ..redis import get_redis_connection
from ..config import settings
from .. import models, schemas
from ..services.auth import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_active_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    return get_current_user(db, token)