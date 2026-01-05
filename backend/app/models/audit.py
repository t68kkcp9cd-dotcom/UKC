"""
Audit logging models for security and compliance
"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel


class AuditLog(BaseModel):
    """Comprehensive audit log for all user actions"""
    
    __tablename__ = "audit_logs"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # CREATE, UPDATE, DELETE, etc.
    resource_type = Column(String(50), index=True)  # inventory_item, recipe, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Change tracking
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    
    # Request metadata
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_logs_user', 'user_id'),
        Index('idx_audit_logs_created', 'created_at'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
    )