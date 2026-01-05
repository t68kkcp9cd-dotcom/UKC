"""
Ultimate Kitchen Compendium - Main Application
FastAPI backend server with comprehensive kitchen management features
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.v1 import auth, users, inventory, recipes, meal_plans, shopping, ai, websocket
from app.database import init_db, close_db
from app.utils.logging import setup_logging
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events"""
    # Startup
    setup_logging()
    await init_db()
    
    # Initialize AI models if available
    from app.services.ai_service import AIService
    app.state.ai_service = AIService()
    await app.state.ai_service.initialize_models()
    
    yield
    
    # Shutdown
    await close_db()
    if hasattr(app.state, 'ai_service'):
        await app.state.ai_service.cleanup()


# Create FastAPI application
app = FastAPI(
    title="Ultimate Kitchen Compendium API",
    description="Comprehensive kitchen management system API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host protection in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)


# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(recipes.router, prefix="/api/v1/recipes", tags=["Recipes"])
app.include_router(meal_plans.router, prefix="/api/v1/meal-plans", tags=["Meal Planning"])
app.include_router(shopping.router, prefix="/api/v1/shopping", tags=["Shopping"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Services"])
app.include_router(websocket.router, prefix="/ws")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": await check_database(),
            "redis": await check_redis(),
            "ollama": await check_ollama()
        }
    }


async def check_database() -> dict:
    """Check database connectivity"""
    try:
        from app.database import database
        await database.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_redis() -> dict:
    """Check Redis connectivity"""
    try:
        from app.services.cache_service import CacheService
        cache = CacheService()
        await cache.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_ollama() -> dict:
    """Check Ollama service connectivity"""
    try:
        from app.utils.ollama_client import OllamaClient
        client = OllamaClient()
        await client.health_check()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )