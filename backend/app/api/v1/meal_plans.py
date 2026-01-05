"""
Meal planning endpoints
"""

from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.meal_plan import MealPlan, MealPlanEntry
from app.models.user import User
from app.schemas.meal_plan import (
    MealPlanCreate, MealPlanUpdate, MealPlanResponse,
    MealPlanEntryCreate, MealPlanEntryResponse
)
from app.services.ai_service import AIService
from app.services.audit_service import AuditService
from app.api.v1.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[MealPlanResponse])
async def get_meal_plans(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get meal plans with filtering"""
    query = select(MealPlan).options(
        selectinload(MealPlan.entries)
    ).where(
        or_(
            MealPlan.created_by == current_user.id,
            MealPlan.household_id == current_user.household_id
        )
    )
    
    # Apply filters
    if start_date:
        query = query.where(MealPlan.start_date >= start_date)
    
    if end_date:
        query = query.where(MealPlan.end_date <= end_date)
    
    if is_active is not None:
        today = date.today()
        if is_active:
            query = query.where(
                and_(
                    MealPlan.start_date <= today,
                    MealPlan.end_date >= today
                )
            )
        else:
            query = query.where(
                or_(
                    MealPlan.start_date > today,
                    MealPlan.end_date < today
                )
            )
    
    if created_by:
        query = query.where(MealPlan.created_by == UUID(created_by))
    
    # Order by creation date
    query = query.order_by(MealPlan.created_at.desc())
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    meal_plans = result.scalars().all()
    
    return meal_plans


@router.post("/", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    meal_plan_data: MealPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Create a new meal plan"""
    # Validate date range
    if meal_plan_data.start_date > meal_plan_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Create meal plan
    meal_plan = MealPlan(
        **meal_plan_data.dict(exclude={"entries"}),
        created_by=current_user.id,
        household_id=current_user.household_id
    )
    
    db.add(meal_plan)
    await db.flush()
    
    # Add entries
    if meal_plan_data.entries:
        for entry_data in meal_plan_data.entries:
            entry = MealPlanEntry(
                meal_plan_id=meal_plan.id,
                **entry_data.dict()
            )
            db.add(entry)
    
    await db.commit()
    await db.refresh(meal_plan)
    
    # Load entries
    await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.entries))
        .where(MealPlan.id == meal_plan.id)
    )
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "meal_plan", meal_plan.id,
        new_values={"name": meal_plan.name, "start_date": meal_plan.start_date.isoformat()}
    )
    
    return meal_plan


@router.get("/{meal_plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(
    meal_plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific meal plan"""
    result = await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.entries))
        .where(
            MealPlan.id == meal_plan_id,
            or_(
                MealPlan.created_by == current_user.id,
                MealPlan.household_id == current_user.household_id
            )
        )
    )
    meal_plan = result.scalar_one_or_none()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return meal_plan


@router.put("/{meal_plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(
    meal_plan_id: UUID,
    meal_plan_update: MealPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Update a meal plan"""
    result = await db.execute(
        select(MealPlan).where(
            MealPlan.id == meal_plan_id,
            MealPlan.created_by == current_user.id
        )
    )
    meal_plan = result.scalar_one_or_none()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found or not authorized"
        )
    
    # Store old values for audit
    old_values = {
        "name": meal_plan.name,
        "description": meal_plan.description,
        "start_date": meal_plan.start_date.isoformat(),
        "end_date": meal_plan.end_date.isoformat()
    }
    
    # Update fields
    update_data = meal_plan_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meal_plan, field, value)
    
    meal_plan.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(meal_plan)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "meal_plan", meal_plan.id,
        old_values=old_values,
        new_values=update_data
    )
    
    return meal_plan


@router.delete("/{meal_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    meal_plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Delete a meal plan"""
    result = await db.execute(
        select(MealPlan).where(
            MealPlan.id == meal_plan_id,
            MealPlan.created_by == current_user.id
        )
    )
    meal_plan = result.scalar_one_or_none()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found or not authorized"
        )
    
    await db.delete(meal_plan)
    await db.commit()
    
    # Log action
    await audit_service.log_action(
        current_user.id, "DELETE", "meal_plan", meal_plan_id,
        old_values={"name": meal_plan.name}
    )


@router.post("/{meal_plan_id}/entries", response_model=MealPlanEntryResponse)
async def add_meal_plan_entry(
    meal_plan_id: UUID,
    entry_data: MealPlanEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Add an entry to a meal plan"""
    # Verify meal plan exists and user has access
    result = await db.execute(
        select(MealPlan).where(
            MealPlan.id == meal_plan_id,
            or_(
                MealPlan.created_by == current_user.id,
                MealPlan.household_id == current_user.household_id
            )
        )
    )
    meal_plan = result.scalar_one_or_none()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    # Create entry
    entry = MealPlanEntry(
        meal_plan_id=meal_plan_id,
        **entry_data.dict()
    )
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "meal_plan_entry", entry.id,
        new_values={
            "meal_plan_id": str(meal_plan_id),
            "date": entry_data.date.isoformat(),
            "meal_type": entry_data.meal_type
        }
    )
    
    return entry


@router.get("/{meal_plan_id}/entries", response_model=List[MealPlanEntryResponse])
async def get_meal_plan_entries(
    meal_plan_id: UUID,
    date: Optional[date] = Query(None, description="Filter by specific date"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get entries for a meal plan"""
    query = select(MealPlanEntry).where(
        MealPlanEntry.meal_plan_id == meal_plan_id
    )
    
    if date:
        query = query.where(MealPlanEntry.date == date)
    
    if meal_type:
        query = query.where(MealPlanEntry.meal_type == meal_type)
    
    query = query.order_by(MealPlanEntry.date, MealPlanEntry.meal_type)
    
    result = await db.execute(query)
    entries = result.scalars().all()
    
    return entries


@router.delete("/{meal_plan_id}/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan_entry(
    meal_plan_id: UUID,
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Delete a meal plan entry"""
    result = await db.execute(
        select(MealPlanEntry)
        .join(MealPlan)
        .where(
            MealPlanEntry.id == entry_id,
            MealPlanEntry.meal_plan_id == meal_plan_id,
            MealPlan.created_by == current_user.id
        )
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan entry not found"
        )
    
    await db.delete(entry)
    await db.commit()
    
    # Log action
    await audit_service.log_action(
        current_user.id, "DELETE", "meal_plan_entry", entry_id,
        old_values={"meal_plan_id": str(meal_plan_id), "date": entry.date.isoformat()}
    )


@router.get("/current-week", response_model=MealPlanResponse)
async def get_current_week_meal_plan(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current active meal plan for this week"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    
    result = await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.entries))
        .where(
            MealPlan.household_id == current_user.household_id,
            MealPlan.start_date <= week_end,
            MealPlan.end_date >= week_start
        )
        .order_by(MealPlan.created_at.desc())
        .limit(1)
    )
    
    meal_plan = result.scalar_one_or_none()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No meal plan found for current week"
        )
    
    return meal_plan


@router.get("/suggestions", response_model=List[str])
async def get_meal_suggestions(
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get meal suggestions based on preferences and history"""
    # This would use AI to suggest meals
    # For now, return some basic suggestions
    
    suggestions = []
    
    if meal_type == "breakfast":
        suggestions = [
            "Overnight Oats with Berries",
            "Avocado Toast with Egg",
            "Greek Yogurt Parfait",
            "Smoothie Bowl",
            "Breakfast Burrito"
        ]
    elif meal_type == "lunch":
        suggestions = [
            "Quinoa Salad with Vegetables",
            "Chicken Caesar Wrap",
            "Lentil Soup",
            "Turkey Club Sandwich",
            "Buddha Bowl"
        ]
    elif meal_type == "dinner":
        suggestions = [
            "Grilled Salmon with Vegetables",
            "Chicken Stir Fry",
            "Pasta Primavera",
            "Beef Tacos",
            "Vegetable Curry"
        ]
    else:
        suggestions = [
            "Grilled Chicken Salad",
            "Vegetable Stir Fry",
            "Pasta with Marinara",
            "Fish Tacos",
            "Quinoa Bowl"
        ]
    
    return suggestions