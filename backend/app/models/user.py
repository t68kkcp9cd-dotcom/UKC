"""
User management models
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class Household(BaseModel):
    """Household for multi-user support"""
    
    __tablename__ = "households"
    
    name = Column(String(100), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="owned_household")
    users = relationship("User", back_populates="household")
    inventory_items = relationship("InventoryItem", back_populates="household")
    meal_plans = relationship("MealPlan", back_populates="household")
    shopping_lists = relationship("ShoppingList", back_populates="household")


class User(BaseModel):
    """Application user"""
    
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    household = relationship("Household", back_populates="users")
    owned_household = relationship("Household", back_populates="owner")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="added_by_user")
    recipes = relationship("Recipe", back_populates="created_by_user")
    meal_plans = relationship("MealPlan", back_populates="created_by_user")
    shopping_lists = relationship("ShoppingList", back_populates="created_by_user")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class UserProfile(BaseModel):
    """Extended user profile with preferences"""
    
    __tablename__ = "user_profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    display_name = Column(String(100))
    avatar_url = Column(String(500))
    
    # JSON fields for flexibility
    dietary_tags = Column(JSONB, default=list, nullable=False)  # vegan, gluten-free, etc.
    allergens = Column(JSONB, default=list, nullable=False)
    preferences = Column(JSONB, default=dict, nullable=False)  # app preferences
    feature_toggles = Column(JSONB, default=dict, nullable=False)  # premium features
    
    # Relationships
    user = relationship("User", back_populates="profile")


class UserSession(BaseModel):
    """User session management for JWT"""
    
    __tablename__ = "user_sessions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")