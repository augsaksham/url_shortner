from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import redis.asyncio as redis
from .database import engine, Base, get_db
from .redis import get_redis_connection
from . import models
from .config import settings
from .api.routes import auth, url

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(url.router, prefix=f"{settings.API_V1_STR}/urls", tags=["urls"])

# Root redirect endpoint for short URLs
@app.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_connection)
):
    """
    Redirect to the original URL
    """
    from .services.url import get_original_url
    from fastapi.responses import RedirectResponse
    
    original_url = await get_original_url(db, redis_client, short_code)
    return RedirectResponse(original_url)

@app.get("/")
def read_root():
    return {"message": "Welcome to URL Shortener API"}

# Health check endpoint
@app.get("/health")
async def health_check(redis_client: redis.Redis = Depends(get_redis_connection)):
    # Check Redis connection
    redis_status = await redis_client.ping()
    
    # Check database connection
    db_status = True
    try:
        db = next(get_db())
        db.execute("SELECT 1")
    except Exception:
        db_status = False
    
    return {
        "status": "healthy" if redis_status and db_status else "unhealthy",
        "redis": "connected" if redis_status else "disconnected",
        "database": "connected" if db_status else "disconnected"
    }