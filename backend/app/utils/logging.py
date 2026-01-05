"""
Logging configuration and utilities
"""

import logging
import sys
from typing import Optional

from app.config import settings


def setup_logging():
    """Setup application logging configuration"""
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log") if settings.ENVIRONMENT == "production" else logging.NullHandler()
        ]
    )
    
    # Configure specific loggers
    # SQLAlchemy logger (reduce noise in production)
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.setLevel(logging.WARNING if not settings.DEBUG else logging.INFO)
    
    # Uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # App logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    return app_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)


def log_api_call(endpoint: str, method: str, status_code: int, duration_ms: float, user_id: Optional[str] = None):
    """Log API call metrics"""
    logger = get_logger("app.api")
    logger.info(
        f"API Call: {method} {endpoint} - {status_code} ({duration_ms:.2f}ms)",
        extra={
            "api_endpoint": endpoint,
            "api_method": method,
            "api_status_code": status_code,
            "api_duration_ms": duration_ms,
            "user_id": user_id
        }
    )


def log_database_query(query: str, duration_ms: float, user_id: Optional[str] = None):
    """Log database query metrics"""
    logger = get_logger("app.database")
    logger.debug(
        f"Database Query: ({duration_ms:.2f}ms) {query[:100]}...",
        extra={
            "db_query": query,
            "db_duration_ms": duration_ms,
            "user_id": user_id
        }
    )


def log_security_event(event_type: str, details: dict, user_id: Optional[str] = None, ip_address: Optional[str] = None):
    """Log security-related events"""
    logger = get_logger("app.security")
    logger.warning(
        f"Security Event: {event_type}",
        extra={
            "security_event_type": event_type,
            "security_details": details,
            "user_id": user_id,
            "ip_address": ip_address
        }
    )


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        # Add structured data if available
        if hasattr(record, 'extra_data'):
            record.msg = f"{record.msg} | {record.extra_data}"
        return super().format(record)