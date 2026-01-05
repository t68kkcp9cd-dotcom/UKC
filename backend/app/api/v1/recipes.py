"""
Recipe management endpoints
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.recipe import Recipe, RecipeIngredient, RecipeStep, RecipeReview
from app.models.user import User
from app.schemas.recipe import (
    RecipeCreate, RecipeUpdate, RecipeResponse,
    RecipeIngredientCreate, RecipeStepCreate, RecipeReviewCreate,
    RecipeSearchResponse, RecipeImportRequest, RecipeImportResponse
)
from app.services.ai_service import AIService
from app.services.audit_service import AuditService
from app.api.v1.auth import get_current_user
from app.config import settings

router = APIRouter()


@router.get("/", response_model=List[RecipeResponse])
async def get_recipes(
    search: Optional[str] = Query(None, description="Search in title and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    cuisine_type: Optional[str] = Query(None, description="Filter by cuisine type"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    prep_time_max: Optional[int] = Query(None, description="Maximum prep time in minutes"),
    cook_time_max: Optional[int] = Query(None, description="Maximum cook time in minutes"),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    is_public: Optional[bool] = Query(None, description="Filter by visibility"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recipes with filtering and search"""
    query = select(Recipe).options(
        selectinload(Recipe.ingredients),
        selectinload(Recipe.steps),
        selectinload(Recipe.reviews)
    ).where(
        or_(
            Recipe.created_by == current_user.id,
            Recipe.is_public == True,
            Recipe.household_id == current_user.household_id
        )
    )
    
    # Apply filters
    if search:
        query = query.where(
            or_(
                Recipe.title.ilike(f"%{search}%"),
                Recipe.description.ilike(f"%{search}%")
            )
        )
    
    if category:
        query = query.where(Recipe.category == category)
    
    if cuisine_type:
        query = query.where(Recipe.cuisine_type == cuisine_type)
    
    if difficulty:
        query = query.where(Recipe.difficulty == difficulty)
    
    if prep_time_max:
        query = query.where(Recipe.prep_time <= prep_time_max)
    
    if cook_time_max:
        query = query.where(Recipe.cook_time <= cook_time_max)
    
    if rating_min:
        query = query.where(Recipe.avg_rating >= rating_min)
    
    if tags:
        for tag in tags:
            query = query.where(Recipe.tags.contains([tag]))
    
    if created_by:
        query = query.where(Recipe.created_by == UUID(created_by))
    
    if is_public is not None:
        query = query.where(Recipe.is_public == is_public)
    
    # Order by rating and creation date
    query = query.order_by(
        Recipe.avg_rating.desc().nullslast(),
        Recipe.created_at.desc()
    )
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    recipes = result.scalars().all()
    
    return recipes


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Create a new recipe"""
    # Create recipe
    recipe = Recipe(
        **recipe_data.dict(exclude={"ingredients", "steps"}),
        created_by=current_user.id,
        household_id=current_user.household_id
    )
    
    db.add(recipe)
    await db.flush()
    
    # Add ingredients
    if recipe_data.ingredients:
        for ingredient_data in recipe_data.ingredients:
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                **ingredient_data.dict()
            )
            db.add(ingredient)
    
    # Add steps
    if recipe_data.steps:
        for step_data in recipe_data.steps:
            step = RecipeStep(
                recipe_id=recipe.id,
                **step_data.dict()
            )
            db.add(step)
    
    await db.commit()
    await db.refresh(recipe)
    
    # Load relationships
    await db.execute(
        select(Recipe)
        .options(selectinload(Recipe.ingredients), selectinload(Recipe.steps))
        .where(Recipe.id == recipe.id)
    )
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "recipe", recipe.id,
        new_values={"title": recipe.title, "category": recipe.category}
    )
    
    return recipe


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific recipe"""
    result = await db.execute(
        select(Recipe)
        .options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.reviews)
        )
        .where(
            Recipe.id == recipe_id,
            or_(
                Recipe.created_by == current_user.id,
                Recipe.is_public == True,
                Recipe.household_id == current_user.household_id
            )
        )
    )
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: UUID,
    recipe_update: RecipeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Update a recipe"""
    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id,
            Recipe.created_by == current_user.id
        )
    )
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or not authorized"
        )
    
    # Store old values for audit
    old_values = {
        "title": recipe.title,
        "description": recipe.description,
        "category": recipe.category,
        "difficulty": recipe.difficulty
    }
    
    # Update recipe fields
    update_data = recipe_update.dict(exclude_unset=True, exclude={"ingredients", "steps"})
    for field, value in update_data.items():
        setattr(recipe, field, value)
    
    # Update ingredients if provided
    if recipe_update.ingredients is not None:
        # Delete existing ingredients
        await db.execute(
            select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
        )
        
        # Add new ingredients
        for ingredient_data in recipe_update.ingredients:
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                **ingredient_data.dict()
            )
            db.add(ingredient)
    
    # Update steps if provided
    if recipe_update.steps is not None:
        # Delete existing steps
        await db.execute(
            select(RecipeStep).where(RecipeStep.recipe_id == recipe_id)
        )
        
        # Add new steps
        for step_data in recipe_update.steps:
            step = RecipeStep(
                recipe_id=recipe.id,
                **step_data.dict()
            )
            db.add(step)
    
    recipe.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(recipe)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "recipe", recipe.id,
        old_values=old_values,
        new_values=update_data
    )
    
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Delete a recipe"""
    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id,
            Recipe.created_by == current_user.id
        )
    )
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or not authorized"
        )
    
    await db.delete(recipe)
    await db.commit()
    
    # Log action
    await audit_service.log_action(
        current_user.id, "DELETE", "recipe", recipe_id,
        old_values={"title": recipe.title}
    )


@router.post("/{recipe_id}/reviews", response_model=RecipeReviewCreate)
async def add_recipe_review(
    recipe_id: UUID,
    review_data: RecipeReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Add a review to a recipe"""
    # Verify recipe exists and is accessible
    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id,
            or_(
                Recipe.is_public == True,
                Recipe.household_id == current_user.household_id
            )
        )
    )
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Create review
    review = RecipeReview(
        recipe_id=recipe_id,
        user_id=current_user.id,
        **review_data.dict()
    )
    
    db.add(review)
    await db.flush()
    
    # Update recipe average rating
    result = await db.execute(
        select(func.avg(RecipeReview.rating))
        .where(RecipeReview.recipe_id == recipe_id)
    )
    avg_rating = result.scalar()
    
    recipe.avg_rating = avg_rating
    recipe.review_count += 1
    
    await db.commit()
    await db.refresh(review)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "recipe_review", review.id,
        new_values={"recipe_id": str(recipe_id), "rating": review_data.rating}
    )
    
    return review


@router.post("/import-url", response_model=RecipeImportResponse)
async def import_recipe_from_url(
    request: RecipeImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService)
):
    """Import recipe from URL using AI"""
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recipe import is a premium feature"
        )
    
    try:
        # This would use AI to scrape and parse recipe from URL
        # For now, return a placeholder response
        recipe_data = RecipeCreate(
            title="Imported Recipe",
            description="Recipe imported from URL",
            category="general",
            prep_time=30,
            cook_time=45,
            servings=4,
            difficulty="medium",
            ingredients=[],
            steps=[]
        )
        
        return RecipeImportResponse(
            success=True,
            recipe=recipe_data,
            source_url=request.url,
            message="Recipe imported successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import recipe: {str(e)}"
        )


@router.get("/search/suggestions", response_model=RecipeSearchResponse)
async def get_search_suggestions(
    query: str = Query(..., min_length=2, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recipe search suggestions"""
    result = await db.execute(
        select(Recipe.title)
        .where(
            Recipe.title.ilike(f"%{query}%"),
            or_(
                Recipe.created_by == current_user.id,
                Recipe.is_public == True,
                Recipe.household_id == current_user.household_id
            )
        )
        .limit(10)
    )
    
    suggestions = result.scalars().all()
    
    return RecipeSearchResponse(
        query=query,
        suggestions=suggestions
    )