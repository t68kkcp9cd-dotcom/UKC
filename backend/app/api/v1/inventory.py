"""
Inventory management endpoints
"""

from typing import List, Optional
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.inventory import InventoryItem, ConsumptionLog
from app.models.user import User
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    BarcodeLookupRequest, BarcodeLookupResponse, WasteForecastResponse,
    ConsumptionLogCreate, ConsumptionLogResponse
)
from app.services.inventory_service import InventoryService
from app.services.barcode_service import BarcodeService
from app.services.ai_service import AIService
from app.services.audit_service import AuditService
from app.api.v1.auth import get_current_user
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    location: Optional[str] = Query(None, description="Filter by location"),
    category: Optional[str] = Query(None, description="Filter by category"),
    expires_before: Optional[date] = Query(None, description="Filter items expiring before date"),
    expires_after: Optional[date] = Query(None, description="Filter items expiring after date"),
    search: Optional[str] = Query(None, description="Search in item names"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inventory items with filtering"""
    query = select(InventoryItem).where(
        InventoryItem.household_id == current_user.household_id
    )
    
    # Apply filters
    if location:
        query = query.where(InventoryItem.location == location)
    
    if category:
        query = query.where(InventoryItem.category == category)
    
    if expires_before:
        query = query.where(InventoryItem.expiration_date <= expires_before)
    
    if expires_after:
        query = query.where(InventoryItem.expiration_date >= expires_after)
    
    if search:
        query = query.where(InventoryItem.name.ilike(f"%{search}%"))
    
    # Order by expiration date (nulls last)
    query = query.order_by(
        InventoryItem.expiration_date.asc().nullslast(),
        InventoryItem.created_at.desc()
    )
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return items


@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Create a new inventory item"""
    # Set default category if not provided
    if not item_data.category:
        item_data.category = "general"
    
    # Create item
    item = InventoryItem(
        **item_data.dict(),
        household_id=current_user.household_id,
        added_by=current_user.id
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CREATE", "inventory_item", item.id,
        new_values=item_data.dict()
    )
    
    logger.info(f"Inventory item created: {item.name} by {current_user.username}")
    return item


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific inventory item"""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == item_id,
            InventoryItem.household_id == current_user.household_id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: UUID,
    item_update: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Update an inventory item"""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == item_id,
            InventoryItem.household_id == current_user.household_id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Store old values for audit
    old_values = {
        "name": item.name,
        "quantity": float(item.quantity),
        "location": item.location,
        "expiration_date": item.expiration_date.isoformat() if item.expiration_date else None
    }
    
    # Update fields
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "UPDATE", "inventory_item", item.id,
        old_values=old_values,
        new_values=update_data
    )
    
    logger.info(f"Inventory item updated: {item.name} by {current_user.username}")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Delete an inventory item"""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == item_id,
            InventoryItem.household_id == current_user.household_id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    await db.delete(item)
    await db.commit()
    
    # Log action
    await audit_service.log_action(
        current_user.id, "DELETE", "inventory_item", item_id,
        old_values={"name": item.name}
    )
    
    logger.info(f"Inventory item deleted: {item.name} by {current_user.username}")


@router.post("/scan-barcode", response_model=BarcodeLookupResponse)
async def scan_barcode(
    barcode_data: BarcodeLookupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    barcode_service: BarcodeService = Depends(BarcodeService)
):
    """Scan barcode and lookup product information"""
    try:
        product_info = await barcode_service.lookup_barcode(barcode_data.barcode)
        return product_info
    except Exception as e:
        logger.error(f"Barcode lookup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to lookup barcode"
        )


@router.get("/forecast-waste", response_model=WasteForecastResponse)
async def forecast_waste(
    days_ahead: int = Query(7, ge=1, le=30, description="Forecast period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(AIService)
):
    """Get AI-powered waste forecasting"""
    try:
        result = await db.execute(
            select(InventoryItem).where(
                InventoryItem.household_id == current_user.household_id,
                InventoryItem.expiration_date.isnot(None),
                InventoryItem.expiration_date <= date.today() + timedelta(days=days_ahead)
            )
        )
        items = result.scalars().all()
        
        forecast = await ai_service.forecast_waste(items, days_ahead)
        return forecast
        
    except Exception as e:
        logger.error(f"Waste forecasting failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate waste forecast"
        )


@router.post("/{item_id}/consume", response_model=ConsumptionLogResponse)
async def log_consumption(
    item_id: UUID,
    consumption_data: ConsumptionLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(AuditService)
):
    """Log consumption of an inventory item"""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == item_id,
            InventoryItem.household_id == current_user.household_id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Create consumption log
    log = ConsumptionLog(
        item_id=item_id,
        user_id=current_user.id,
        quantity_used=consumption_data.quantity_used,
        waste_reason=consumption_data.waste_reason
    )
    
    db.add(log)
    
    # Update item quantity
    item.quantity -= consumption_data.quantity_used
    
    if item.quantity <= 0:
        await db.delete(item)
    
    await db.commit()
    await db.refresh(log)
    
    # Log action
    await audit_service.log_action(
        current_user.id, "CONSUME", "inventory_item", item_id,
        new_values={
            "quantity_used": float(consumption_data.quantity_used),
            "waste_reason": consumption_data.waste_reason
        }
    )
    
    return log