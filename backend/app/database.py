"""
Database connection and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import asyncio
import logging

from app.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=300,
    future=True
)

# Create session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Global database instance for dependency injection
database = None


async def init_db():
    """Initialize database connection and create tables"""
    global database
    
    try:
        # Test connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        logger.info("Database connection established")
        
        # Create tables (in production, use migrations)
        if settings.ENVIRONMENT == "development":
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections"""
    global database
    
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")


async def get_db() -> AsyncSession:
    """Dependency for getting database sessions"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Database session decorator
def with_db(func):
    """Decorator to inject database session"""
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                result = await func(session, *args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    return wrapper