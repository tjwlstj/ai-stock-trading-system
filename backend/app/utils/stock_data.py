"""
Stock data utilities with retry logic and caching
Provides resilient Yahoo Finance data fetching
"""

import logging
import yfinance as yf
from typing import Dict, Any, Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import pandas as pd
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class StockDataFetcher:
    """Resilient stock data fetcher with caching and retry logic"""
    
    def __init__(self, cache_dir: str = ".cache/yf"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    @retry(
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((Exception,))
    )
    def _fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock info with retry logic"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info:
                # Fallback to history if info is incomplete
                hist = ticker.history(period="1d")
                if not hist.empty:
                    latest = hist.iloc[-1]
                    info = {
                        'symbol': symbol,
                        'regularMarketPrice': latest['Close'],
                        'regularMarketChange': latest['Close'] - latest['Open'],
                        'regularMarketChangePercent': ((latest['Close'] - latest['Open']) / latest['Open']) * 100,
                        'regularMarketVolume': latest['Volume'],
                        'marketCap': info.get('marketCap', 'N/A'),
                        'source': 'history_fallback'
                    }
            
            return info
            
        except Exception as e:
            logger.warning(f"Failed to fetch data for {symbol}: {e}")
            raise
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock data with caching and error handling
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing stock data
        """
        try:
            info = self._fetch_stock_info(symbol.upper())
            
            # Normalize the data structure
            return {
                "symbol": symbol.upper(),
                "price": info.get('regularMarketPrice', info.get('currentPrice', 0)),
                "change": info.get('regularMarketChange', 0),
                "change_percent": info.get('regularMarketChangePercent', 0),
                "volume": info.get('regularMarketVolume', info.get('volume', 0)),
                "market_cap": info.get('marketCap', 'N/A'),
                "timestamp": datetime.now().isoformat(),
                "source": "yahoo_finance",
                "currency": info.get('currency', 'USD'),
                "exchange": info.get('exchange', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            # Return mock data as fallback
            return {
                "symbol": symbol.upper(),
                "price": 0,
                "change": 0,
                "change_percent": 0,
                "volume": 0,
                "market_cap": "N/A",
                "timestamp": datetime.now().isoformat(),
                "source": "fallback",
                "error": str(e),
                "currency": "USD",
                "exchange": "Unknown"
            }
    
    async def get_multiple_stocks(self, symbols: list) -> Dict[str, Dict[str, Any]]:
        """
        Get data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to their data
        """
        results = {}
        
        for symbol in symbols:
            try:
                results[symbol] = await self.get_stock_data(symbol)
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                results[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results

# Global instance
stock_fetcher = StockDataFetcher()
