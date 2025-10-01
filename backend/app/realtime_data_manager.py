"""
Real-time Data Management System for Stock Trading
Provides intelligent caching, market hours awareness, and multi-source data aggregation
"""

import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import json
import pytz
from dataclasses import dataclass, asdict
import hashlib

import redis
import yfinance as yf
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class MarketStatus(str, Enum):
    """Market trading status"""
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    OPEN = "open"
    AFTER_HOURS = "after_hours"
    HOLIDAY = "holiday"

class DataSource(str, Enum):
    """Available data sources"""
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    FINNHUB = "finnhub"
    CACHED = "cached"

@dataclass
class StockQuote:
    """Standardized stock quote data structure"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    open_price: float
    high: float
    low: float
    previous_close: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    timestamp: datetime = None
    source: DataSource = DataSource.YAHOO_FINANCE
    market_status: MarketStatus = MarketStatus.CLOSED
    is_cached: bool = False
    cache_age_seconds: int = 0

class MarketHoursManager:
    """Manages market hours and trading sessions across different exchanges"""
    
    def __init__(self):
        self.market_timezones = {
            'US': pytz.timezone('America/New_York'),
            'UK': pytz.timezone('Europe/London'),
            'JP': pytz.timezone('Asia/Tokyo'),
            'HK': pytz.timezone('Asia/Hong_Kong'),
            'CN': pytz.timezone('Asia/Shanghai')
        }
        
        self.market_hours = {
            'US': {
                'regular': (time(9, 30), time(16, 0)),
                'pre_market': (time(4, 0), time(9, 30)),
                'after_hours': (time(16, 0), time(20, 0))
            },
            'UK': {
                'regular': (time(8, 0), time(16, 30)),
                'pre_market': (time(7, 0), time(8, 0)),
                'after_hours': (time(16, 30), time(17, 30))
            },
            'JP': {
                'regular': (time(9, 0), time(15, 0)),
                'pre_market': (time(8, 0), time(9, 0)),
                'after_hours': (time(15, 0), time(16, 0))
            }
        }
    
    def get_market_status(self, symbol: str) -> MarketStatus:
        """Determine current market status for a symbol"""
        
        # Determine market based on symbol
        market = self._get_market_from_symbol(symbol)
        
        if market not in self.market_timezones:
            return MarketStatus.CLOSED
        
        # Get current time in market timezone
        market_tz = self.market_timezones[market]
        current_time = datetime.now(market_tz).time()
        current_date = datetime.now(market_tz).date()
        
        # Check if it's a weekend
        if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return MarketStatus.CLOSED
        
        # Check if it's a holiday (simplified - you'd want a proper holiday calendar)
        if self._is_market_holiday(current_date, market):
            return MarketStatus.HOLIDAY
        
        # Check trading sessions
        hours = self.market_hours.get(market, self.market_hours['US'])
        
        if hours['regular'][0] <= current_time <= hours['regular'][1]:
            return MarketStatus.OPEN
        elif hours['pre_market'][0] <= current_time < hours['regular'][0]:
            return MarketStatus.PRE_MARKET
        elif hours['regular'][1] < current_time <= hours['after_hours'][1]:
            return MarketStatus.AFTER_HOURS
        else:
            return MarketStatus.CLOSED
    
    def _get_market_from_symbol(self, symbol: str) -> str:
        """Determine market from stock symbol"""
        symbol = symbol.upper()
        
        # Simple heuristics - in production, you'd want a proper symbol-to-market mapping
        if symbol.endswith('.L'):
            return 'UK'
        elif symbol.endswith('.T') or symbol.endswith('.TO'):
            return 'JP'
        elif symbol.endswith('.HK'):
            return 'HK'
        elif symbol.endswith('.SS') or symbol.endswith('.SZ'):
            return 'CN'
        else:
            return 'US'  # Default to US market
    
    def _is_market_holiday(self, date, market: str) -> bool:
        """Check if date is a market holiday (simplified implementation)"""
        # This is a simplified implementation
        # In production, you'd want to use a proper holiday calendar library
        
        # Common holidays (you'd expand this)
        us_holidays_2024 = [
            datetime(2024, 1, 1).date(),   # New Year's Day
            datetime(2024, 1, 15).date(),  # MLK Day
            datetime(2024, 2, 19).date(),  # Presidents Day
            datetime(2024, 7, 4).date(),   # Independence Day
            datetime(2024, 12, 25).date(), # Christmas
        ]
        
        if market == 'US':
            return date in us_holidays_2024
        
        return False
    
    def get_cache_ttl(self, symbol: str) -> int:
        """Get appropriate cache TTL based on market status"""
        status = self.get_market_status(symbol)
        
        ttl_map = {
            MarketStatus.OPEN: 60,        # 1 minute during trading
            MarketStatus.PRE_MARKET: 300, # 5 minutes pre-market
            MarketStatus.AFTER_HOURS: 600, # 10 minutes after hours
            MarketStatus.CLOSED: 3600,    # 1 hour when closed
            MarketStatus.HOLIDAY: 7200    # 2 hours on holidays
        }
        
        return ttl_map.get(status, 3600)

class SmartCache:
    """Intelligent caching system with market-aware TTL"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.market_manager = MarketHoursManager()
        self.local_cache: Dict[str, Tuple[StockQuote, datetime]] = {}
        self.max_local_cache_size = 1000
    
    def _generate_cache_key(self, symbol: str, data_type: str = "quote") -> str:
        """Generate cache key for stock data"""
        return f"stock:{data_type}:{symbol.upper()}"
    
    async def get_cached_quote(self, symbol: str) -> Optional[StockQuote]:
        """Retrieve cached stock quote with freshness check"""
        
        cache_key = self._generate_cache_key(symbol)
        
        # Try Redis first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    quote = StockQuote(**data)
                    
                    # Check if cache is still fresh
                    if self._is_cache_fresh(quote, symbol):
                        quote.is_cached = True
                        quote.cache_age_seconds = int((datetime.now() - quote.timestamp).total_seconds())
                        return quote
            except Exception as e:
                logger.warning(f"Redis cache retrieval failed: {e}")
        
        # Try local cache
        if symbol in self.local_cache:
            quote, cached_at = self.local_cache[symbol]
            if self._is_cache_fresh(quote, symbol):
                quote.is_cached = True
                quote.cache_age_seconds = int((datetime.now() - cached_at).total_seconds())
                return quote
        
        return None
    
    async def cache_quote(self, quote: StockQuote):
        """Cache stock quote with appropriate TTL"""
        
        cache_key = self._generate_cache_key(quote.symbol)
        ttl = self.market_manager.get_cache_ttl(quote.symbol)
        
        # Add timestamp if not present
        if not quote.timestamp:
            quote.timestamp = datetime.now()
        
        # Cache in Redis
        if self.redis_client:
            try:
                quote_data = asdict(quote)
                quote_data['timestamp'] = quote.timestamp.isoformat()
                
                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(quote_data, default=str)
                )
            except Exception as e:
                logger.warning(f"Redis cache storage failed: {e}")
        
        # Cache locally (with size limit)
        if len(self.local_cache) >= self.max_local_cache_size:
            # Remove oldest entry
            oldest_symbol = min(self.local_cache.keys(), 
                              key=lambda k: self.local_cache[k][1])
            del self.local_cache[oldest_symbol]
        
        self.local_cache[quote.symbol] = (quote, datetime.now())
    
    def _is_cache_fresh(self, quote: StockQuote, symbol: str) -> bool:
        """Check if cached data is still fresh based on market status"""
        
        if not quote.timestamp:
            return False
        
        ttl = self.market_manager.get_cache_ttl(symbol)
        age = (datetime.now() - quote.timestamp).total_seconds()
        
        return age < ttl

class MultiSourceDataProvider:
    """Aggregates data from multiple sources with fallback logic"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.cache = SmartCache(redis_client)
        self.market_manager = MarketHoursManager()
        self.sources = [
            YahooFinanceProvider(),
            # AlphaVantageProvider(),  # Would be implemented
            # PolygonProvider(),       # Would be implemented
        ]
        self.circuit_breakers = {}
    
    async def get_quote(self, symbol: str, force_refresh: bool = False) -> StockQuote:
        """Get stock quote with intelligent source selection and caching"""
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_quote = await self.cache.get_cached_quote(symbol)
            if cached_quote:
                return cached_quote
        
        # Try each data source
        last_error = None
        for source in self.sources:
            if self._is_source_available(source):
                try:
                    quote = await source.get_quote(symbol)
                    if quote:
                        # Add market status
                        quote.market_status = self.market_manager.get_market_status(symbol)
                        
                        # Cache the result
                        await self.cache.cache_quote(quote)
                        
                        # Reset circuit breaker on success
                        self._reset_circuit_breaker(source)
                        
                        return quote
                        
                except Exception as e:
                    logger.warning(f"Data source {source.__class__.__name__} failed: {e}")
                    last_error = e
                    self._record_failure(source)
        
        # If all sources failed, try to return stale cache
        stale_quote = await self._get_stale_cache(symbol)
        if stale_quote:
            stale_quote.is_cached = True
            stale_quote.cache_age_seconds = int((datetime.now() - stale_quote.timestamp).total_seconds())
            logger.warning(f"Returning stale data for {symbol}")
            return stale_quote
        
        # Complete failure
        raise Exception(f"Unable to fetch data for {symbol} from any source. Last error: {last_error}")
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, StockQuote]:
        """Get quotes for multiple symbols efficiently"""
        
        # Check cache for all symbols first
        results = {}
        uncached_symbols = []
        
        for symbol in symbols:
            cached_quote = await self.cache.get_cached_quote(symbol)
            if cached_quote:
                results[symbol] = cached_quote
            else:
                uncached_symbols.append(symbol)
        
        # Fetch uncached symbols concurrently
        if uncached_symbols:
            tasks = [self.get_quote(symbol) for symbol in uncached_symbols]
            try:
                quotes = await asyncio.gather(*tasks, return_exceptions=True)
                
                for symbol, quote in zip(uncached_symbols, quotes):
                    if isinstance(quote, Exception):
                        logger.error(f"Failed to fetch {symbol}: {quote}")
                        # Create a placeholder quote
                        results[symbol] = StockQuote(
                            symbol=symbol,
                            price=0.0,
                            change=0.0,
                            change_percent=0.0,
                            volume=0,
                            open_price=0.0,
                            high=0.0,
                            low=0.0,
                            previous_close=0.0,
                            timestamp=datetime.now(),
                            source=DataSource.CACHED,
                            is_cached=True
                        )
                    else:
                        results[symbol] = quote
            except Exception as e:
                logger.error(f"Batch quote fetch failed: {e}")
        
        return results
    
    def _is_source_available(self, source) -> bool:
        """Check if data source is available (circuit breaker logic)"""
        source_name = source.__class__.__name__
        
        if source_name not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[source_name]
        
        # If circuit is open, check if enough time has passed to try again
        if breaker['failures'] >= 5:  # Circuit opens after 5 failures
            time_since_last_failure = datetime.now() - breaker['last_failure']
            if time_since_last_failure < timedelta(minutes=5):  # Stay open for 5 minutes
                return False
            else:
                # Reset and try again
                breaker['failures'] = 0
        
        return True
    
    def _record_failure(self, source):
        """Record a failure for circuit breaker logic"""
        source_name = source.__class__.__name__
        
        if source_name not in self.circuit_breakers:
            self.circuit_breakers[source_name] = {
                'failures': 0,
                'last_failure': datetime.now()
            }
        
        self.circuit_breakers[source_name]['failures'] += 1
        self.circuit_breakers[source_name]['last_failure'] = datetime.now()
    
    def _reset_circuit_breaker(self, source):
        """Reset circuit breaker on successful request"""
        source_name = source.__class__.__name__
        if source_name in self.circuit_breakers:
            self.circuit_breakers[source_name]['failures'] = 0
    
    async def _get_stale_cache(self, symbol: str) -> Optional[StockQuote]:
        """Get stale cached data as last resort"""
        cache_key = self.cache._generate_cache_key(symbol)
        
        if self.cache.redis_client:
            try:
                # Look for expired cache entries
                cached_data = await self.cache.redis_client.get(f"{cache_key}:stale")
                if cached_data:
                    data = json.loads(cached_data)
                    return StockQuote(**data)
            except Exception:
                pass
        
        return None

class YahooFinanceProvider:
    """Yahoo Finance data provider with enhanced error handling"""
    
    def __init__(self):
        self.session = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, ConnectionError))
    )
    async def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get stock quote from Yahoo Finance"""
        
        try:
            # Use yfinance library
            ticker = yf.Ticker(symbol)
            
            # Get current data
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                # Try daily data if minute data is not available
                hist = ticker.history(period="2d")
                if hist.empty:
                    return None
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            # Extract data
            current_price = float(latest['Close'])
            previous_close = float(previous['Close'])
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0
            
            quote = StockQuote(
                symbol=symbol.upper(),
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=int(latest['Volume']),
                open_price=float(latest['Open']),
                high=float(latest['High']),
                low=float(latest['Low']),
                previous_close=previous_close,
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                timestamp=datetime.now(),
                source=DataSource.YAHOO_FINANCE
            )
            
            return quote
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            raise

class RealTimeDataManager:
    """Main interface for real-time data management"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.data_provider = MultiSourceDataProvider(redis_client)
        self.market_manager = MarketHoursManager()
        self.subscribers = {}  # For WebSocket subscriptions
    
    async def get_stock_quote(self, symbol: str, force_refresh: bool = False) -> StockQuote:
        """Get stock quote with intelligent caching and source selection"""
        return await self.data_provider.get_quote(symbol, force_refresh)
    
    async def get_portfolio_quotes(self, symbols: List[str]) -> Dict[str, StockQuote]:
        """Get quotes for multiple stocks efficiently"""
        return await self.data_provider.get_multiple_quotes(symbols)
    
    def get_market_status(self, symbol: str) -> MarketStatus:
        """Get current market status for a symbol"""
        return self.market_manager.get_market_status(symbol)
    
    async def subscribe_to_updates(self, symbol: str, callback):
        """Subscribe to real-time updates for a symbol (WebSocket-like)"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        
        self.subscribers[symbol].append(callback)
        
        # Start background task to send updates
        asyncio.create_task(self._send_updates(symbol))
    
    async def _send_updates(self, symbol: str):
        """Send periodic updates to subscribers"""
        while symbol in self.subscribers and self.subscribers[symbol]:
            try:
                quote = await self.get_stock_quote(symbol, force_refresh=True)
                
                # Notify all subscribers
                for callback in self.subscribers[symbol]:
                    try:
                        await callback(quote)
                    except Exception as e:
                        logger.error(f"Subscriber callback failed: {e}")
                
                # Wait based on market status
                status = self.get_market_status(symbol)
                if status == MarketStatus.OPEN:
                    await asyncio.sleep(30)  # 30 seconds during market hours
                else:
                    await asyncio.sleep(300)  # 5 minutes when closed
                    
            except Exception as e:
                logger.error(f"Update loop error for {symbol}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def unsubscribe_from_updates(self, symbol: str, callback):
        """Unsubscribe from real-time updates"""
        if symbol in self.subscribers:
            try:
                self.subscribers[symbol].remove(callback)
                if not self.subscribers[symbol]:
                    del self.subscribers[symbol]
            except ValueError:
                pass
    
    async def get_data_freshness_info(self, symbol: str) -> Dict[str, Any]:
        """Get information about data freshness and sources"""
        quote = await self.get_stock_quote(symbol)
        market_status = self.get_market_status(symbol)
        
        return {
            'symbol': symbol,
            'market_status': market_status.value,
            'data_source': quote.source.value,
            'is_cached': quote.is_cached,
            'cache_age_seconds': quote.cache_age_seconds,
            'timestamp': quote.timestamp.isoformat(),
            'recommended_refresh_interval': self.market_manager.get_cache_ttl(symbol)
        }

# Global instance
realtime_manager = RealTimeDataManager()
