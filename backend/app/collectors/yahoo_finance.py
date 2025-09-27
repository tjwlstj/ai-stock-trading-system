"""
Yahoo Finance Data Collector
Robust data collection with error handling, caching, and fallback mechanisms
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import httpx
import pandas as pd
from dataclasses import dataclass
import json

from ..utils.retry import yahoo_finance_retry, CircuitBreaker
from ..utils.market_time import should_fetch_realtime_data, get_data_freshness_requirement
from ..settings import settings

logger = logging.getLogger(__name__)

@dataclass
class StockQuote:
    """Stock quote data structure"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[str] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    timestamp: datetime = None
    source: str = "yahoo_finance"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'pe_ratio': self.pe_ratio,
            'dividend_yield': self.dividend_yield,
            'fifty_two_week_high': self.fifty_two_week_high,
            'fifty_two_week_low': self.fifty_two_week_low,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source
        }

class YahooFinanceCollector:
    """
    Yahoo Finance data collector with resilience features
    """
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com"
        self.timeout = settings.YAHOO_FINANCE_TIMEOUT
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes default TTL
        
        # Circuit breaker for Yahoo Finance API
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=300,  # 5 minutes
            expected_exception=httpx.HTTPStatusError
        )
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid"""
        if symbol not in self.cache:
            return False
        
        cached_data = self.cache[symbol]
        cache_time = cached_data.get('timestamp')
        
        if not cache_time:
            return False
        
        # Get freshness requirement based on market status
        freshness_seconds = get_data_freshness_requirement(symbol)
        age_seconds = (datetime.now() - cache_time).total_seconds()
        
        return age_seconds < freshness_seconds
    
    def _get_from_cache(self, symbol: str) -> Optional[StockQuote]:
        """Get data from cache if valid"""
        if self._is_cache_valid(symbol):
            cached_data = self.cache[symbol]
            logger.info(f"Using cached data for {symbol}")
            return cached_data['quote']
        return None
    
    def _store_in_cache(self, symbol: str, quote: StockQuote):
        """Store data in cache"""
        self.cache[symbol] = {
            'quote': quote,
            'timestamp': datetime.now()
        }
    
    @yahoo_finance_retry
    async def _fetch_quote_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch raw quote data from Yahoo Finance API"""
        url = f"{self.base_url}/v8/finance/chart/{symbol}"
        
        params = {
            'range': '1d',
            'interval': '1m',
            'includePrePost': 'true',
            'events': 'div,splits'
        }
        
        timeout = httpx.Timeout(self.timeout, connect=5.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=params)
            
            # Handle specific HTTP errors
            if response.status_code == 404:
                raise ValueError(f"Symbol {symbol} not found")
            elif response.status_code == 429:
                logger.warning("Rate limit hit for Yahoo Finance")
                raise httpx.HTTPStatusError(
                    "Rate limit exceeded",
                    request=response.request,
                    response=response
                )
            
            response.raise_for_status()
            return response.json()
    
    def _parse_quote_data(self, symbol: str, data: Dict[str, Any]) -> StockQuote:
        """Parse Yahoo Finance response into StockQuote"""
        try:
            chart = data['chart']
            if not chart or 'result' not in chart or not chart['result']:
                raise ValueError(f"No data available for {symbol}")
            
            result = chart['result'][0]
            meta = result.get('meta', {})
            
            # Get current price
            current_price = meta.get('regularMarketPrice')
            if current_price is None:
                current_price = meta.get('previousClose', 0.0)
            
            # Calculate change
            previous_close = meta.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0.0
            
            # Get volume
            volume = meta.get('regularMarketVolume', 0)
            
            # Get additional metrics
            market_cap = self._format_market_cap(meta.get('marketCap'))
            pe_ratio = meta.get('trailingPE')
            dividend_yield = meta.get('dividendYield')
            
            # Get 52-week range
            fifty_two_week_high = meta.get('fiftyTwoWeekHigh')
            fifty_two_week_low = meta.get('fiftyTwoWeekLow')
            
            return StockQuote(
                symbol=symbol.upper(),
                price=round(current_price, 2),
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=volume,
                market_cap=market_cap,
                pe_ratio=pe_ratio,
                dividend_yield=dividend_yield,
                fifty_two_week_high=fifty_two_week_high,
                fifty_two_week_low=fifty_two_week_low,
                timestamp=datetime.now(),
                source="yahoo_finance"
            )
            
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error parsing quote data for {symbol}: {e}")
            raise ValueError(f"Failed to parse data for {symbol}: {str(e)}")
    
    def _format_market_cap(self, market_cap: Optional[float]) -> Optional[str]:
        """Format market cap into readable string"""
        if market_cap is None:
            return None
        
        if market_cap >= 1e12:
            return f"{market_cap / 1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"{market_cap / 1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"{market_cap / 1e6:.2f}M"
        else:
            return f"{market_cap:.0f}"
    
    async def get_quote(self, symbol: str, use_cache: bool = True) -> StockQuote:
        """
        Get stock quote with caching and error handling
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
            use_cache: Whether to use cached data if available
            
        Returns:
            StockQuote object with current data
            
        Raises:
            ValueError: If symbol is invalid or data cannot be retrieved
        """
        symbol = symbol.upper().strip()
        
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        
        # Check cache first
        if use_cache:
            cached_quote = self._get_from_cache(symbol)
            if cached_quote:
                return cached_quote
        
        # Check if we should fetch real-time data
        should_fetch, reason = should_fetch_realtime_data(symbol)
        if not should_fetch and use_cache:
            # Try to return cached data even if slightly stale
            if symbol in self.cache:
                logger.info(f"Market closed ({reason}), using cached data for {symbol}")
                return self.cache[symbol]['quote']
        
        try:
            # Apply circuit breaker
            @self.circuit_breaker
            async def fetch_with_circuit_breaker():
                return await self._fetch_quote_data(symbol)
            
            raw_data = await fetch_with_circuit_breaker()
            quote = self._parse_quote_data(symbol, raw_data)
            
            # Store in cache
            self._store_in_cache(symbol, quote)
            
            logger.info(f"Successfully fetched quote for {symbol}: ${quote.price}")
            return quote
            
        except Exception as e:
            logger.error(f"Failed to fetch quote for {symbol}: {e}")
            
            # Try to return stale cached data as fallback
            if symbol in self.cache:
                logger.warning(f"Using stale cached data for {symbol} due to error")
                cached_quote = self.cache[symbol]['quote']
                # Mark as stale
                cached_quote.source = "yahoo_finance_cached"
                return cached_quote
            
            # If no cache available, create a minimal quote with error info
            raise ValueError(f"Unable to fetch data for {symbol}: {str(e)}")
    
    async def get_multiple_quotes(
        self, 
        symbols: List[str], 
        max_concurrent: int = 5
    ) -> Dict[str, StockQuote]:
        """
        Get quotes for multiple symbols concurrently
        
        Args:
            symbols: List of stock symbols
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dictionary mapping symbols to StockQuote objects
        """
        if not symbols:
            return {}
        
        # Remove duplicates and clean symbols
        unique_symbols = list(set(s.upper().strip() for s in symbols if s.strip()))
        
        if not unique_symbols:
            return {}
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_single(symbol: str) -> Tuple[str, Optional[StockQuote]]:
            async with semaphore:
                try:
                    quote = await self.get_quote(symbol)
                    return symbol, quote
                except Exception as e:
                    logger.error(f"Failed to fetch {symbol}: {e}")
                    return symbol, None
        
        # Execute all requests concurrently
        tasks = [fetch_single(symbol) for symbol in unique_symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        quotes = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed with exception: {result}")
                continue
            
            symbol, quote = result
            if quote:
                quotes[symbol] = quote
        
        logger.info(f"Successfully fetched {len(quotes)}/{len(unique_symbols)} quotes")
        return quotes
    
    def clear_cache(self, symbol: Optional[str] = None):
        """Clear cache for specific symbol or all symbols"""
        if symbol:
            self.cache.pop(symbol.upper(), None)
            logger.info(f"Cleared cache for {symbol}")
        else:
            self.cache.clear()
            logger.info("Cleared all cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        valid_entries = sum(1 for symbol in self.cache if self._is_cache_valid(symbol))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'stale_entries': total_entries - valid_entries,
            'symbols': list(self.cache.keys())
        }

# Global collector instance
yahoo_collector = YahooFinanceCollector()
