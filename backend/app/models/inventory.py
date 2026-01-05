"""
Inventory and pantry management models
"""

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class InventoryItem(BaseModel):
    """Items in user's pantry/inventory"""
    
    __tablename__ = "inventory_items"
    
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    barcode = Column(String(50))
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), index=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit = Column(String(50), nullable=False)
    expiration_date = Column(Date, index=True)
    purchase_date = Column(Date)
    purchase_price = Column(Numeric(10, 2))
    location = Column(String(100), index=True)  # pantry, fridge, freezer
    
    # JSON fields for flexibility
    nutrition_data = Column(JSONB)
    price_history = Column(JSONB, default=list, nullable=False)
    
    added_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    household = relationship("Household", back_populates="inventory_items")
    added_by_user = relationship("User", back_populates="inventory_items")
    consumption_logs = relationship("ConsumptionLog", back_populates="item", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_inventory_household_location', 'household_id', 'location'),
        Index('idx_inventory_expiration', 'expiration_date'),
    )


class ConsumptionLog(BaseModel):
    """Track consumption and waste for analytics"""
    
    __tablename__ = "consumption_logs"
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    quantity_used = Column(Numeric(10, 3), nullable=False)
    waste_reason = Column(String(50))  # expired, spoiled, used, donated
    
    # Relationships
    item = relationship("InventoryItem", back_populates="consumption_logs")
    user = relationship("User")