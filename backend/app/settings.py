"""
Application Settings
Centralized configuration management with environment variable support
"""

import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from root .env file
ROOT_ENV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if os.path.exists(ROOT_ENV):
    load_dotenv(ROOT_ENV, override=False)

class Settings(BaseModel):
    """Application settings with validation"""
    
    # Application
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/stock_data.db")
    DB_URL: str = os.getenv("DB_URL", f"sqlite:///{DATABASE_PATH}")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "30"))
    
    # Stock Data API
    STOCK_API_KEY: str = os.getenv("STOCK_API_KEY", "")
    YAHOO_FINANCE_TIMEOUT: int = int(os.getenv("YAHOO_FINANCE_TIMEOUT", "10"))
    
    # CORS Configuration
    CORS_ALLOW_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Optional services
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.APP_ENV.lower() in ("dev", "development")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.APP_ENV.lower() in ("prod", "production")
    
    @property
    def async_db_url(self) -> str:
        """Get async database URL"""
        if self.DB_URL.startswith("sqlite://"):
            return self.DB_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return self.DB_URL
    
    def validate_required_settings(self) -> List[str]:
        """Validate required settings and return missing ones"""
        missing = []
        
        if not self.OPENAI_API_KEY and self.APP_ENV != "testing":
            missing.append("OPENAI_API_KEY")
        
        return missing

# Global settings instance
settings = Settings()

# Validate settings on import
if __name__ != "__main__":
    missing_settings = settings.validate_required_settings()
    if missing_settings:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Missing required settings: {missing_settings}")
