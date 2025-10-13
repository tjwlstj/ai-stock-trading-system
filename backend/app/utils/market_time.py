"""
Market Time Utilities
Handle market hours, holidays, and trading sessions
"""

import pytz
from datetime import datetime, time, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Market timezones
MARKET_TIMEZONES = {
    'NYSE': pytz.timezone('America/New_York'),
    'NASDAQ': pytz.timezone('America/New_York'),
    'LSE': pytz.timezone('Europe/London'),
    'TSE': pytz.timezone('Asia/Tokyo'),
    'HKEX': pytz.timezone('Asia/Hong_Kong'),
    'SSE': pytz.timezone('Asia/Shanghai'),
}

# Market hours (local time)
MARKET_HOURS = {
    'NYSE': {'open': time(9, 30), 'close': time(16, 0)},
    'NASDAQ': {'open': time(9, 30), 'close': time(16, 0)},
    'LSE': {'open': time(8, 0), 'close': time(16, 30)},
    'TSE': {'open': time(9, 0), 'close': time(15, 0)},
    'HKEX': {'open': time(9, 30), 'close': time(16, 0)},
    'SSE': {'open': time(9, 30), 'close': time(15, 0)},
}

# US Market holidays (simplified - in production, use a proper holiday library)
US_MARKET_HOLIDAYS_2024 = [
    date(2024, 1, 1),   # New Year's Day
    date(2024, 1, 15),  # Martin Luther King Jr. Day
    date(2024, 2, 19),  # Presidents' Day
    date(2024, 3, 29),  # Good Friday
    date(2024, 5, 27),  # Memorial Day
    date(2024, 6, 19),  # Juneteenth
    date(2024, 7, 4),   # Independence Day
    date(2024, 9, 2),   # Labor Day
    date(2024, 11, 28), # Thanksgiving
    date(2024, 12, 25), # Christmas
]

US_MARKET_HOLIDAYS_2025 = [
    date(2025, 1, 1),   # New Year's Day
    date(2025, 1, 20),  # Martin Luther King Jr. Day
    date(2025, 2, 17),  # Presidents' Day
    date(2025, 4, 18),  # Good Friday
    date(2025, 5, 26),  # Memorial Day
    date(2025, 6, 19),  # Juneteenth
    date(2025, 7, 4),   # Independence Day
    date(2025, 9, 1),   # Labor Day
    date(2025, 11, 27), # Thanksgiving
    date(2025, 12, 25), # Christmas
]

ALL_US_HOLIDAYS = US_MARKET_HOLIDAYS_2024 + US_MARKET_HOLIDAYS_2025

class MarketSession:
    """Market session information"""
    
    def __init__(self, market: str = 'NYSE'):
        self.market = market.upper()
        self.timezone = MARKET_TIMEZONES.get(self.market, MARKET_TIMEZONES['NYSE'])
        self.hours = MARKET_HOURS.get(self.market, MARKET_HOURS['NYSE'])
    
    def is_market_open(self, dt: Optional[datetime] = None) -> bool:
        """Check if market is currently open"""
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        # Check if it's a weekend
        if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if it's a holiday (US markets only for now)
        if self.market in ['NYSE', 'NASDAQ'] and dt.date() in ALL_US_HOLIDAYS:
            return False
        
        # Check if current time is within market hours
        current_time = dt.time()
        return self.hours['open'] <= current_time <= self.hours['close']
    
    def is_market_closed(self, dt: Optional[datetime] = None) -> bool:
        """Check if market is currently closed"""
        return not self.is_market_open(dt)

    def _next_calendar_day(self, current_date: date) -> date:
        """Return the next calendar day"""
        return current_date + timedelta(days=1)

    def _is_trading_day(self, current_date: date) -> bool:
        """Determine if the given date is a valid trading day"""
        if current_date.weekday() >= 5:
            return False
        if self.market in ['NYSE', 'NASDAQ'] and current_date in ALL_US_HOLIDAYS:
            return False
        return True

    def _advance_to_next_trading_day(self, current_date: date, include_current: bool = False) -> date:
        """Advance to the next trading day, optionally considering the current date"""
        candidate = current_date if include_current else self._next_calendar_day(current_date)
        while not self._is_trading_day(candidate):
            candidate = self._next_calendar_day(candidate)
        return candidate

    def next_market_open(self, dt: Optional[datetime] = None) -> datetime:
        """Get the next market open time"""
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        current_date = dt.date()

        if self.is_market_open(dt) or dt.time() >= self.hours['close']:
            current_date = self._advance_to_next_trading_day(current_date)
        elif not self._is_trading_day(current_date):
            current_date = self._advance_to_next_trading_day(current_date, include_current=True)

        # Combine date with market open time
        next_open = datetime.combine(current_date, self.hours['open'])
        return self.timezone.localize(next_open)
    
    def time_until_open(self, dt: Optional[datetime] = None) -> Optional[float]:
        """Get seconds until market opens (None if market is open)"""
        if self.is_market_open(dt):
            return None
        
        next_open = self.next_market_open(dt)
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        return (next_open - dt).total_seconds()
    
    def get_market_status(self, dt: Optional[datetime] = None) -> Dict[str, any]:
        """Get comprehensive market status"""
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        is_open = self.is_market_open(dt)
        
        status = {
            'market': self.market,
            'is_open': is_open,
            'current_time': dt.isoformat(),
            'timezone': str(self.timezone),
            'market_hours': {
                'open': self.hours['open'].strftime('%H:%M'),
                'close': self.hours['close'].strftime('%H:%M')
            }
        }
        
        if not is_open:
            next_open = self.next_market_open(dt)
            time_until = self.time_until_open(dt)
            
            status.update({
                'next_open': next_open.isoformat(),
                'time_until_open_seconds': time_until,
                'time_until_open_hours': time_until / 3600 if time_until else None
            })
        
        # Add reason for closure
        if dt.weekday() >= 5:
            status['closure_reason'] = 'weekend'
        elif self.market in ['NYSE', 'NASDAQ'] and dt.date() in ALL_US_HOLIDAYS:
            status['closure_reason'] = 'holiday'
        elif not is_open:
            status['closure_reason'] = 'after_hours'
        
        return status

def get_trading_session_info(symbol: str) -> Dict[str, any]:
    """
    Get trading session info for a symbol
    This is a simplified version - in production, you'd map symbols to their primary exchanges
    """
    # Simple mapping - in reality, you'd need a comprehensive symbol-to-exchange mapping
    if symbol.endswith('.L'):
        market = 'LSE'
    elif symbol.endswith('.T'):
        market = 'TSE'
    elif symbol.endswith('.HK'):
        market = 'HKEX'
    elif symbol.endswith('.SS'):
        market = 'SSE'
    else:
        # Default to US markets for most symbols
        market = 'NYSE'
    
    session = MarketSession(market)
    return session.get_market_status()

def should_fetch_realtime_data(symbol: str) -> Tuple[bool, str]:
    """
    Determine if we should fetch real-time data or use cached/delayed data
    Returns (should_fetch, reason)
    """
    try:
        session_info = get_trading_session_info(symbol)
        
        if session_info['is_open']:
            return True, "market_open"
        else:
            reason = session_info.get('closure_reason', 'unknown')
            return False, f"market_closed_{reason}"
    
    except Exception as e:
        logger.warning(f"Error checking market status for {symbol}: {e}")
        return True, "status_check_failed"  # Default to fetching when in doubt

def get_data_freshness_requirement(symbol: str) -> int:
    """
    Get data freshness requirement in seconds based on market status
    Returns how old data can be before it's considered stale
    """
    should_fetch, reason = should_fetch_realtime_data(symbol)
    
    if should_fetch:
        return 60  # 1 minute for open markets
    elif 'weekend' in reason:
        return 86400 * 2  # 2 days for weekends
    elif 'holiday' in reason:
        return 86400  # 1 day for holidays
    else:
        return 3600  # 1 hour for after-hours
