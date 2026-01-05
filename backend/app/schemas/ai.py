"""
AI-related schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.recipe import RecipeCreate
from app.schemas.meal_plan import MealPlanCreate


class RecipeGenerationRequest(BaseModel):
    """Request schema for recipe generation"""
    ingredients: List[str] = Field(..., min_items=1, description="Available ingredients")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary restrictions")
    cuisine_type: Optional[str] = Field(None, description="Preferred cuisine type")
    difficulty: Optional[str] = Field(None, description="Recipe difficulty level")
    servings: Optional[int] = Field(4, ge=1, description="Number of servings")


class RecipeGenerationResponse(BaseModel):
    """Response schema for recipe generation"""
    success: bool
    recipe: Optional[RecipeCreate] = None
    message: str
    estimated_cost: Optional[float] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)


class AISuggestionResponse(BaseModel):
    """AI suggestion response"""
    title: str
    description: str
    confidence_score: float = Field(..., ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


class MealPlanGenerationRequest(BaseModel):
    """Request schema for meal plan generation"""
    days: int = Field(7, ge=1, le=14, description="Number of days to plan")
    dietary_preferences: Optional[List[str]] = Field(None, description="Dietary preferences")
    budget_range: Optional[str] = Field(None, description="Budget range")
    exclude_cuisines: Optional[List[str]] = Field(None, description="Cuisines to exclude")
    preferred_meal_types: Optional[List[str]] = Field(None, description="Preferred meal types")


class MealPlanGenerationResponse(BaseModel):
    """Response schema for meal plan generation"""
    success: bool
    meal_plan: Optional[MealPlanCreate] = None
    message: str
    estimated_weekly_cost: Optional[float] = None
    nutrition_summary: Optional[Dict[str, float]] = None


class AIChatRequest(BaseModel):
    """AI chat request"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None, description="Previous conversation messages"
    )
    context: Optional[str] = Field(None, description="Additional context")


class AIChatResponse(BaseModel):
    """AI chat response"""
    response: str
    timestamp: datetime
    context_used: Optional[str] = None
    follow_up_suggestions: Optional[List[str]] = None