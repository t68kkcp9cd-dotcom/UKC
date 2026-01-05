"""
Recipe management schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, validator


class RecipeIngredientBase(BaseModel):
    """Base recipe ingredient schema"""
    name: str = Field(..., min_length=1, max_length=255)
    quantity: str = Field(..., max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    is_optional: bool = False


class RecipeIngredientCreate(RecipeIngredientBase):
    """Recipe ingredient creation schema"""
    pass


class RecipeIngredientResponse(RecipeIngredientBase):
    """Recipe ingredient response schema"""
    id: UUID
    recipe_id: UUID
    
    class Config:
        from_attributes = True


class RecipeStepBase(BaseModel):
    """Base recipe step schema"""
    step_number: int = Field(..., ge=1)
    instruction: str = Field(..., min_length=1, max_length=2000)
    duration: Optional[int] = Field(None, ge=0, description="Duration in minutes")
    temperature: Optional[str] = Field(None, max_length=20)
    equipment: Optional[List[str]] = Field(default_factory=list)


class RecipeStepCreate(RecipeStepBase):
    """Recipe step creation schema"""
    pass


class RecipeStepResponse(RecipeStepBase):
    """Recipe step response schema"""
    id: UUID
    recipe_id: UUID
    
    class Config:
        from_attributes = True


class RecipeReviewBase(BaseModel):
    """Base recipe review schema"""
    rating: float = Field(..., ge=0, le=5, description="Rating out of 5")
    comment: Optional[str] = Field(None, max_length=2000)
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 0 or v > 5:
            raise ValueError('Rating must be between 0 and 5')
        return v


class RecipeReviewCreate(RecipeReviewBase):
    """Recipe review creation schema"""
    pass


class RecipeReviewResponse(RecipeReviewBase):
    """Recipe review response schema"""
    id: UUID
    recipe_id: UUID
    user_id: UUID
    user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NutritionInfo(BaseModel):
    """Nutrition information schema"""
    calories: Optional[Decimal] = None
    protein: Optional[Decimal] = None
    carbs: Optional[Decimal] = None
    fat: Optional[Decimal] = None
    fiber: Optional[Decimal] = None
    sodium: Optional[Decimal] = None
    sugar: Optional[Decimal] = None


class RecipeBase(BaseModel):
    """Base recipe schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: str = Field(..., max_length=100)
    cuisine_type: Optional[str] = Field(None, max_length=50)
    prep_time: int = Field(..., ge=0, description="Preparation time in minutes")
    cook_time: int = Field(..., ge=0, description="Cooking time in minutes")
    total_time: Optional[int] = Field(None, ge=0, description="Total time in minutes")
    servings: int = Field(..., ge=1, description="Number of servings")
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")
    is_public: bool = Field(False, description="Whether recipe is publicly visible")
    tags: List[str] = Field(default_factory=list)
    nutrition_info: Optional[NutritionInfo] = None
    image_url: Optional[str] = Field(None, max_length=500)
    source_url: Optional[str] = Field(None, max_length=500)
    tips: List[str] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)
    dietary_tags: List[str] = Field(default_factory=list)
    equipment_needed: List[str] = Field(default_factory=list)
    
    @validator('total_time', pre=True, always=True)
    def calculate_total_time(cls, v, values):
        if v is None:
            prep = values.get('prep_time', 0)
            cook = values.get('cook_time', 0)
            return prep + cook
        return v


class RecipeCreate(RecipeBase):
    """Recipe creation schema"""
    ingredients: List[RecipeIngredientCreate] = Field(default_factory=list)
    steps: List[RecipeStepCreate] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    """Recipe update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    cuisine_type: Optional[str] = Field(None, max_length=50)
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = Field(None, regex="^(easy|medium|hard)$")
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    nutrition_info: Optional[NutritionInfo] = None
    image_url: Optional[str] = Field(None, max_length=500)
    tips: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    dietary_tags: Optional[List[str]] = None
    equipment_needed: Optional[List[str]] = None
    ingredients: Optional[List[RecipeIngredientCreate]] = None
    steps: Optional[List[RecipeStepCreate]] = None


class RecipeResponse(RecipeBase):
    """Recipe response schema"""
    id: UUID
    created_by: UUID
    household_id: UUID
    avg_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_count: int = 0
    ingredients: List[RecipeIngredientResponse] = Field(default_factory=list)
    steps: List[RecipeStepResponse] = Field(default_factory=list)
    reviews: List[RecipeReviewResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RecipeSearchResponse(BaseModel):
    """Recipe search suggestions response"""
    query: str
    suggestions: List[str]
    total_results: Optional[int] = None


class RecipeImportRequest(BaseModel):
    """Recipe import request"""
    url: str = Field(..., description="URL to import recipe from")
    auto_categorize: bool = Field(True, description="Auto-categorize imported recipe")
    

class RecipeImportResponse(BaseModel):
    """Recipe import response"""
    success: bool
    recipe: Optional[RecipeCreate] = None
    source_url: str
    message: str
    import_warnings: List[str] = Field(default_factory=list)