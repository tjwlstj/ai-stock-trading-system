"""
Enhanced Security Module for AI Stock Trading System
Provides comprehensive security features including rate limiting, input validation, and audit logging
"""

import hashlib
import hmac
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
import logging
import json
import re

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

# Security configuration
class SecurityConfig:
    """Security configuration settings"""
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_BURST = 10
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Input validation
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB
    MAX_STRING_LENGTH = 1000
    ALLOWED_SYMBOLS_PATTERN = r'^[A-Z0-9\.\-]{1,10}$'
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs to all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # Add to request state
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
            
        return response

class RateLimiter:
    """Redis-based rate limiter with sliding window"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.fallback_cache: Dict[str, List[float]] = {}
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit key"""
        return f"rate_limit:{identifier}:{endpoint}"
    
    def _cleanup_fallback_cache(self, key: str, window: int):
        """Clean up expired entries in fallback cache"""
        if key in self.fallback_cache:
            current_time = time.time()
            self.fallback_cache[key] = [
                timestamp for timestamp in self.fallback_cache[key]
                if current_time - timestamp < window
            ]
    
    async def is_allowed(
        self, 
        identifier: str, 
        endpoint: str, 
        limit: int = SecurityConfig.RATE_LIMIT_PER_MINUTE,
        window: int = SecurityConfig.RATE_LIMIT_WINDOW
    ) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed under rate limit"""
        
        key = self._get_key(identifier, endpoint)
        current_time = time.time()
        
        if self.redis_client:
            try:
                # Use Redis sliding window
                pipe = self.redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, current_time - window)
                pipe.zcard(key)
                pipe.zadd(key, {str(current_time): current_time})
                pipe.expire(key, window)
                results = pipe.execute()
                
                current_requests = results[1]
                allowed = current_requests < limit
                
                return allowed, {
                    "limit": limit,
                    "remaining": max(0, limit - current_requests - 1),
                    "reset_time": int(current_time + window),
                    "retry_after": window if not allowed else None
                }
                
            except Exception as e:
                logger.warning(f"Redis rate limiter failed, using fallback: {e}")
        
        # Fallback to in-memory rate limiting
        self._cleanup_fallback_cache(key, window)
        
        if key not in self.fallback_cache:
            self.fallback_cache[key] = []
        
        self.fallback_cache[key].append(current_time)
        current_requests = len(self.fallback_cache[key])
        allowed = current_requests <= limit
        
        return allowed, {
            "limit": limit,
            "remaining": max(0, limit - current_requests),
            "reset_time": int(current_time + window),
            "retry_after": window if not allowed else None
        }

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    @staticmethod
    def validate_stock_symbol(symbol: str) -> str:
        """Validate and sanitize stock symbol"""
        if not symbol:
            raise HTTPException(status_code=400, detail="Stock symbol is required")
        
        # Remove whitespace and convert to uppercase
        symbol = symbol.strip().upper()
        
        # Validate format
        if not re.match(SecurityConfig.ALLOWED_SYMBOLS_PATTERN, symbol):
            raise HTTPException(
                status_code=400, 
                detail="Invalid stock symbol format. Use only letters, numbers, dots, and hyphens."
            )
        
        # Check length
        if len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Stock symbol too long")
        
        return symbol
    
    @staticmethod
    def validate_string_input(value: str, field_name: str, max_length: int = None) -> str:
        """Validate and sanitize string input"""
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail=f"{field_name} must be a string")
        
        # Check length
        max_len = max_length or SecurityConfig.MAX_STRING_LENGTH
        if len(value) > max_len:
            raise HTTPException(
                status_code=400, 
                detail=f"{field_name} exceeds maximum length of {max_len}"
            )
        
        # Basic XSS prevention
        dangerous_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if pattern in value_lower:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid characters detected in {field_name}"
                )
        
        return value.strip()
    
    @staticmethod
    def sanitize_ai_input(text: str) -> str:
        """Sanitize input for AI models to prevent prompt injection"""
        if not text:
            return text
        
        # Remove potential prompt injection patterns
        dangerous_patterns = [
            r'ignore\s+previous\s+instructions',
            r'system\s*:',
            r'assistant\s*:',
            r'user\s*:',
            r'###\s*instruction',
            r'###\s*system',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Limit length
        if len(text) > 1000:
            text = text[:1000]
        
        return text.strip()

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
    
    def log_request(
        self, 
        request: Request, 
        user_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log incoming request for audit purposes"""
        
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": getattr(request.state, 'correlation_id', None),
            "event_type": "api_request",
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": {
                key: value for key, value in request.headers.items()
                if key.lower() not in ['authorization', 'cookie', 'x-api-key']
            },
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "user_id": user_id,
            "additional_data": additional_data or {}
        }
        
        self.logger.info(json.dumps(audit_data))
    
    def log_response(
        self, 
        request: Request, 
        status_code: int,
        response_time_ms: float,
        error: Optional[str] = None
    ):
        """Log response for audit purposes"""
        
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": getattr(request.state, 'correlation_id', None),
            "event_type": "api_response",
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "error": error
        }
        
        self.logger.info(json.dumps(audit_data))
    
    def log_security_event(
        self, 
        event_type: str, 
        request: Request,
        details: Dict[str, Any]
    ):
        """Log security-related events"""
        
        security_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": getattr(request.state, 'correlation_id', None),
            "event_type": f"security_{event_type}",
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "path": request.url.path,
            "details": details
        }
        
        self.logger.warning(json.dumps(security_data))

# Global instances
rate_limiter = RateLimiter()
input_validator = InputValidator()
audit_logger = AuditLogger()

def rate_limit(
    limit: int = SecurityConfig.RATE_LIMIT_PER_MINUTE,
    window: int = SecurityConfig.RATE_LIMIT_WINDOW,
    per: str = "ip"  # "ip" or "user"
):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Determine identifier
            if per == "ip":
                identifier = request.client.host if request.client else "unknown"
            else:
                identifier = "user"  # Could be extracted from auth token
            
            # Check rate limit
            allowed, info = await rate_limiter.is_allowed(
                identifier, 
                request.url.path, 
                limit, 
                window
            )
            
            if not allowed:
                audit_logger.log_security_event(
                    "rate_limit_exceeded",
                    request,
                    {"limit": limit, "window": window, "identifier": identifier}
                )
                
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": str(info["reset_time"]),
                        "Retry-After": str(info["retry_after"])
                    }
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Pydantic models for enhanced validation
class SecureStockRequest(BaseModel):
    """Secure stock request model with validation"""
    symbol: str
    
    @validator('symbol')
    def validate_symbol(cls, v):
        return input_validator.validate_stock_symbol(v)

class SecureAnalysisRequest(BaseModel):
    """Secure analysis request model with validation"""
    analysis_type: str = "comprehensive"
    confidence_threshold: float = 0.7
    include_technical: bool = True
    include_fundamental: bool = True
    custom_prompt: Optional[str] = None
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed_types = ['comprehensive', 'technical', 'fundamental', 'quick']
        if v not in allowed_types:
            raise ValueError(f"Analysis type must be one of: {allowed_types}")
        return v
    
    @validator('confidence_threshold')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        return v
    
    @validator('custom_prompt')
    def validate_custom_prompt(cls, v):
        if v:
            return input_validator.sanitize_ai_input(v)
        return v

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers (when behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive data in logs"""
    sensitive_keys = ['password', 'token', 'key', 'secret', 'authorization']
    
    masked_data = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            masked_data[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_data(value)
        else:
            masked_data[key] = value
    
    return masked_data
