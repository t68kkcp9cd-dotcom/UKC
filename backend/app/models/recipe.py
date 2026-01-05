"""
Recipe management models
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class Recipe(BaseModel):
    """Recipe headers/metadata"""
    
    __tablename__ = "recipes"
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    servings = Column(Integer)
    difficulty = Column(String(20))  # easy, medium, hard
    cuisine_type = Column(String(50), index=True)
    
    # JSON fields
    dietary_tags = Column(JSONB, default=list, nullable=False)
    nutrition_estimates = Column(JSONB)
    
    # Cost and sustainability
    cost_estimate = Column(Numeric(10, 2))
    carbon_footprint = Column(Numeric(10, 2))
    
    # Source tracking
    source_url = Column(String(500))
    imported_from = Column(String(50))  # youtube, website, manual
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    average_rating = Column(Numeric(3, 2))
    total_ratings = Column(Integer, default=0, nullable=False)
    
    # Relationships
    created_by_user = relationship("User", back_populates="recipes")
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    steps = relationship("RecipeStep", back_populates="recipe", cascade="all, delete-orphan")
    reviews = relationship("RecipeReview", back_populates="recipe", cascade="all, delete-orphan")
    meal_plan_entries = relationship("MealPlanEntry", back_populates="recipe")


class RecipeIngredient(BaseModel):
    """Recipe ingredients"""
    
    __tablename__ = "recipe_ingredients"
    
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=False)
    ingredient_name = Column(String(255), nullable=False, index=True)
    quantity = Column(Numeric(10, 3))
    unit = Column(String(50))
    notes = Column(Text)
    order_index = Column(Integer, default=0, nullable=False)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    
    # Indexes
    __table_args__ = (
        Index('idx_recipe_ingredients_recipe', 'recipe_id'),
        Index('idx_recipe_ingredients_name', 'ingredient_name'),
    )


class RecipeStep(BaseModel):
    """Recipe preparation steps"""
    
    __tablename__ = "recipe_steps"
    
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    instruction = Column(Text, nullable=False)
    timer_seconds = Column(Integer)  # optional timer for step
    image_url = Column(String(500))
    
    # Relationships
    recipe = relationship("Recipe", back_populates="steps")
    
    # Indexes
    __table_args__ = (
        Index('idx_recipe_steps_recipe', 'recipe_id', 'step_number'),
    )


class RecipeReview(BaseModel):
    """User reviews and ratings for recipes"""
    
    __tablename__ = "recipe_reviews"
    
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    review_text = Column(Text)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="reviews")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_recipe_reviews_recipe', 'recipe_id'),
        Index('idx_recipe_reviews_user', 'user_id'),
        Index('idx_recipe_reviews_rating', 'rating'),
    )