"""
Shopping list and store integration models
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class Store(BaseModel):
    """Store information for price comparison"""
    
    __tablename__ = "stores"
    
    name = Column(String(255), nullable=False, index=True)
    chain = Column(String(100), index=True)
    address = Column(Text)
    zip_code = Column(String(20), index=True)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    
    # API configuration
    api_endpoint = Column(String(500))  # for price lookups
    api_config = Column(JSONB)  # store-specific API config
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    shopping_lists = relationship("ShoppingList", back_populates="store")
    prices = relationship("StorePrice", back_populates="store")


class StorePrice(BaseModel):
    """Store pricing data for items"""
    
    __tablename__ = "store_prices"
    
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    item_barcode = Column(String(50), index=True)
    item_name = Column(String(255), index=True)
    current_price = Column(Numeric(10, 2), nullable=False)
    price_per_unit = Column(Numeric(10, 2))
    unit_type = Column(String(50))
    availability_status = Column(String(20))  # in_stock, out_of_stock, limited
    last_updated = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    store = relationship("Store", back_populates="prices")
    
    # Indexes
    __table_args__ = (
        Index('idx_store_prices_lookup', 'store_id', 'item_barcode'),
        Index('idx_store_prices_name', 'item_name'),
    )


class ShoppingList(BaseModel):
    """Shopping lists"""
    
    __tablename__ = "shopping_lists"
    
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    list_name = Column(String(255), nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    household = relationship("Household", back_populates="shopping_lists")
    store = relationship("Store", back_populates="shopping_lists")
    created_by_user = relationship("User", back_populates="shopping_lists")
    items = relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")


class ShoppingListItem(BaseModel):
    """Items in shopping lists"""
    
    __tablename__ = "shopping_list_items"
    
    list_id = Column(UUID(as_uuid=True), ForeignKey("shopping_lists.id"), nullable=False)
    item_name = Column(String(255), nullable=False, index=True)
    quantity = Column(Numeric(10, 3))
    unit = Column(String(50))
    category = Column(String(100), index=True)
    
    # Price tracking
    estimated_price = Column(Numeric(10, 2))
    best_price_found = Column(Numeric(10, 2))
    best_store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True)
    
    is_checked = Column(Boolean, default=False, nullable=False)
    added_from_inventory = Column(Boolean, default=False, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    
    # Relationships
    shopping_list = relationship("ShoppingList", back_populates="items")
    best_store = relationship("Store")
    
    # Indexes
    __table_args__ = (
        Index('idx_shopping_list_items_list', 'list_id'),
        Index('idx_shopping_list_items_category', 'category'),
    )