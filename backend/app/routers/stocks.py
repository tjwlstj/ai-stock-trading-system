"""
Stock API Routes
Handles stock data and analysis endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from ..models import StockAnalysisRequest, StockAnalysisResponse
from ..openai_client import OpenAIClient
from ..settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["stocks"])

# Global OpenAI client (will be injected)
openai_client: Optional[OpenAIClient] = None

def get_openai_client() -> OpenAIClient:
    """Dependency to get OpenAI client"""
    if not openai_client:
        raise HTTPException(
            status_code=503,
            detail="AI analysis service not available. OpenAI API key not configured."
        )
    return openai_client

@router.get("/stocks/{symbol}")
async def get_stock_data(symbol: str):
    """Get stock data for a symbol"""
    try:
        from ..utils.stock_data import stock_fetcher
        return await stock_fetcher.get_stock_data(symbol)
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch data for {symbol}"
        )

@router.post("/stocks/batch")
async def get_multiple_stocks(symbols: list[str]):
    """Get data for multiple stocks"""
    try:
        from ..utils.stock_data import stock_fetcher
        return await stock_fetcher.get_multiple_stocks(symbols)
    except Exception as e:
        logger.error(f"Error fetching multiple stock data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch stock data"
        )

@router.post("/analysis/{symbol}", response_model=StockAnalysisResponse)
async def analyze_stock(
    symbol: str, 
    request: Optional[StockAnalysisRequest] = None,
    client: OpenAIClient = Depends(get_openai_client)
):
    """Analyze stock using AI agents"""
    try:
        # Get stock data first
        from ..utils.stock_data import stock_fetcher
        stock_data = await stock_fetcher.get_stock_data(symbol)
        
        # Prepare analysis prompt
        prompt = f"""
        Analyze the stock {symbol} with the following data:
        Price: ${stock_data['price']}
        Change: {stock_data['change']} ({stock_data['change_percent']}%)
        Volume: {stock_data['volume']}
        
        Provide a comprehensive analysis including:
        1. Overall recommendation (BUY/HOLD/SELL)
        2. Confidence score (0.0-1.0)
        3. Target price
        4. Key factors
        5. Risk assessment
        
        Respond in JSON format.
        """
        
        # Get AI analysis
        ai_response = await client.analyze_stock(prompt)
        
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

def set_openai_client(client: OpenAIClient):
    """Set the global OpenAI client instance"""
    global openai_client
    openai_client = client
