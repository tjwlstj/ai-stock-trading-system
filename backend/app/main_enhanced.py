"""
Enhanced Main Application with Integrated Quality Management, Real-time Data, and Cost Optimization
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Import our enhanced modules
from .ai_quality_manager import (
    AIQualityMonitor, AIUsageOptimizer, AIResponseValidator, BatchAnalyzer,
    AnalysisLevel, ValidationResult, validate_and_monitor_response
)
from .realtime_data_manager import RealTimeDataManager, MarketStatus
from .cost_optimizer import (
    CostTracker, BudgetManager, CostOptimizer, CostReporter,
    track_ai_request_cost, check_budget_alerts
)
from .security import SecurityManager, RateLimiter, InputValidator
from .error_handling import ErrorHandler, CircuitBreaker, HealthMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models
class StockAnalysisRequest(BaseModel):
    symbol: str
    analysis_level: AnalysisLevel = AnalysisLevel.STANDARD
    force_refresh: bool = False
    include_technical: bool = True
    include_fundamental: bool = True
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Invalid stock symbol')
        return v.upper().strip()

class BatchAnalysisRequest(BaseModel):
    symbols: List[str]
    analysis_level: AnalysisLevel = AnalysisLevel.STANDARD
    max_concurrent: int = 5
    
    @validator('symbols')
    def validate_symbols(cls, v):
        if not v or len(v) > 50:  # Limit batch size
            raise ValueError('Invalid symbols list (max 50)')
        return [s.upper().strip() for s in v if s.strip()]

class AnalysisResponse(BaseModel):
    symbol: str
    recommendation: str
    confidence: float
    reasoning: str
    key_factors: List[str] = []
    risks: List[str] = []
    price_target: Optional[float] = None
    market_status: str
    data_freshness: Dict[str, Any]
    validation_result: str
    quality_score: float
    cost_info: Dict[str, Any]
    timestamp: datetime
    correlation_id: str

# Global instances
redis_client: Optional[redis.Redis] = None
realtime_manager: Optional[RealTimeDataManager] = None
ai_monitor: Optional[AIQualityMonitor] = None
security_manager: Optional[SecurityManager] = None
error_handler: Optional[ErrorHandler] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global redis_client, realtime_manager, ai_monitor, security_manager, error_handler
    
    # Startup
    logger.info("Starting AI Stock Trading System...")
    
    try:
        # Initialize Redis
        redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Running without Redis.")
        redis_client = None
    
    # Initialize managers
    realtime_manager = RealTimeDataManager(redis_client)
    ai_monitor = AIQualityMonitor(redis_client)
    security_manager = SecurityManager(redis_client)
    error_handler = ErrorHandler()
    
    # Start background tasks
    asyncio.create_task(periodic_budget_check())
    asyncio.create_task(periodic_health_check())
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if redis_client:
        await redis_client.close()
    logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="AI Stock Trading System - Enhanced",
    description="Multi-Agent AI Stock Analysis with Quality Management and Cost Optimization",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
async def get_correlation_id(request: Request) -> str:
    """Generate or extract correlation ID for request tracking"""
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    return correlation_id

async def get_user_id(request: Request) -> Optional[str]:
    """Extract user ID from request (placeholder for authentication)"""
    # In a real application, this would extract from JWT token or session
    return request.headers.get("X-User-ID", "anonymous")

# Background tasks
async def periodic_budget_check():
    """Periodic budget monitoring"""
    while True:
        try:
            alerts = await check_budget_alerts()
            if alerts:
                for alert in alerts:
                    logger.warning(f"Budget Alert: {alert}")
                    # In production, you'd send notifications here
        except Exception as e:
            logger.error(f"Budget check failed: {e}")
        
        await asyncio.sleep(300)  # Check every 5 minutes

async def periodic_health_check():
    """Periodic system health monitoring"""
    while True:
        try:
            # Check system health
            health_status = await error_handler.health_monitor.get_system_health()
            if health_status['status'] != 'healthy':
                logger.warning(f"System health issue: {health_status}")
        except Exception as e:
            logger.error(f"Health check failed: {e}")
        
        await asyncio.sleep(60)  # Check every minute

# API Routes
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    try:
        health_status = await error_handler.health_monitor.get_system_health()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/v1/market-status/{symbol}")
async def get_market_status(
    symbol: str,
    correlation_id: str = Depends(get_correlation_id)
):
    """Get current market status for a symbol"""
    try:
        # Input validation
        symbol = InputValidator.sanitize_symbol(symbol)
        
        # Get market status
        status = realtime_manager.get_market_status(symbol)
        
        # Get data freshness info
        freshness_info = await realtime_manager.get_data_freshness_info(symbol)
        
        return {
            "symbol": symbol,
            "market_status": status.value,
            "data_freshness": freshness_info,
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market status error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_stock(
    request: StockAnalysisRequest,
    background_tasks: BackgroundTasks,
    correlation_id: str = Depends(get_correlation_id),
    user_id: str = Depends(get_user_id)
):
    """Analyze a single stock with enhanced quality management"""
    
    start_time = time.time()
    
    try:
        # Rate limiting
        await security_manager.rate_limiter.check_rate_limit(
            f"user:{user_id}", requests_per_minute=10
        )
        
        # Input validation and sanitization
        symbol = InputValidator.sanitize_symbol(request.symbol)
        
        # Get real-time stock data
        stock_quote = await realtime_manager.get_stock_quote(
            symbol, force_refresh=request.force_refresh
        )
        
        # Prepare stock data for AI analysis
        stock_data = {
            'symbol': symbol,
            'price': stock_quote.price,
            'change': stock_quote.change,
            'change_percent': stock_quote.change_percent,
            'volume': stock_quote.volume,
            'market_cap': stock_quote.market_cap,
            'pe_ratio': stock_quote.pe_ratio
        }
        
        # Generate AI analysis (placeholder - integrate with your AI service)
        ai_response = await generate_ai_analysis(
            symbol, stock_data, request.analysis_level, correlation_id
        )
        
        # Validate and monitor AI response
        response_time = time.time() - start_time
        validation_result, issues, quality_score = await validate_and_monitor_response(
            ai_response, stock_data, "gpt-4o-mini", 
            ai_response.get('input_tokens', 0),
            ai_response.get('output_tokens', 0),
            response_time
        )
        
        # Track costs
        background_tasks.add_task(
            track_ai_request_cost,
            "gpt-4o-mini",
            ai_response.get('input_tokens', 0),
            ai_response.get('output_tokens', 0),
            user_id=user_id,
            session_id=correlation_id
        )
        
        # Get data freshness info
        freshness_info = await realtime_manager.get_data_freshness_info(symbol)
        
        # Prepare response
        response = AnalysisResponse(
            symbol=symbol,
            recommendation=ai_response.get('recommendation', 'HOLD'),
            confidence=ai_response.get('confidence', 0.5),
            reasoning=ai_response.get('reasoning', ''),
            key_factors=ai_response.get('key_factors', []),
            risks=ai_response.get('risks', []),
            price_target=ai_response.get('price_target'),
            market_status=stock_quote.market_status.value,
            data_freshness=freshness_info,
            validation_result=validation_result.value,
            quality_score=quality_score,
            cost_info={
                'estimated_cost': ai_response.get('estimated_cost', 0),
                'tokens_used': ai_response.get('input_tokens', 0) + ai_response.get('output_tokens', 0)
            },
            timestamp=datetime.now(),
            correlation_id=correlation_id
        )
        
        # Log successful analysis
        logger.info(f"Analysis completed for {symbol} (correlation_id: {correlation_id})")
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed for {request.symbol}: {e} (correlation_id: {correlation_id})")
        
        # Handle different types of errors
        if "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        elif "budget" in str(e).lower():
            raise HTTPException(status_code=402, detail="Budget limit exceeded")
        else:
            raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/api/v1/analyze-batch")
async def analyze_batch(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    correlation_id: str = Depends(get_correlation_id),
    user_id: str = Depends(get_user_id)
):
    """Analyze multiple stocks efficiently"""
    
    try:
        # Rate limiting for batch requests
        await security_manager.rate_limiter.check_rate_limit(
            f"batch:{user_id}", requests_per_minute=2
        )
        
        # Validate symbols
        symbols = [InputValidator.sanitize_symbol(s) for s in request.symbols]
        
        # Use batch analyzer for efficiency
        batch_analyzer = BatchAnalyzer(None, AIUsageOptimizer(redis_client))  # AI client would be injected
        
        results = await batch_analyzer.analyze_portfolio(symbols, request.analysis_level)
        
        # Get real-time data for all symbols
        stock_quotes = await realtime_manager.get_portfolio_quotes(symbols)
        
        # Prepare batch response
        batch_response = {
            'correlation_id': correlation_id,
            'timestamp': datetime.now().isoformat(),
            'total_symbols': len(symbols),
            'successful_analyses': len(results),
            'results': {}
        }
        
        for symbol in symbols:
            if symbol in results and symbol in stock_quotes:
                analysis = results[symbol]
                quote = stock_quotes[symbol]
                
                batch_response['results'][symbol] = {
                    'recommendation': analysis.get('recommendation', 'HOLD'),
                    'confidence': analysis.get('confidence', 0.5),
                    'reasoning': analysis.get('reasoning', ''),
                    'market_status': quote.market_status.value,
                    'current_price': quote.price,
                    'change_percent': quote.change_percent,
                    'is_cached': analysis.get('is_cached', False)
                }
        
        return batch_response
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e} (correlation_id: {correlation_id})")
        raise HTTPException(status_code=500, detail="Batch analysis failed")

@app.get("/api/v1/cost-summary")
async def get_cost_summary(
    days: int = 7,
    user_id: str = Depends(get_user_id)
):
    """Get cost summary and optimization recommendations"""
    
    try:
        # Get cost optimization recommendations
        optimization_report = await CostOptimizer(CostTracker()).analyze_usage_patterns(days)
        
        # Get current budget status
        budget_status = await BudgetManager(CostTracker(), redis_client).get_budget_status()
        
        return {
            'period_days': days,
            'optimization_report': optimization_report,
            'budget_status': budget_status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cost summary failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate cost summary")

@app.get("/api/v1/quality-metrics")
async def get_quality_metrics():
    """Get AI quality metrics and system performance"""
    
    try:
        # Get daily summary from AI monitor
        daily_summary = await ai_monitor.get_daily_summary()
        
        # Check for quality alerts
        should_alert, alerts = ai_monitor.should_trigger_alert()
        
        return {
            'daily_summary': daily_summary,
            'quality_alerts': alerts if should_alert else [],
            'system_status': 'healthy' if not should_alert else 'warning',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Quality metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quality metrics")

@app.websocket("/ws/realtime/{symbol}")
async def websocket_realtime_data(websocket, symbol: str):
    """WebSocket endpoint for real-time stock data"""
    
    await websocket.accept()
    
    try:
        symbol = InputValidator.sanitize_symbol(symbol)
        
        async def send_update(quote):
            await websocket.send_json({
                'symbol': quote.symbol,
                'price': quote.price,
                'change': quote.change,
                'change_percent': quote.change_percent,
                'volume': quote.volume,
                'market_status': quote.market_status.value,
                'timestamp': quote.timestamp.isoformat()
            })
        
        # Subscribe to updates
        await realtime_manager.subscribe_to_updates(symbol, send_update)
        
        # Keep connection alive
        while True:
            try:
                await websocket.receive_text()
            except:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
    finally:
        # Unsubscribe
        if 'send_update' in locals():
            realtime_manager.unsubscribe_from_updates(symbol, send_update)

# Placeholder AI analysis function (integrate with your AI service)
async def generate_ai_analysis(
    symbol: str, 
    stock_data: Dict[str, Any], 
    level: AnalysisLevel,
    correlation_id: str
) -> Dict[str, Any]:
    """Generate AI analysis (placeholder implementation)"""
    
    # This is a placeholder - integrate with your actual AI service
    # The real implementation would call OpenAI API with optimized prompts
    
    await asyncio.sleep(0.1)  # Simulate AI processing time
    
    return {
        'recommendation': 'HOLD',
        'confidence': 0.75,
        'reasoning': f'Based on current market conditions and {symbol} fundamentals, maintaining current position is recommended.',
        'key_factors': ['Market volatility', 'Sector performance', 'Technical indicators'],
        'risks': ['Market uncertainty', 'Sector rotation'],
        'price_target': stock_data['price'] * 1.05,
        'input_tokens': 150,
        'output_tokens': 100,
        'estimated_cost': 0.0001
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
