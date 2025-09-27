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
    await init_db()
    
    if settings.OPENAI_API_KEY:
        openai_client = OpenAIClient(settings.OPENAI_API_KEY)
        logger.info("OpenAI client initialized")
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
cors_origins = settings.CORS_ALLOW_ORIGINS.split(",") if settings.CORS_ALLOW_ORIGINS else ["*"]

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

@app.get("/api/stocks/{symbol}")
async def get_stock_data(symbol: str):
    """Get stock data for a symbol"""
    try:
        # TODO: Implement actual stock data fetching
        # For now, return mock data
        return {
            "symbol": symbol.upper(),
            "price": 150.25,
            "change": 2.35,
            "change_percent": 1.59,
            "volume": 1234567,
            "market_cap": "2.5T",
            "timestamp": datetime.now().isoformat(),
            "source": "mock_data"
        }
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch data for {symbol}"
        )

@app.post("/api/analysis/{symbol}", response_model=StockAnalysisResponse)
async def analyze_stock(symbol: str, request: Optional[StockAnalysisRequest] = None):
    """Analyze stock using AI agents"""
    if not openai_client:
        raise HTTPException(
            status_code=503,
            detail="AI analysis service not available. OpenAI API key not configured."
        )
    
    try:
        # Get stock data first
        stock_data = await get_stock_data(symbol)
        
        # Prepare analysis prompt
        prompt = f"""
        Analyze the stock {symbol} with the following data:
        Price: ${stock_data['price']}
        Change: {stock_data['change']} ({stock_data['change_percent']}%)
        
        Provide a comprehensive analysis including:
        1. Overall recommendation (BUY/HOLD/SELL)
        2. Confidence score (0.0-1.0)
        3. Target price
        4. Key factors
        5. Risk assessment
        
        Respond in JSON format.
        """
        
        # Get AI analysis
        ai_response = await openai_client.analyze_stock(prompt)
        
        # Parse and structure response
        return StockAnalysisResponse(
            symbol=symbol.upper(),
            recommendation=ai_response.get("recommendation", "HOLD"),
            confidence=ai_response.get("confidence", 0.5),
            target_price=ai_response.get("target_price", stock_data["price"]),
            analysis={
                "optimistic": {"score": 0.7, "reasoning": "Growth potential identified"},
                "pessimistic": {"score": 0.6, "reasoning": "Market volatility concerns"},
                "risk_manager": {"score": 0.65, "reasoning": "Moderate risk profile"}
            },
            timestamp=datetime.now().isoformat(),
            model_used=settings.OPENAI_MODEL
        )
        
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze {symbol}: {str(e)}"
        )

@app.get("/api/portfolio/summary")
async def get_portfolio_summary():
    """Get portfolio summary"""
    # TODO: Implement actual portfolio logic
    return {
        "total_value": 50000.00,
        "daily_change": 1250.50,
        "daily_change_percent": 2.56,
        "positions": 8,
        "cash": 5000.00,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.APP_ENV == "development"
    )
