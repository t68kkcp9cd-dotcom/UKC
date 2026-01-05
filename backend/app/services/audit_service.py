"""
Audit service for logging user actions and system events
Provides comprehensive audit trail for security and compliance
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.audit import AuditLog
from app.models.user import User

logger = logging.getLogger(__name__)


class AuditService:
    """Service for comprehensive audit logging"""
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        
    async def log_action(
        self,
        user_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> AuditLog:
        """
        Log a user action to the audit trail
        
        Args:
            user_id: ID of the user performing the action
            action: Action type (CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT, etc.)
            resource_type: Type of resource affected (inventory_item, recipe, user, etc.)
            resource_id: ID of the specific resource
            old_values: Previous values (for UPDATE actions)
            new_values: New values after the action
            ip_address: Client IP address
            user_agent: Client user agent string
            db: Database session (optional if provided in constructor)
            
        Returns:
            Created audit log entry
        """
        # Use provided db or instance db
        session = db or self.db
        if not session:
            raise ValueError("Database session required for audit logging")
            
        # Sanitize sensitive data
        if old_values:
            old_values = self._sanitize_data(old_values)
        if new_values:
            new_values = self._sanitize_data(new_values)
            
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        session.add(audit_log)
        await session.commit()
        await session.refresh(audit_log)
        
        # Log to application logger as well
        logger.info(
            f"Audit: {action} on {resource_type} by user {user_id}",
            extra={
                "audit_action": action,
                "audit_resource_type": resource_type,
                "audit_resource_id": str(resource_id) if resource_id else None,
                "audit_user_id": str(user_id) if user_id else None
            }
        )
        
        return audit_log
        
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from audit data"""
        if not data:
            return {}
            
        sanitized = {}
        sensitive_fields = [
            "password", "password_hash", "token", "secret", "key",
            "auth_token", "refresh_token", "jwt", "credential"
        ]
        
        for key, value in data.items():
            # Skip sensitive fields
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "[REDACTED]"
            # Recursively sanitize nested dictionaries
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            # Truncate very long values
            elif isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + "...[TRUNCATED]"
            else:
                sanitized[key] = value
                
        return sanitized
        
    async def get_audit_trail(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Retrieve audit trail with filtering options
        
        Args:
            db: Database session
            user_id: Filter by user ID
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            action: Filter by action type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of audit log entries
        """
        query = select(AuditLog).order_by(AuditLog.created_at.desc())
        
        # Apply filters
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)
        if action:
            query = query.where(AuditLog.action == action)
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
            
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_user_activity_summary(
        self,
        db: AsyncSession,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get activity summary for a user
        
        Args:
            db: Database session
            user_id: User ID to analyze
            days: Number of days to look back
            
        Returns:
            Activity summary statistics
        """
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user's recent actions
        result = await db.execute(
            select(AuditLog)
            .where(
                AuditLog.user_id == user_id,
                AuditLog.created_at >= start_date
            )
            .order_by(AuditLog.created_at.desc())
        )
        
        logs = result.scalars().all()
        
        # Calculate statistics
        action_counts = {}
        resource_counts = {}
        
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
            resource_counts[log.resource_type] = resource_counts.get(log.resource_type, 0) + 1
            
        return {
            "user_id": user_id,
            "period_days": days,
            "total_actions": len(logs),
            "action_breakdown": action_counts,
            "resource_breakdown": resource_counts,
            "most_active_day": self._find_most_active_day(logs),
            "recent_activity": [
                {
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": str(log.resource_id) if log.resource_id else None,
                    "timestamp": log.created_at.isoformat()
                }
                for log in logs[:10]  # Last 10 actions
            ]
        }
        
    def _find_most_active_day(self, logs: list[AuditLog]) -> Optional[str]:
        """Find the most active day from audit logs"""
        if not logs:
            return None
            
        day_counts = {}
        for log in logs:
            day = log.created_at.date()
            day_counts[day] = day_counts.get(day, 0) + 1
            
        if day_counts:
            most_active_day = max(day_counts, key=day_counts.get)
            return most_active_day.isoformat()
            
        return None
        
    async def get_security_events(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: str = "all"
    ) -> list[AuditLog]:
        """
        Get security-related events
        
        Args:
            db: Database session
            start_date: Filter by start date
            end_date: Filter by end date
            severity: Event severity level (all, high, medium, low)
            
        Returns:
            List of security-related audit logs
        """
        security_actions = [
            "LOGIN", "LOGIN_FAILED", "LOGOUT", "PASSWORD_CHANGED",
            "TOKEN_REFRESHED", "ACCOUNT_LOCKED", "SUSPICIOUS_ACTIVITY"
        ]
        
        query = (
            select(AuditLog)
            .where(AuditLog.action.in_(security_actions))
            .order_by(AuditLog.created_at.desc())
        )
        
        # Apply date filters
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
            
        result = await db.execute(query)
        return result.scalars().all()
        
    async def log_failed_login(
        self,
        db: AsyncSession,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        reason: str = "invalid_credentials"
    ):
        """Log a failed login attempt"""
        await self.log_action(
            db=db,
            user_id=None,  # No user ID for failed logins
            action="LOGIN_FAILED",
            resource_type="authentication",
            resource_id=None,
            new_values={
                "username": username,
                "reason": reason,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
    async def log_password_change(
        self,
        db: AsyncSession,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log password change event"""
        await self.log_action(
            db=db,
            user_id=user_id,
            action="PASSWORD_CHANGED",
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
    async def log_security_event(
        self,
        db: AsyncSession,
        event_type: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """Log a security-related event"""
        await self.log_action(
            db=db,
            user_id=user_id,
            action=f"SECURITY_{event_type}",
            resource_type="security",
            resource_id=None,
            new_values=details,
            ip_address=ip_address
        )
        
    async def export_audit_trail(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """
        Export audit trail for compliance or analysis
        
        Args:
            db: Database session
            start_date: Filter by start date
            end_date: Filter by end date
            format: Export format (json, csv)
            
        Returns:
            Exported data as string
        """
        logs = await self.get_audit_trail(
            db=db,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Large limit for exports
        )
        
        if format == "json":
            export_data = []
            for log in logs:
                export_data.append({
                    "id": str(log.id),
                    "timestamp": log.created_at.isoformat(),
                    "user_id": str(log.user_id) if log.user_id else None,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": str(log.resource_id) if log.resource_id else None,
                    "ip_address": str(log.ip_address) if log.ip_address else None,
                    "old_values": log.old_values,
                    "new_values": log.new_values
                })
                
            return json.dumps(export_data, indent=2, default=str)
            
        elif format == "csv":
            # Simple CSV export
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                "ID", "Timestamp", "User ID", "Action", "Resource Type",
                "Resource ID", "IP Address", "Old Values", "New Values"
            ])
            
            # Data rows
            for log in logs:
                writer.writerow([
                    log.id,
                    log.created_at.isoformat(),
                    log.user_id,
                    log.action,
                    log.resource_type,
                    log.resource_id,
                    log.ip_address,
                    json.dumps(log.old_values) if log.old_values else "",
                    json.dumps(log.new_values) if log.new_values else ""
                ])
                
            return output.getvalue()
            
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
    async def cleanup_old_logs(self, db: AsyncSession, days_to_keep: int = 365):
        """
        Clean up old audit logs to manage database size
        
        Args:
            db: Database session
            days_to_keep: Number of days to keep logs
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # This would delete old logs
        # For safety, we'll just log the action for now
        logger.info(f"Would delete audit logs older than {cutoff_date}")
        
        # Actual deletion would be:
        # await db.execute(
        #     delete(AuditLog).where(AuditLog.created_at < cutoff_date)
        # )
        # await db.commit()