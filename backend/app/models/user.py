from sqlalchemy import Column, String, Boolean, DateTime, JSON
from app.models.base import BaseModel
from datetime import datetime

class User(BaseModel):
    """사용자 모델"""
    __tablename__ = "users"
    
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # Additional user info
    phone = Column(String)
    address = Column(String)
    company = Column(String)
    
    # Preferences
    preferences = Column(JSON)  # Store user preferences as JSON
