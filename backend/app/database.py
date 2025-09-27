"""
Database Management
Async SQLAlchemy setup with SQLite WAL mode for better concurrency
"""

import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import logging

from .settings import settings

logger = logging.getLogger(__name__)

# Database engine
engine = create_async_engine(
    settings.async_db_url,
    echo=settings.is_development,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.async_db_url else {}
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

async def init_db():
    """Initialize database with optimizations"""
    try:
        # Create data directory if it doesn't exist
        db_dir = os.path.dirname(settings.DATABASE_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        # Configure SQLite for better performance and concurrency
        if "sqlite" in settings.async_db_url:
            async with engine.begin() as conn:
                # Enable WAL mode for better concurrency
                await conn.execute(text("PRAGMA journal_mode=WAL"))
                # Set synchronous mode to NORMAL for better performance
                await conn.execute(text("PRAGMA synchronous=NORMAL"))
                # Increase cache size
                await conn.execute(text("PRAGMA cache_size=10000"))
                # Use memory for temporary storage
                await conn.execute(text("PRAGMA temp_store=MEMORY"))
                # Set busy timeout
                await conn.execute(text("PRAGMA busy_timeout=30000"))
                
                logger.info("SQLite optimizations applied")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

@asynccontextmanager
async def get_db_session():
    """Get database session with proper cleanup"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_db():
    """Dependency for FastAPI to get database session"""
    async with get_db_session() as session:
        yield session

async def health_check_db():
    """Check database connectivity"""
    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
