"""
Shopping list management endpoints
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.shopping import ShoppingList, ShoppingListItem, Store
from app.models.user import User
from app.schemas.shopping import (
    ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse,
    ShoppingListItemCreate, ShoppingListItemUpdate, ShoppingListItemResponse,
    StoreCreate, StoreResponse, PriceComparisonResponse
)
from app.services.audit_service import AuditService
from app.api.v1.auth import get_current_user

router = APIRouter()


@router.get("/stores", response_model=List[StoreResponse])
async def get_stores(
    name: Optional[str] = Query(None, description="Filter by store name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stores with filtering"""
    query = select(Store).where(
        or_(
            Store.created_by == current_user.id,
            Store.is_public == True
        )
    )
    
    if name:
        query = query.where(Store.name.ilike(f"%{name}%"))
    
    query = query.order_by(Store.name)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    stores = result.scalars().all()
    
    return stores


@router.post("/stores", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    store_data: StoreCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Create a new store"""
    store = Store(
        **store_data.dict(),
        created_by=current_user.id
    )
    
    db.add(store)
    await db.commit()
    await db.refresh(store)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "store", store.id,
        new_values={"name": store.name}
    )
    
    return store


@router.get("/lists", response_model=List[ShoppingListResponse])
async def get_shopping_lists(
    name: Optional[str] = Query(None, description="Filter by list name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get shopping lists with filtering"""
    query = select(ShoppingList).options(
        selectinload(ShoppingList.items)
    ).where(
        or_(
            ShoppingList.created_by == current_user.id,
            ShoppingList.household_id == current_user.household_id
        )
    )
    
    if name:
        query = query.where(ShoppingList.name.ilike(f"%{name}%"))
    
    if is_active is not None:
        query = query.where(ShoppingList.is_active == is_active)
    
    if created_by:
        query = query.where(ShoppingList.created_by == UUID(created_by))
    
    query = query.order_by(ShoppingList.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    shopping_lists = result.scalars().all()
    
    return shopping_lists


@router.post("/lists", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    list_data: ShoppingListCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Create a new shopping list"""
    shopping_list = ShoppingList(
        **list_data.dict(),
        created_by=current_user.id,
        household_id=current_user.household_id
    )
    
    db.add(shopping_list)
    await db.commit()
    await db.refresh(shopping_list)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "shopping_list", shopping_list.id,
        new_values={"name": shopping_list.name}
    )
    
    return shopping_list


@router.get("/lists/{list_id}", response_model=ShoppingListResponse)
async def get_shopping_list(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific shopping list"""
    result = await db.execute(
        select(ShoppingList)
        .options(selectinload(ShoppingList.items))
        .where(
            ShoppingList.id == list_id,
            or_(
                ShoppingList.created_by == current_user.id,
                ShoppingList.household_id == current_user.household_id
            )
        )
    )
    shopping_list = result.scalar_one_or_none()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    return shopping_list


@router.put("/lists/{list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(
    list_id: UUID,
    list_update: ShoppingListUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Update a shopping list"""
    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            ShoppingList.created_by == current_user.id
        )
    )
    shopping_list = result.scalar_one_or_none()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or not authorized"
        )
    
    # Store old values for audit
    old_values = {
        "name": shopping_list.name,
        "description": shopping_list.description,
        "is_active": shopping_list.is_active
    }
    
    # Update fields
    update_data = list_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shopping_list, field, value)
    
    shopping_list.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(shopping_list)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "shopping_list", shopping_list.id,
        old_values=old_values,
        new_values=update_data
    )
    
    return shopping_list


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Delete a shopping list"""
    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            ShoppingList.created_by == current_user.id
        )
    )
    shopping_list = result.scalar_one_or_none()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or not authorized"
        )
    
    await db.delete(shopping_list)
    await db.commit()
    
    # Log action
    await audit_service.log_action(
        current_user.id, "DELETE", "shopping_list", list_id,
        old_values={"name": shopping_list.name}
    )


@router.post("/lists/{list_id}/items", response_model=ShoppingListItemResponse)
async def add_shopping_list_item(
    list_id: UUID,
    item_data: ShoppingListItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Add an item to a shopping list"""
    # Verify shopping list exists and user has access
    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            or_(
                ShoppingList.created_by == current_user.id,
                ShoppingList.household_id == current_user.household_id
            )
        )
    )
    shopping_list = result.scalar_one_or_none()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    # Create item
    item = ShoppingListItem(
        shopping_list_id=list_id,
        **item_data.dict()
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "shopping_list_item", item.id,
        new_values={
            "shopping_list_id": str(list_id),
            "name": item_data.name,
            "quantity": float(item_data.quantity)
        }
    )
    
    return item


@router.get("/lists/{list_id}/items", response_model=List[ShoppingListItemResponse])
async def get_shopping_list_items(
    list_id: UUID,
    is_completed: Optional[bool] = Query(None, description="Filter by completion status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get items from a shopping list"""
    # Verify shopping list access
    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            or_(
                ShoppingList.created_by == current_user.id,
                ShoppingList.household_id == current_user.household_id
            )
        )
    )
    shopping_list = result.scalar_one_or_none()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    query = select(ShoppingListItem).where(
        ShoppingListItem.shopping_list_id == list_id
    )
    
    if is_completed is not None:
        query = query.where(ShoppingListItem.is_completed == is_completed)
    
    if category:
        query = query.where(ShoppingListItem.category == category)
    
    query = query.order_by(
        ShoppingListItem.is_completed,
        ShoppingListItem.category.nullslast(),
        ShoppingListItem.name
    )
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return items


@router.put("/lists/{list_id}/items/{item_id}", response_model=ShoppingListItemResponse)
async def update_shopping_list_item(
    list_id: UUID,
    item_id: UUID,
    item_update: ShoppingListItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Update a shopping list item"""
    result = await db.execute(
        select(ShoppingListItem)
        .join(ShoppingList)
        .where(
            ShoppingListItem.id == item_id,
            ShoppingListItem.shopping_list_id == list_id,
            ShoppingList.created_by == current_user.id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found"
        )
    
    # Update fields
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    item.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(item)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "shopping_list_item", item_id,
        new_values=update_data
    )
    
    return item


@router.delete("/lists/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list_item(
    list_id: UUID,
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Delete a shopping list item"""
    result = await db.execute(
        select(ShoppingListItem)
        .join(ShoppingList)
        .where(
            ShoppingListItem.id == item_id,
            ShoppingListItem.shopping_list_id == list_id,
            ShoppingList.created_by == current_user.id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found"
        )
    
    await db.delete(item)
    await db.commit()
    
    # Log action
    await audit_service.log_action(
        current_user.id, "DELETE", "shopping_list_item", item_id,
        old_values={"name": item.name}
    )


@router.get("/lists/{list_id}/compare-prices", response_model=PriceComparisonResponse)
async def compare_prices(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare prices for shopping list items across stores"""
    # Verify shopping list access
    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            or_(
                ShoppingList.created_by == current_user.id,
                ShoppingList.household_id == current_user.household_id
            )
        )
    )
    shopping_list = result.scalar_one_or_none()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    # Get items
    result = await db.execute(
        select(ShoppingListItem).where(
            ShoppingListItem.shopping_list_id == list_id,
            ShoppingListItem.is_completed == False
        )
    )
    items = result.scalars().all()
    
    # Mock price comparison (in real implementation, this would query store APIs)
    comparisons = []
    
    for item in items:
        mock_prices = [
            {"store": "Store A", "price": 2.99, "unit": "per lb"},
            {"store": "Store B", "price": 3.49, "unit": "per lb"},
            {"store": "Store C", "price": 2.79, "unit": "per lb"}
        ]
        
        best_price = min(mock_prices, key=lambda x: x["price"])
        
        comparisons.append({
            "item_name": item.name,
            "best_price": best_price,
            "all_prices": mock_prices,
            "potential_savings": max(p["price"] for p in mock_prices) - best_price["price"]
        })
    
    total_savings = sum(c["potential_savings"] for c in comparisons)
    
    return PriceComparisonResponse(
        shopping_list_id=list_id,
        item_comparisons=comparisons,
        total_estimated_savings=total_savings,
        best_store="Store C",  # Mock best overall store
        message="Price comparison completed"
    )


@router.post("/lists/{list_id}/optimize")
async def optimize_shopping_list(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimize shopping list by grouping items by store section"""
    # Verify shopping list access
    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id,
            or_(
                ShoppingList.created_by == current_user.id,
                ShoppingList.household_id == current_user.household_id
            )
        )
    )
    shopping_list = result.scalar_one_or_none()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    
    # Get items
    result = await db.execute(
        select(ShoppingListItem).where(
            ShoppingListItem.shopping_list_id == list_id,
            ShoppingListItem.is_completed == False
        )
    )
    items = result.scalars().all()
    
    # Group by store sections
    sections = {
        "produce": [],
        "dairy": [],
        "meat": [],
        "pantry": [],
        "frozen": [],
        "bakery": [],
        "other": []
    }
    
    # Simple categorization based on item name
    for item in items:
        name_lower = item.name.lower()
        
        if any(word in name_lower for word in ["apple", "banana", "lettuce", "tomato", "onion", "carrot"]):
            sections["produce"].append(item)
        elif any(word in name_lower for word in ["milk", "cheese", "yogurt", "butter", "cream"]):
            sections["dairy"].append(item)
        elif any(word in name_lower for word in ["chicken", "beef", "pork", "fish", "meat"]):
            sections["meat"].append(item)
        elif any(word in name_lower for word in ["bread", "rice", "pasta", "cereal", "flour"]):
            sections["pantry"].append(item)
        elif any(word in name_lower for word in ["frozen", "ice cream"]):
            sections["frozen"].append(item)
        elif any(word in name_lower for word in ["bread", "cake", "cookies"]):
            sections["bakery"].append(item)
        else:
            sections["other"].append(item)
    
    return {
        "shopping_list_id": list_id,
        "optimized_sections": sections,
        "total_items": len(items),
        "optimization_suggestions": [
            "Start with non-perishable items",
            "Get frozen items last",
            "Check produce for freshness",
            "Compare prices in each section"
        ]
    }