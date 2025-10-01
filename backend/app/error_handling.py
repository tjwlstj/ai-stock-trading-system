"""
Enhanced Error Handling System for AI Stock Trading System
Provides comprehensive error handling, fallback mechanisms, and error recovery
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from enum import Enum
import asyncio
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories for better classification"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    EXTERNAL_API = "external_api"
    DATABASE = "database"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    NETWORK = "network"

class ErrorResponse(BaseModel):
    """Standardized error response model"""
    error: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    correlation_id: Optional[str] = None
    timestamp: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    retry_after: Optional[int] = None

class APIError(Exception):
    """Base API error class"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.status_code = status_code
        self.details = details or {}
        self.suggestions = suggestions or []
        super().__init__(message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            status_code=400,
            details=details,
            suggestions=["Check your input parameters", "Refer to API documentation"]
        )

class ExternalAPIError(APIError):
    """External API error"""
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service} API error: {message}",
            category=ErrorCategory.EXTERNAL_API,
            severity=ErrorSeverity.HIGH,
            status_code=503,
            details=details,
            suggestions=[
                "Try again in a few moments",
                "Check if the external service is operational",
                "Contact support if the issue persists"
            ]
        )

class DatabaseError(APIError):
    """Database error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Database error: {message}",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            status_code=503,
            details=details,
            suggestions=[
                "Try again in a few moments",
                "Contact support if the issue persists"
            ]
        )

class RateLimitError(APIError):
    """Rate limit error"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            status_code=429,
            suggestions=[
                f"Wait {retry_after} seconds before retrying",
                "Reduce request frequency",
                "Consider upgrading your plan for higher limits"
            ]
        )
        self.retry_after = retry_after

class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
    
    def create_error_response(
        self, 
        error: Union[APIError, Exception], 
        request: Optional[Request] = None
    ) -> ErrorResponse:
        """Create standardized error response"""
        
        correlation_id = None
        if request and hasattr(request.state, 'correlation_id'):
            correlation_id = request.state.correlation_id
        
        if isinstance(error, APIError):
            return ErrorResponse(
                error=error.__class__.__name__,
                message=error.message,
                category=error.category,
                severity=error.severity,
                correlation_id=correlation_id,
                timestamp=datetime.utcnow().isoformat(),
                details=error.details,
                suggestions=error.suggestions,
                retry_after=getattr(error, 'retry_after', None)
            )
        else:
            # Handle unexpected errors
            return ErrorResponse(
                error="UnexpectedError",
                message="An unexpected error occurred",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                correlation_id=correlation_id,
                timestamp=datetime.utcnow().isoformat(),
                details={"original_error": str(error)},
                suggestions=["Contact support with the correlation ID"]
            )
    
    def log_error(
        self, 
        error: Union[APIError, Exception], 
        request: Optional[Request] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        """Log error with appropriate level and context"""
        
        context = {
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "correlation_id": getattr(request.state, 'correlation_id', None) if request else None,
            "path": request.url.path if request else None,
            "method": request.method if request else None,
            "client_ip": request.client.host if request and request.client else None,
            **(additional_context or {})
        }
        
        if isinstance(error, APIError):
            if error.severity == ErrorSeverity.CRITICAL:
                logger.critical(f"Critical error: {error.message}", extra=context)
            elif error.severity == ErrorSeverity.HIGH:
                logger.error(f"High severity error: {error.message}", extra=context)
            elif error.severity == ErrorSeverity.MEDIUM:
                logger.warning(f"Medium severity error: {error.message}", extra=context)
            else:
                logger.info(f"Low severity error: {error.message}", extra=context)
        else:
            logger.error(f"Unexpected error: {str(error)}", extra=context, exc_info=True)
    
    def increment_error_count(self, error_key: str):
        """Increment error count for circuit breaker logic"""
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def should_circuit_break(self, service: str, threshold: int = 5) -> bool:
        """Check if circuit breaker should activate"""
        return self.error_counts.get(service, 0) >= threshold
    
    def reset_circuit_breaker(self, service: str):
        """Reset circuit breaker for a service"""
        self.error_counts[service] = 0

class FallbackManager:
    """Manages fallback mechanisms for external services"""
    
    def __init__(self):
        self.fallback_data_cache: Dict[str, Any] = {}
        self.service_status: Dict[str, bool] = {}
    
    async def get_stock_data_with_fallback(self, symbol: str) -> Dict[str, Any]:
        """Get stock data with fallback mechanisms"""
        
        # Primary: Yahoo Finance
        try:
            data = await self._fetch_yahoo_finance(symbol)
            self.service_status["yahoo_finance"] = True
            return data
        except Exception as e:
            logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
            self.service_status["yahoo_finance"] = False
        
        # Fallback 1: Alpha Vantage (if configured)
        try:
            data = await self._fetch_alpha_vantage(symbol)
            self.service_status["alpha_vantage"] = True
            return data
        except Exception as e:
            logger.warning(f"Alpha Vantage failed for {symbol}: {e}")
            self.service_status["alpha_vantage"] = False
        
        # Fallback 2: Cached data
        cached_data = self.fallback_data_cache.get(symbol)
        if cached_data:
            logger.info(f"Using cached data for {symbol}")
            cached_data["is_cached"] = True
            cached_data["cache_warning"] = "Data may be outdated due to service unavailability"
            return cached_data
        
        # Final fallback: Error with suggestions
        raise ExternalAPIError(
            service="Stock Data",
            message=f"Unable to fetch data for {symbol} from any source",
            details={
                "symbol": symbol,
                "attempted_sources": ["yahoo_finance", "alpha_vantage", "cache"],
                "service_status": self.service_status
            }
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def _fetch_yahoo_finance(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from Yahoo Finance with retry logic"""
        import yfinance as yf
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                raise ExternalAPIError("Yahoo Finance", f"No data available for {symbol}")
            
            latest = hist.iloc[-1]
            data = {
                "symbol": symbol,
                "price": float(latest['Close']),
                "change": float(latest['Close'] - latest['Open']),
                "change_percent": float((latest['Close'] - latest['Open']) / latest['Open'] * 100),
                "volume": int(latest['Volume']),
                "timestamp": datetime.now().isoformat(),
                "source": "yahoo_finance"
            }
            
            # Cache successful data
            self.fallback_data_cache[symbol] = data
            
            return data
            
        except Exception as e:
            raise ExternalAPIError("Yahoo Finance", str(e))
    
    async def _fetch_alpha_vantage(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from Alpha Vantage (placeholder implementation)"""
        # This would require Alpha Vantage API key and implementation
        raise ExternalAPIError("Alpha Vantage", "Not implemented")
    
    async def get_ai_analysis_with_fallback(
        self, 
        symbol: str, 
        stock_data: Dict[str, Any],
        analysis_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get AI analysis with fallback mechanisms"""
        
        # Primary: OpenAI GPT-4
        try:
            analysis = await self._get_openai_analysis(symbol, stock_data, analysis_request)
            self.service_status["openai"] = True
            return analysis
        except Exception as e:
            logger.warning(f"OpenAI analysis failed for {symbol}: {e}")
            self.service_status["openai"] = False
        
        # Fallback 1: Simplified rule-based analysis
        try:
            analysis = await self._get_rule_based_analysis(symbol, stock_data)
            self.service_status["rule_based"] = True
            return analysis
        except Exception as e:
            logger.warning(f"Rule-based analysis failed for {symbol}: {e}")
            self.service_status["rule_based"] = False
        
        # Final fallback: Basic analysis
        return {
            "symbol": symbol,
            "analysis": "Unable to generate detailed analysis due to service unavailability",
            "recommendation": "HOLD",
            "confidence": 0.1,
            "reasoning": "Fallback analysis due to AI service unavailability",
            "is_fallback": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_openai_analysis(
        self, 
        symbol: str, 
        stock_data: Dict[str, Any],
        analysis_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get analysis from OpenAI (placeholder)"""
        # This would integrate with the actual OpenAI client
        raise ExternalAPIError("OpenAI", "Implementation needed")
    
    async def _get_rule_based_analysis(
        self, 
        symbol: str, 
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simple rule-based analysis as fallback"""
        
        price = stock_data.get("price", 0)
        change_percent = stock_data.get("change_percent", 0)
        
        # Simple rules
        if change_percent > 5:
            recommendation = "STRONG_BUY"
            confidence = 0.6
        elif change_percent > 2:
            recommendation = "BUY"
            confidence = 0.5
        elif change_percent < -5:
            recommendation = "STRONG_SELL"
            confidence = 0.6
        elif change_percent < -2:
            recommendation = "SELL"
            confidence = 0.5
        else:
            recommendation = "HOLD"
            confidence = 0.4
        
        return {
            "symbol": symbol,
            "analysis": f"Rule-based analysis for {symbol}",
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": f"Based on {change_percent:.2f}% price change",
            "is_fallback": True,
            "fallback_type": "rule_based",
            "timestamp": datetime.now().isoformat()
        }

class HealthChecker:
    """System health monitoring and checks"""
    
    def __init__(self):
        self.service_health: Dict[str, Dict[str, Any]] = {}
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            from .database import get_db_session
            from sqlalchemy import text
            import time
            
            start_time = time.time()
            async with get_db_session() as session:
                await session.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000
            
            status = "healthy" if response_time < 100 else "degraded"
            
            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def check_external_services_health(self) -> Dict[str, Any]:
        """Check external services health"""
        services = {}
        
        # Check Yahoo Finance
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://finance.yahoo.com")
                services["yahoo_finance"] = {
                    "status": "healthy" if response.status_code == 200 else "degraded",
                    "response_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            services["yahoo_finance"] = {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        # Check OpenAI (if configured)
        try:
            from .settings import settings
            if settings.OPENAI_API_KEY:
                # Simple API check (would need actual implementation)
                services["openai"] = {
                    "status": "configured",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                services["openai"] = {
                    "status": "not_configured",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            services["openai"] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        return services
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health"""
        
        db_health = await self.check_database_health()
        services_health = await self.check_external_services_health()
        
        # Determine overall status
        overall_status = "healthy"
        if db_health["status"] == "unhealthy":
            overall_status = "unhealthy"
        elif any(service.get("status") == "unhealthy" for service in services_health.values()):
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "database": db_health,
            "external_services": services_health,
            "timestamp": datetime.now().isoformat()
        }

# Global instances
error_handler = ErrorHandler()
fallback_manager = FallbackManager()
health_checker = HealthChecker()

async def handle_api_error(request: Request, exc: Exception) -> JSONResponse:
    """Global API error handler"""
    
    error_handler.log_error(exc, request)
    error_response = error_handler.create_error_response(exc, request)
    
    status_code = 500
    if isinstance(exc, APIError):
        status_code = exc.status_code
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.dict()
    )
