"""
Shopping list management schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class StoreBase(BaseModel):
    """Base store schema"""
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    is_public: bool = Field(False, description="Whether store is publicly visible")


class StoreCreate(StoreBase):
    """Store creation schema"""
    pass


class StoreResponse(StoreBase):
    """Store response schema"""
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ShoppingListItemBase(BaseModel):
    """Base shopping list item schema"""
    name: str = Field(..., min_length=1, max_length=255)
    quantity: Decimal = Field(..., gt=0, decimal_places=3)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    estimated_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notes: Optional[str] = Field(None, max_length=500)
    is_completed: bool = False
    priority: str = Field("medium", regex="^(low|medium|high)$")


class ShoppingListItemCreate(ShoppingListItemBase):
    """Shopping list item creation schema"""
    pass


class ShoppingListItemUpdate(BaseModel):
    """Shopping list item update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    quantity: Optional[Decimal] = Field(None, gt=0, decimal_places=3)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    estimated_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notes: Optional[str] = Field(None, max_length=500)
    is_completed: Optional[bool] = None
    priority: Optional[str] = Field(None, regex="^(low|medium|high)$")


class ShoppingListItemResponse(ShoppingListItemBase):
    """Shopping list item response schema"""
    id: UUID
    shopping_list_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ShoppingListBase(BaseModel):
    """Base shopping list schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True


class ShoppingListCreate(ShoppingListBase):
    """Shopping list creation schema"""
    pass


class ShoppingListUpdate(BaseModel):
    """Shopping list update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ShoppingListResponse(ShoppingListBase):
    """Shopping list response schema"""
    id: UUID
    created_by: UUID
    household_id: UUID
    items: List[ShoppingListItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PriceComparisonItem(BaseModel):
    """Price comparison for a single item"""
    item_name: str
    best_price: Dict[str, Any]
    all_prices: List[Dict[str, Any]]
    potential_savings: Decimal


class PriceComparisonResponse(BaseModel):
    """Price comparison response"""
    shopping_list_id: UUID
    item_comparisons: List[PriceComparisonItem]
    total_estimated_savings: Decimal
    best_store: str
    message: str