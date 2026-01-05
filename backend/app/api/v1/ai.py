"""
AI-powered endpoints for recipe generation, meal planning, and smart suggestions
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.ai import (
    RecipeGenerationRequest, RecipeGenerationResponse,
    MealPlanGenerationRequest, MealPlanGenerationResponse,
    AISuggestionResponse, AIChatRequest, AIChatResponse
)
from app.services.ai_service import AIService
from app.services.inventory_service import InventoryService
from app.api.v1.auth import get_current_user
from app.config import settings

router = APIRouter()


@router.post("/generate-recipe", response_model=RecipeGenerationResponse)
async def generate_recipe(
    request: RecipeGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService)
):
    """Generate a recipe from available ingredients"""
    try:
        # Check if user has premium features
        if not current_user.is_premium and settings.ENABLE_AI_FEATURES:
            # For free users, limit AI usage
            # In production, implement usage tracking here
            pass
            
        recipe = await ai_service.generate_recipe_from_ingredients(
            ingredients=request.ingredients,
            dietary_restrictions=request.dietary_restrictions,
            cuisine_type=request.cuisine_type,
            difficulty=request.difficulty,
            user=current_user
        )
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate recipe"
            )
            
        return RecipeGenerationResponse(
            success=True,
            recipe=recipe,
            message="Recipe generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recipe generation failed: {str(e)}"
        )


@router.get("/suggest-recipes", response_model=List[AISuggestionResponse])
async def suggest_recipes(
    max_suggestions: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService)
):
    """Suggest recipes based on user's current inventory"""
    try:
        suggestions = await ai_service.suggest_recipes_from_inventory(
            db=db,
            user=current_user,
            max_recipes=max_suggestions
        )
        
        return [
            AISuggestionResponse(
                title=suggestion["title"],
                description=suggestion["description"],
                confidence_score=suggestion.get("match_percentage", 0),
                metadata=suggestion
            )
            for suggestion in suggestions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recipe suggestions failed: {str(e)}"
        )


@router.post("/generate-meal-plan", response_model=MealPlanGenerationResponse)
async def generate_meal_plan(
    request: MealPlanGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService)
):
    """Generate a meal plan for specified days"""
    try:
        # Premium feature check
        if not current_user.is_premium:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Meal plan generation is a premium feature"
            )
            
        meal_plan = await ai_service.generate_meal_plan(
            db=db,
            user=current_user,
            days=request.days,
            dietary_preferences=request.dietary_preferences,
            budget_range=request.budget_range
        )
        
        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate meal plan"
            )
            
        return MealPlanGenerationResponse(
            success=True,
            meal_plan=meal_plan,
            message=f"Generated {request.days}-day meal plan"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meal plan generation failed: {str(e)}"
        )


@router.get("/waste-reduction-tips", response_model=List[str])
async def get_waste_reduction_tips(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService)
):
    """Get personalized waste reduction tips"""
    try:
        tips = await ai_service.get_waste_reduction_tips(
            db=db,
            user=current_user
        )
        
        return tips
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get waste reduction tips: {str(e)}"
        )


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService)
):
    """General cooking and kitchen Q&A chat"""
    try:
        # Rate limiting for chat (basic implementation)
        if not current_user.is_premium:
            # Free users get limited chat
            pass
            
        response = await ai_service.chat_about_cooking(
            message=request.message,
            conversation_history=request.conversation_history
        )
        
        return AIChatResponse(
            response=response,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.get("/models", response_model=Dict[str, Any])
async def get_ai_models(
    current_user: User = Depends(get_current_user)
):
    """Get information about available AI models"""
    return {
        "chat_model": settings.OLLAMA_CHAT_MODEL,
        "recipe_model": settings.OLLAMA_RECIPE_MODEL,
        "ai_enabled": settings.ENABLE_AI_FEATURES,
        "premium_features": {
            "advanced_recipes": True,
            "meal_planning": True,
            "unlimited_chat": True
        }
    }