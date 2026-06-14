# 🗄️ Database Configuration Guide

## SQLite Configuration (Default)

The system uses SQLite by default with optimized settings for better performance and concurrency.

### Optimizations Applied

**WAL Mode (Write-Ahead Logging)**
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 1000000;
PRAGMA foreign_keys = ON;
PRAGMA temp_store = MEMORY;
```

**Benefits:**
- ✅ Better concurrent read/write performance
- ✅ Reduced database locking
- ✅ Improved crash recovery
- ✅ Faster queries with larger cache

### Concurrent Access Considerations

**SQLite Limitations:**
- Multiple readers: ✅ Supported
- Multiple writers: ⚠️ Limited (one writer at a time)
- High concurrency: ❌ Not recommended for >100 concurrent users

**Best Practices:**
- Use connection pooling
- Keep transactions short
- Implement retry logic for busy database errors
- Monitor database file size and performance

### File Structure
```
data/
├── stock_data.db          # Main database file
├── stock_data.db-wal      # WAL file (auto-generated)
└── stock_data.db-shm      # Shared memory file (auto-generated)
```

⚠️ **Important**: Never delete WAL/SHM files while the application is running.

## PostgreSQL Migration (Production)

For production environments with high concurrency, migrate to PostgreSQL.

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Docker:**
```bash
docker run --name postgres-db \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=stock_trading \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Update Environment Variables

Add to your `.env` file:
```env
# PostgreSQL Configuration
DB_URL=postgresql://username:password@localhost:5432/stock_trading
DATABASE_TYPE=postgresql

# Connection Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
```

### 3. Install PostgreSQL Dependencies

Add to `backend/requirements.txt`:
```
asyncpg==0.29.0
psycopg2-binary==2.9.9
```

### 4. Update Database Configuration

Modify `backend/app/database.py`:
```python
from sqlalchemy.ext.asyncio import create_async_engine

# PostgreSQL-specific engine
if settings.DATABASE_TYPE == "postgresql":
    engine = create_async_engine(
        settings.DB_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        echo=settings.LOG_LEVEL == "DEBUG"
    )
else:
    # SQLite engine (existing code)
    engine = create_async_engine(
        settings.DB_URL,
        connect_args={"check_same_thread": False}
    )
```

### 5. Database Migration

**Create Migration Script:**
```python
# scripts/migrate_to_postgresql.py
import asyncio
import sqlite3
import asyncpg
from sqlalchemy import create_engine

async def migrate_data():
    # Export from SQLite
    sqlite_conn = sqlite3.connect('data/stock_data.db')
    
    # Import to PostgreSQL
    pg_conn = await asyncpg.connect(
        'postgresql://username:password@localhost:5432/stock_trading'
    )
    
    # Migrate tables and data
    # ... migration logic here
    
    await pg_conn.close()
    sqlite_conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_data())
```

## Performance Monitoring

### SQLite Monitoring

**Check Database Size:**
```bash
ls -lh data/stock_data.db*
```

**Analyze Performance:**
```sql
-- Enable query analysis
PRAGMA compile_options;
EXPLAIN QUERY PLAN SELECT * FROM stocks WHERE symbol = 'AAPL';
```

**Monitor WAL File:**
```bash
# WAL file should be periodically checkpointed
watch -n 5 'ls -lh data/stock_data.db-wal'
```

### PostgreSQL Monitoring

**Connection Stats:**
```sql
SELECT * FROM pg_stat_activity WHERE datname = 'stock_trading';
```

**Performance Stats:**
```sql
SELECT * FROM pg_stat_user_tables;
SELECT * FROM pg_stat_user_indexes;
```

## Backup Strategies

### SQLite Backup

**Simple File Copy (when app is stopped):**
```bash
cp data/stock_data.db data/backup_$(date +%Y%m%d_%H%M%S).db
```

**Online Backup (while app is running):**
```bash
sqlite3 data/stock_data.db ".backup data/backup_$(date +%Y%m%d_%H%M%S).db"
```

**Automated Backup Script:**
```bash
#!/bin/bash
# scripts/backup_sqlite.sh
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR

sqlite3 data/stock_data.db ".backup $BACKUP_DIR/stock_data_$(date +%Y%m%d_%H%M%S).db"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "stock_data_*.db" -mtime +7 -delete
```

### PostgreSQL Backup

**Using pg_dump:**
```bash
pg_dump -h localhost -U username -d stock_trading > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Automated with cron:**
```bash
# Add to crontab: crontab -e
0 2 * * * /path/to/backup_postgresql.sh
```

## Troubleshooting

### Common SQLite Issues

**Database Locked Error:**
```python
# Implement retry logic
import time
import sqlite3

def execute_with_retry(query, max_retries=5):
    for attempt in range(max_retries):
        try:
            # Execute query
            return cursor.execute(query)
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                continue
            raise
```

**WAL File Growing Too Large:**
```sql
-- Force checkpoint
PRAGMA wal_checkpoint(TRUNCATE);
```

**Corruption Detection:**
```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

### PostgreSQL Issues

**Connection Pool Exhaustion:**
```python
# Monitor pool status
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    print(f"Pool size: {engine.pool.size()}")
    print(f"Checked out: {engine.pool.checkedout()}")
```

**Slow Queries:**
```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();
```

## Environment-Specific Recommendations

### Development
- ✅ SQLite with WAL mode
- ✅ Local file storage
- ✅ Simple backup strategy

### Staging
- ⚠️ SQLite (acceptable for testing)
- ✅ Regular backups
- ✅ Performance monitoring

### Production
- ✅ PostgreSQL with connection pooling
- ✅ Automated backups
- ✅ Monitoring and alerting
- ✅ Read replicas for scaling
- ✅ Connection pooling (PgBouncer)

## Migration Checklist

- [ ] Backup existing SQLite database
- [ ] Set up PostgreSQL instance
- [ ] Update environment variables
- [ ] Install PostgreSQL dependencies
- [ ] Run migration script
- [ ] Test all API endpoints
- [ ] Verify data integrity
- [ ] Update deployment scripts
- [ ] Monitor performance
- [ ] Set up backup automation
