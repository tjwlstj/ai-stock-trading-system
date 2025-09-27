"""
Database configuration utilities
Optimizes SQLite settings for concurrent access and performance
"""

import logging
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
import sqlite3

logger = logging.getLogger(__name__)

def configure_sqlite_for_production(engine: Engine) -> None:
    """
    Configure SQLite engine for production use with WAL mode and optimizations
    
    Args:
        engine: SQLAlchemy engine instance
    """
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragmas for optimal performance and concurrency"""
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            
            # Enable WAL mode for better concurrent access
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # Optimize performance settings
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed
            cursor.execute("PRAGMA cache_size=10000")    # 10MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")    # Use memory for temp tables
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            
            # Set busy timeout for concurrent access
            cursor.execute("PRAGMA busy_timeout=30000")  # 30 seconds
            
            cursor.close()
            
            logger.debug("SQLite pragmas configured for production")

def get_sqlite_connection_args() -> dict:
    """
    Get SQLite connection arguments for optimal configuration
    
    Returns:
        Dictionary of connection arguments
    """
    return {
        "check_same_thread": False,  # Allow multi-threading
        "timeout": 30,               # Connection timeout
        "isolation_level": None,     # Autocommit mode
    }
