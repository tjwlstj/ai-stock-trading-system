"""
AI Stock Trading System - FastAPI Backend
Modern async backend with comprehensive error handling and monitoring
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .settings import settings
from .database import init_db, get_db_session
from .openai_client import OpenAIClient
from .models import StockAnalysisRequest, StockAnalysisResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global OpenAI client instance
openai_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global openai_client
    
    # Startup
    logger.info("Starting AI Stock Trading System Backend")
    
    # Initialize required directories
    from .utils.directories import initialize_app_directories
    initialize_app_directories()
    
    await init_db()
    
    if settings.OPENAI_API_KEY:
        openai_client = OpenAIClient(settings.OPENAI_API_KEY)
        logger.info("OpenAI client initialized")
        
        # Set OpenAI client for routers
        from .routers import stocks
        stocks.set_openai_client(openai_client)
    else:
        logger.warning("OpenAI API key not configured")
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend")

# Create FastAPI app
app = FastAPI(
    title="AI Stock Trading System API",
    description="Multi-agent AI-powered stock analysis and trading system",
    version="1.1.0",
    lifespan=lifespan
)

# Configure CORS origins from environment
cors_origins = []
if settings.CORS_ALLOW_ORIGINS:
    cors_origins = [origin.strip() for origin in settings.CORS_ALLOW_ORIGINS.split(",")]
else:
    # Default development origins
    cors_origins = [
        "http://localhost:5173",
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

logger.info(f"CORS origins configured: {cors_origins}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.APP_ENV == "development" else "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test database connection
        async with get_db_session() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.1.0",
            "environment": settings.APP_ENV,
            "services": {
                "database": "connected",
                "openai": "configured" if settings.OPENAI_API_KEY else "not_configured"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Include API routers
from .routers import stocks, portfolio

# Include routers
app.include_router(stocks.router)
app.include_router(portfolio.router)

@app.get("/api/config")
async def get_client_config():
    """Get client-safe configuration"""
    return {
        "backend_url": f"http://localhost:{settings.BACKEND_PORT}",
        "openai_model": settings.OPENAI_MODEL,
        "environment": settings.APP_ENV,
        "features": {
            "ai_analysis": bool(settings.OPENAI_API_KEY),
            "database": True,
            "real_time_data": True
        },
        "version": "1.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.APP_ENV == "development"
    )
