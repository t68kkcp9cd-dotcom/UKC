"""
Application configuration management using Pydantic Settings
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Ultimate Kitchen Compendium"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment")
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")
    
    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for encryption"
    )
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="JWT secret key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION_MINUTES: int = Field(default=10080, description="JWT expiration in minutes")
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=30, description="JWT refresh expiration in days")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://ukc:ukc@localhost:5432/ukc_db",
        description="Database connection URL"
    )
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=30, description="Database max overflow")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis connection pool size")
    
    # Ollama AI
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama base URL")
    OLLAMA_CHAT_MODEL: str = Field(default="phi3:mini", description="Default chat model")
    OLLAMA_RECIPE_MODEL: str = Field(default="llama2:7b", description="Recipe processing model")
    OLLAMA_TIMEOUT: int = Field(default=60, description="Ollama request timeout")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="./uploads", description="Upload directory")
    MAX_UPLOAD_SIZE: int = Field(default=10485760, description="Maximum upload size in bytes")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "webp", "pdf"],
        description="Allowed file extensions"
    )
    
    # External APIs
    OPENFOODFACTS_API_URL: str = Field(default="https://world.openfoodfacts.org/api/v0", description="OpenFoodFacts API URL")
    USDA_API_KEY: Optional[str] = Field(default=None, description="USDA API key")
    USDA_API_URL: str = Field(default="https://api.nal.usda.gov/fdc/v1", description="USDA API URL")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_BURST: int = Field(default=10, description="Rate limit burst")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")
    METRICS_PORT: int = Field(default=9090, description="Metrics port")
    
    # Features
    ENABLE_AI_FEATURES: bool = Field(default=True, description="Enable AI features")
    ENABLE_GAMIFICATION: bool = Field(default=True, description="Enable gamification")
    ENABLE_STORE_INTEGRATION: bool = Field(default=True, description="Enable store integration")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()