"""
Meal planning schemas
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MealPlanEntryBase(BaseModel):
    """Base meal plan entry schema"""
    date: date
    meal_type: str = Field(..., regex="^(breakfast|lunch|dinner|snack)$")
    recipe_name: str = Field(..., min_length=1, max_length=255)
    recipe_id: Optional[UUID] = None
    servings: int = Field(1, ge=1)
    estimated_prep_time: Optional[int] = Field(None, ge=0, description="Estimated prep time in minutes")
    notes: Optional[str] = Field(None, max_length=1000)
    is_completed: bool = False


class MealPlanEntryCreate(MealPlanEntryBase):
    """Meal plan entry creation schema"""
    pass


class MealPlanEntryResponse(MealPlanEntryBase):
    """Meal plan entry response schema"""
    id: UUID
    meal_plan_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MealPlanBase(BaseModel):
    """Base meal plan schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: date
    end_date: date
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True


class MealPlanCreate(MealPlanBase):
    """Meal plan creation schema"""
    entries: List[MealPlanEntryCreate] = Field(default_factory=list)


class MealPlanUpdate(BaseModel):
    """Meal plan update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class MealPlanResponse(MealPlanBase):
    """Meal plan response schema"""
    id: UUID
    created_by: UUID
    household_id: UUID
    entries: List[MealPlanEntryResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True