"""
Symbol Validation and Management
Handle symbol validation, normalization, and blacklisting
"""

import re
import logging
from typing import Set, List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class SymbolInfo:
    """Information about a stock symbol"""
    symbol: str
    normalized: str
    exchange: Optional[str] = None
    is_valid: bool = True
    last_checked: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None

class SymbolValidator:
    """
    Symbol validation and management system
    """
    
    def __init__(self):
        # Known invalid or problematic symbols
        self.blacklist: Set[str] = {
            # Common invalid patterns
            '', ' ', 'NULL', 'NONE', 'N/A',
            # Test symbols
            'TEST', 'DUMMY', 'FAKE',
            # Delisted or problematic symbols (examples)
            'GMEQ', 'BBBYQ',  # Bankruptcy symbols
        }
        
        # Symbols that have been validated
        self.validated_symbols: Dict[str, SymbolInfo] = {}
        
        # Symbols that have failed validation
        self.failed_symbols: Dict[str, SymbolInfo] = {}
        
        # Symbol patterns for different exchanges
        self.exchange_patterns = {
            'US': re.compile(r'^[A-Z]{1,5}$'),  # 1-5 letters
            'LSE': re.compile(r'^[A-Z]{1,4}\.L$'),  # London Stock Exchange
            'TSE': re.compile(r'^[A-Z0-9]{4}\.T$'),  # Tokyo Stock Exchange
            'HKEX': re.compile(r'^[0-9]{4}\.HK$'),  # Hong Kong Exchange
            'SSE': re.compile(r'^[0-9]{6}\.SS$'),  # Shanghai Stock Exchange
            'SZSE': re.compile(r'^[0-9]{6}\.SZ$'),  # Shenzhen Stock Exchange
        }
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol format"""
        if not symbol:
            return ""
        
        # Remove whitespace and convert to uppercase
        normalized = symbol.strip().upper()
        
        # Handle common variations
        replacements = {
            # Common suffixes
            '.US': '',
            '.USA': '',
            ' US': '',
            # Handle dots in US symbols (some data sources use them)
            '.': '' if not any(pattern in normalized for pattern in ['.L', '.T', '.HK', '.SS', '.SZ']) else '.'
        }
        
        for old, new in replacements.items():
            if normalized.endswith(old):
                normalized = normalized[:-len(old)] + new
                break
        
        return normalized
    
    def detect_exchange(self, symbol: str) -> Optional[str]:
        """Detect exchange from symbol format"""
        for exchange, pattern in self.exchange_patterns.items():
            if pattern.match(symbol):
                return exchange
        return None
    
    def is_valid_format(self, symbol: str) -> Tuple[bool, str]:
        """
        Check if symbol has valid format
        Returns (is_valid, reason)
        """
        if not symbol:
            return False, "Empty symbol"
        
        normalized = self.normalize_symbol(symbol)
        
        if not normalized:
            return False, "Symbol becomes empty after normalization"
        
        if normalized in self.blacklist:
            return False, "Symbol is blacklisted"
        
        # Check length constraints
        if len(normalized) > 10:
            return False, "Symbol too long"
        
        # Check for invalid characters (basic check)
        if not re.match(r'^[A-Z0-9.-]+$', normalized):
            return False, "Contains invalid characters"
        
        # Check against known patterns
        exchange = self.detect_exchange(normalized)
        if exchange:
            return True, f"Valid {exchange} symbol"
        
        # Default to US format validation
        if re.match(r'^[A-Z]{1,5}$', normalized):
            return True, "Valid US symbol format"
        
        return False, "Unknown symbol format"
    
    def add_to_blacklist(self, symbol: str, reason: str = "Manual addition"):
        """Add symbol to blacklist"""
        normalized = self.normalize_symbol(symbol)
        self.blacklist.add(normalized)
        
        # Remove from validated symbols if present
        self.validated_symbols.pop(normalized, None)
        
        # Add to failed symbols
        self.failed_symbols[normalized] = SymbolInfo(
            symbol=symbol,
            normalized=normalized,
            is_valid=False,
            last_checked=datetime.now(),
            error_count=1,
            last_error=reason
        )
        
        logger.info(f"Added {normalized} to blacklist: {reason}")
    
    def remove_from_blacklist(self, symbol: str):
        """Remove symbol from blacklist"""
        normalized = self.normalize_symbol(symbol)
        self.blacklist.discard(normalized)
        self.failed_symbols.pop(normalized, None)
        logger.info(f"Removed {normalized} from blacklist")
    
    def validate_symbol(self, symbol: str, force_recheck: bool = False) -> SymbolInfo:
        """
        Validate a symbol and return detailed information
        
        Args:
            symbol: Raw symbol to validate
            force_recheck: Force revalidation even if cached
            
        Returns:
            SymbolInfo with validation results
        """
        normalized = self.normalize_symbol(symbol)
        
        # Check cache first (unless forced recheck)
        if not force_recheck:
            if normalized in self.validated_symbols:
                return self.validated_symbols[normalized]
            
            if normalized in self.failed_symbols:
                failed_info = self.failed_symbols[normalized]
                # Re-check failed symbols after some time
                if failed_info.last_checked and \
                   datetime.now() - failed_info.last_checked < timedelta(hours=24):
                    return failed_info
        
        # Perform validation
        is_valid_fmt, reason = self.is_valid_format(normalized)
        exchange = self.detect_exchange(normalized) if is_valid_fmt else None
        
        symbol_info = SymbolInfo(
            symbol=symbol,
            normalized=normalized,
            exchange=exchange,
            is_valid=is_valid_fmt,
            last_checked=datetime.now(),
            error_count=0 if is_valid_fmt else 1,
            last_error=None if is_valid_fmt else reason
        )
        
        # Cache the result
        if is_valid_fmt:
            self.validated_symbols[normalized] = symbol_info
            # Remove from failed cache if present
            self.failed_symbols.pop(normalized, None)
        else:
            self.failed_symbols[normalized] = symbol_info
        
        return symbol_info
    
    def validate_multiple(self, symbols: List[str]) -> Dict[str, SymbolInfo]:
        """Validate multiple symbols"""
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.validate_symbol(symbol)
            except Exception as e:
                logger.error(f"Error validating symbol {symbol}: {e}")
                results[symbol] = SymbolInfo(
                    symbol=symbol,
                    normalized=self.normalize_symbol(symbol),
                    is_valid=False,
                    last_checked=datetime.now(),
                    error_count=1,
                    last_error=str(e)
                )
        return results
    
    def get_valid_symbols(self, symbols: List[str]) -> List[str]:
        """Filter and return only valid symbols"""
        valid_symbols = []
        for symbol in symbols:
            info = self.validate_symbol(symbol)
            if info.is_valid:
                valid_symbols.append(info.normalized)
        return valid_symbols
    
    def record_fetch_error(self, symbol: str, error: str):
        """Record that a symbol failed to fetch data"""
        normalized = self.normalize_symbol(symbol)
        
        if normalized in self.validated_symbols:
            info = self.validated_symbols[normalized]
            info.error_count += 1
            info.last_error = error
            info.last_checked = datetime.now()
            
            # Move to failed list if too many errors
            if info.error_count >= 5:
                info.is_valid = False
                self.failed_symbols[normalized] = info
                del self.validated_symbols[normalized]
                logger.warning(f"Moved {normalized} to failed list after {info.error_count} errors")
        
        elif normalized in self.failed_symbols:
            info = self.failed_symbols[normalized]
            info.error_count += 1
            info.last_error = error
            info.last_checked = datetime.now()
        
        else:
            # New failed symbol
            self.failed_symbols[normalized] = SymbolInfo(
                symbol=symbol,
                normalized=normalized,
                is_valid=False,
                last_checked=datetime.now(),
                error_count=1,
                last_error=error
            )
    
    def record_fetch_success(self, symbol: str):
        """Record that a symbol successfully fetched data"""
        normalized = self.normalize_symbol(symbol)
        
        if normalized in self.failed_symbols:
            # Move back to validated if it was previously failed
            info = self.failed_symbols[normalized]
            info.is_valid = True
            info.error_count = 0
            info.last_error = None
            info.last_checked = datetime.now()
            
            self.validated_symbols[normalized] = info
            del self.failed_symbols[normalized]
            logger.info(f"Moved {normalized} back to validated list")
        
        elif normalized in self.validated_symbols:
            info = self.validated_symbols[normalized]
            info.error_count = max(0, info.error_count - 1)  # Reduce error count
            info.last_checked = datetime.now()
    
    def get_stats(self) -> Dict[str, any]:
        """Get validation statistics"""
        return {
            'blacklisted_count': len(self.blacklist),
            'validated_count': len(self.validated_symbols),
            'failed_count': len(self.failed_symbols),
            'total_processed': len(self.validated_symbols) + len(self.failed_symbols),
            'blacklist_sample': list(self.blacklist)[:10],
            'recent_failures': [
                {
                    'symbol': info.normalized,
                    'error': info.last_error,
                    'error_count': info.error_count,
                    'last_checked': info.last_checked.isoformat() if info.last_checked else None
                }
                for info in sorted(
                    self.failed_symbols.values(),
                    key=lambda x: x.last_checked or datetime.min,
                    reverse=True
                )[:5]
            ]
        }
    
    def cleanup_old_entries(self, days: int = 30):
        """Clean up old validation entries"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Clean up old failed symbols
        old_failed = [
            symbol for symbol, info in self.failed_symbols.items()
            if info.last_checked and info.last_checked < cutoff
        ]
        
        for symbol in old_failed:
            del self.failed_symbols[symbol]
        
        logger.info(f"Cleaned up {len(old_failed)} old failed symbol entries")

# Global validator instance
symbol_validator = SymbolValidator()
