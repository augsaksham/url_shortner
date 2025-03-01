from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    short_code = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    access_count = Column(Integer, default=0)

    user = relationship("User", back_populates="urls")

# Create indexes for performance
Index("idx_short_code", URL.short_code)
Index("idx_original_url", URL.original_url)

# Add back-reference to User model
from .user import User
User.urls = relationship("URL", back_populates="user")