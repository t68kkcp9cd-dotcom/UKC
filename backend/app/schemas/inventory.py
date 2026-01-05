"""
Inventory management schemas
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, validator


class InventoryItemBase(BaseModel):
    """Base inventory item schema"""
    name: str = Field(..., min_length=1, max_length=255)
    barcode: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    quantity: Decimal = Field(..., ge=0, decimal_places=3)
    unit: str = Field(..., max_length=50)
    expiration_date: Optional[date] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    location: str = Field(..., max_length=100)  # pantry, fridge, freezer
    nutrition_data: Optional[Dict[str, Any]] = None


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating inventory items"""
    pass


class InventoryItemUpdate(BaseModel):
    """Schema for updating inventory items"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    barcode: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    quantity: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    unit: Optional[str] = Field(None, max_length=50)
    expiration_date: Optional[date] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    location: Optional[str] = Field(None, max_length=100)
    nutrition_data: Optional[Dict[str, Any]] = None


class InventoryItemResponse(InventoryItemBase):
    """Inventory item response schema"""
    id: UUID
    household_id: UUID
    added_by: UUID
    price_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    days_until_expiration: Optional[int] = None
    
    @validator('days_until_expiration', pre=True, always=True)
    def calculate_days_until_expiration(cls, v, values):
        if 'expiration_date' in values and values['expiration_date']:
            return (values['expiration_date'] - date.today()).days
        return None
    
    class Config:
        from_attributes = True


class BarcodeLookupRequest(BaseModel):
    """Barcode lookup request"""
    barcode: str = Field(..., min_length=8, max_length=13)
    location: Optional[str] = Field(None, max_length=100)


class BarcodeLookupResponse(BaseModel):
    """Barcode lookup response"""
    barcode: str
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    nutrition_data: Dict[str, Any] = Field(default_factory=dict)
    allergens: List[str] = Field(default_factory=list)
    ingredients: List[str] = Field(default_factory=list)
    source: str = Field(..., description="Data source (openfoodfacts, usda, etc.)")
    

class WasteForecastResponse(BaseModel):
    """Waste forecasting response"""
    household_id: UUID
    forecast_period_days: int
    total_items_at_risk: int
    estimated_waste_value: Decimal
    items_at_risk: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0, le=1)
    
    class Config:
        from_attributes = True


class ConsumptionLogCreate(BaseModel):
    """Consumption log creation schema"""
    item_id: UUID
    quantity_used: Decimal = Field(..., gt=0, decimal_places=3)
    waste_reason: Optional[str] = Field(None, max_length=50)


class ConsumptionLogResponse(BaseModel):
    """Consumption log response"""
    id: UUID
    item_id: UUID
    user_id: UUID
    quantity_used: Decimal
    waste_reason: Optional[str] = None
    used_at: datetime
    
    class Config:
        from_attributes = True