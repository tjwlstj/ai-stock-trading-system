"""
Retry Utilities
Robust retry mechanisms for external API calls and data collection
"""

import asyncio
import logging
from typing import Callable, Any, Optional, Type, Union, List
from functools import wraps
import httpx
from tenacity import (
    retry, 
    wait_exponential, 
    stop_after_attempt, 
    retry_if_exception_type,
    before_sleep_log,
    after_log
)

logger = logging.getLogger(__name__)

# Common retry configurations
NETWORK_RETRY = retry(
    wait=wait_exponential(multiplier=0.5, min=1, max=10),
    stop=stop_after_attempt(4),
    retry=retry_if_exception_type((
        httpx.RequestError, 
        httpx.HTTPStatusError,
        asyncio.TimeoutError,
        ConnectionError
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    after=after_log(logger, logging.INFO)
)

API_RETRY = retry(
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type((
        httpx.HTTPStatusError,
        httpx.RequestError,
        asyncio.TimeoutError
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)

DATABASE_RETRY = retry(
    wait=wait_exponential(multiplier=0.3, min=0.5, max=5),
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)

class RetryableError(Exception):
    """Base class for retryable errors"""
    pass

class NonRetryableError(Exception):
    """Base class for non-retryable errors"""
    pass

def safe_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], tuple] = Exception,
    non_retryable: Optional[Union[Type[Exception], tuple]] = None
):
    """
    Decorator for safe retry with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier
        exceptions: Exception types to retry on
        non_retryable: Exception types that should not be retried
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if this is a non-retryable error
                    if non_retryable and isinstance(e, non_retryable):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    # Check if this is a retryable error
                    if not isinstance(e, exceptions):
                        logger.error(f"Non-retryable exception type in {func.__name__}: {e}")
                        raise
                    
                    # Don't sleep on the last attempt
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if non_retryable and isinstance(e, non_retryable):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    if not isinstance(e, exceptions):
                        logger.error(f"Non-retryable exception type in {func.__name__}: {e}")
                        raise
                    
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class CircuitBreaker:
    """
    Circuit breaker pattern implementation for external service calls
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise NonRetryableError("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise NonRetryableError("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        import time
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call"""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

# Pre-configured decorators for common use cases
yahoo_finance_retry = safe_retry(
    max_attempts=4,
    delay=1.0,
    backoff=2.0,
    exceptions=(httpx.RequestError, httpx.HTTPStatusError, asyncio.TimeoutError),
    non_retryable=(httpx.HTTPStatusError,)  # Don't retry on 4xx errors
)

openai_retry = safe_retry(
    max_attempts=5,
    delay=2.0,
    backoff=2.0,
    exceptions=(httpx.RequestError, httpx.HTTPStatusError, asyncio.TimeoutError),
    non_retryable=(httpx.HTTPStatusError,)  # Don't retry on auth errors
)

database_retry = safe_retry(
    max_attempts=3,
    delay=0.5,
    backoff=1.5,
    exceptions=(Exception,),
    non_retryable=(ValueError, TypeError)
)
