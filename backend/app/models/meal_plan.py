"""
Meal planning models
"""

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class MealPlan(BaseModel):
    """Meal planning headers"""
    
    __tablename__ = "meal_plans"
    
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    plan_name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    generated_by_ai = Column(Boolean, default=False, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    household = relationship("Household", back_populates="meal_plans")
    created_by_user = relationship("User", back_populates="meal_plans")
    entries = relationship("MealPlanEntry", back_populates="meal_plan", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_meal_plans_household_date', 'household_id', 'start_date', 'end_date'),
    )


class MealPlanEntry(BaseModel):
    """Individual meal entries in a plan"""
    
    __tablename__ = "meal_plan_entries"
    
    plan_id = Column(UUID(as_uuid=True), ForeignKey("meal_plans.id"), nullable=False)
    meal_date = Column(Date, nullable=False, index=True)
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=True)
    servings_planned = Column(Integer, default=1, nullable=False)
    prep_notes = Column(Text)
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="entries")
    recipe = relationship("Recipe", back_populates="meal_plan_entries")
    
    # Indexes
    __table_args__ = (
        Index('idx_meal_plan_entries_plan_date', 'plan_id', 'meal_date'),
        Index('idx_meal_plan_entries_type', 'meal_type'),
    )