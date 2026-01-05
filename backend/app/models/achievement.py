"""
Gamification and achievement models
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class Achievement(BaseModel):
    """Achievement/badges definitions"""
    
    __tablename__ = "achievements"
    
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    badge_icon_url = Column(String(500))
    category = Column(String(50), index=True)  # waste_reduction, cooking, etc.
    criteria = Column(JSONB, nullable=False)  # conditions to unlock
    points = Column(Integer, default=0, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(BaseModel):
    """User achievements/badges"""
    
    __tablename__ = "user_achievements"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), nullable=False)
    progress_data = Column(JSONB, default=dict, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_achievements_user', 'user_id'),
        Index('idx_user_achievements_achievement', 'achievement_id'),
    )