"""
User management schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    household_id: Optional[UUID] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for user updates"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None


class UserProfileResponse(BaseModel):
    """User profile response schema"""
    id: UUID
    user_id: UUID
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    dietary_tags: List[str] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    feature_toggles: Dict[str, bool] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update schema"""
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    dietary_tags: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None
    feature_toggles: Optional[Dict[str, bool]] = None


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    household_id: Optional[UUID] = None
    is_active: bool
    is_premium: bool
    profile: Optional[UserProfileResponse] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HouseholdCreate(BaseModel):
    """Household creation schema"""
    name: str = Field(..., min_length=1, max_length=100)


class HouseholdUpdate(BaseModel):
    """Household update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class HouseholdResponse(BaseModel):
    """Household response schema"""
    id: UUID
    name: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    household_id: Optional[UUID] = None
    

class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str