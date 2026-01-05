"""
Pydantic schemas for API request/response models
"""

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserProfileResponse,
    Token, TokenData, HouseholdCreate, HouseholdResponse
)
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    BarcodeLookupResponse, WasteForecastResponse
)
from app.schemas.recipe import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeIngredientResponse,
    RecipeStepResponse, RecipeReviewCreate, RecipeReviewResponse,
    RecipeImportRequest, RecipeAdaptationRequest
)
from app.schemas.meal_plan import (
    MealPlanCreate, MealPlanUpdate, MealPlanResponse,
    MealPlanEntryCreate, MealPlanEntryResponse
)
from app.schemas.shopping import (
    ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse,
    ShoppingListItemCreate, ShoppingListItemResponse,
    StoreResponse, PriceComparisonResponse
)
from app.schemas.ai import (
    AIChatRequest, AIChatResponse, VoiceCommandResponse,
    RecipeSuggestionRequest, RecipeAdaptationResponse
)

__all__ = [
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserProfileResponse",
    "Token",
    "TokenData",
    "HouseholdCreate",
    "HouseholdResponse",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItemResponse",
    "BarcodeLookupResponse",
    "WasteForecastResponse",
    "RecipeCreate",
    "RecipeUpdate",
    "RecipeResponse",
    "RecipeIngredientResponse",
    "RecipeStepResponse",
    "RecipeReviewCreate",
    "RecipeReviewResponse",
    "RecipeImportRequest",
    "RecipeAdaptationRequest",
    "MealPlanCreate",
    "MealPlanUpdate",
    "MealPlanResponse",
    "MealPlanEntryCreate",
    "MealPlanEntryResponse",
    "ShoppingListCreate",
    "ShoppingListUpdate",
    "ShoppingListResponse",
    "ShoppingListItemCreate",
    "ShoppingListItemResponse",
    "StoreResponse",
    "PriceComparisonResponse",
    "AIChatRequest",
    "AIChatResponse",
    "VoiceCommandResponse",
    "RecipeSuggestionRequest",
    "RecipeAdaptationResponse"
]