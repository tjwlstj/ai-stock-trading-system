# CHANGELOG

## [1.2.5-beta] - 2025-11-17

### Changed
- **Backend Dependencies**: Conservative patch update for bug fixes and stability
  - Updated `fastapi` from 0.121.1 to 0.121.2 (bug fixes, stability improvements)

### Fixed
- Inherited bug fixes from FastAPI 0.121.2 (released 2025-11-13)

### Technical Details

**Commit Information**:
- Maintenance Type: Regular inspection and conservative patch update
- Update Strategy: Bug-fix oriented, backward-compatible changes only
- Testing: Dependency compatibility verified

**File Statistics**:
- Files changed: 4 (backend/requirements.txt, VERSION, CHANGELOG.md, VERSION_HISTORY.md)
- Backend dependency updates: 1 package (FastAPI)
- Breaking changes: None

**Version Management**:
- This is a **beta release** for testing and validation
- Version naming: 1.2.5-beta (incremental beta versioning)
- Previous beta: 1.2.4-beta (2025-11-10)
- Latest stable: 1.2.0 (2025-10-13)
- Stable release will be 1.2.5 after validation

**Deferred Updates**:
- OpenAI SDK v2.x migration (major version update with breaking changes)
  - Current: 1.54.4 (stable and secure)
  - Latest: 2.8.0 (requires migration effort and testing)

---

## [1.2.4-beta] - 2025-11-10

### Changed
- **Backend Dependencies**: Conservative minor and patch updates for bug fixes, stability, and security
  - Updated `fastapi` from 0.120.4 to 0.121.1 (new dependency scopes feature, bug fixes)
  - Updated `pydantic` from 2.12.3 to 2.12.4 (regression fixes, stability improvements)
  - Updated `httpx` from 0.27.2 to 0.28.1 (HTTP/2 improvements, bug fixes)
  - Updated `aiofiles` from 24.1.0 to 25.1.0 (async file I/O improvements)
  - Updated `aiosqlite` from 0.20.0 to 0.21.0 (async SQLite improvements)
  - Updated `python-dotenv` from 1.0.1 to 1.2.1 (environment variable handling improvements)
  - Updated `pytz` from 2024.2 to 2025.2 (latest timezone data)
  - Updated `tenacity` from 9.0.0 to 9.1.2 (retry logic improvements)
  - Updated `tiktoken` from 0.8.0 to 0.12.0 (token calculation accuracy improvements)

### Fixed
- Inherited bug fixes from FastAPI `0.120.5` to `0.121.1`:
  - Fixed `Depends(func, scope='function')` for top level (parameterless) dependencies
  - Fixed security schemes in OpenAPI when added at the top level app
  - Reduced internal cyclic recursion in dependencies
- Inherited bug fixes from Pydantic `2.12.4`:
  - Fixed forward references in parent `TypedDict` classes (Python 3.14+)
  - Fixed IP address type serialization with `serialize_as_any`
  - Fixed `collections.defaultdict` default value handling
  - Fixed field serializers on nested typed dictionaries

### Technical Details

**Commit Information**:
- Maintenance Type: Regular inspection and conservative updates
- Update Strategy: Bug-fix and stability-oriented, backward-compatible changes only
- Testing: Dependency compatibility verified, syntax checks passed

**File Statistics**:
- Files changed: 4 (backend/requirements.txt, VERSION, CHANGELOG.md, VERSION_HISTORY.md)
- Backend dependency updates: 9 packages
- Breaking changes: None

**Version Management**:
- This is a **beta release** for testing and validation
- Version naming: 1.2.4-beta (incremental beta versioning)
- Previous beta: 1.2.3-beta (2025-11-03)
- Latest stable: 1.2.0 (2025-10-13)
- Stable release will be 1.2.4 after validation

**Deferred Updates**:
- OpenAI SDK v2.x migration (major version update with breaking changes)
  - Current: 1.54.4 (stable and secure)
  - Latest: 2.7.1 (requires migration effort)
  - Plan: Separate update cycle with dedicated testing
- NumPy 2.x upgrade (major version update, pandas compatibility verification needed)
- Pytest 9.x upgrade (major version update, test suite verification needed)

## [1.2.3-beta] - 2025-11-03

### Changed
- **Backend Dependencies**: Conservative patch update for bug fixes and stability
  - Updated `fastapi` from 0.120.0 to 0.120.4

### Fixed
- Inherited bug fixes from FastAPI `0.120.1` to `0.120.4`:
  - Fixed an issue with schema separation for nested models introduced in `0.119.0`.
  - Resolved a bug in OpenAPI generation when security schemes are added at the top-level application.

### Technical Details

**Commit Information**:
- Maintenance Type: Regular inspection and conservative patch update
- Update Strategy: Bug-fix-oriented, backward-compatible changes only
- Testing: Dependency compatibility verified, syntax checks passed

**File Statistics**:
- Files changed: 3 (backend/requirements.txt, VERSION, CHANGELOG.md)
- Backend dependency updates: 1 package
- Breaking changes: None

**Version Management**:
- This is a **beta release** for testing and validation
- Version naming: 1.2.3-beta (incremental beta versioning)
- Previous beta: 1.2.2-beta (2025-10-27)
- Latest stable: 1.2.0 (2025-10-13)
- Stable release will be 1.2.3 after validation


All notable changes to the AI Stock Trading System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2-beta] - 2025-10-27

### Changed
- **Backend Dependencies**: Conservative minor and patch updates
  - Updated `fastapi` from 0.119.0 to 0.120.0 (internal documentation migration, no breaking changes)
  - Updated `sqlalchemy` from 2.0.43 to 2.0.44 (Python 3.14 compatibility, bug fixes)
  - Updated `pandas` from 2.2.3 to 2.3.3 (minor version update with improvements)
  - Updated `yfinance` from 0.2.44 to 0.2.66 (bug fixes and stability improvements)
  - Updated `uvicorn` from 0.30.6 to 0.38.0 (performance and stability improvements)
  - Updated `pydantic` from 2.9.2 to 2.12.3 (compatibility improvements with FastAPI 0.119+)
- **Frontend Dependencies**: Security vulnerability fixes
  - Applied automatic security patches via `pnpm audit --fix`
  - Fixed `brace-expansion` vulnerability (ESLint dependency)
  - Fixed `@eslint/plugin-kit` vulnerability
  - Updated `vite` to 7.1.12 (security patches applied via overrides)

### Security
- **All known vulnerabilities resolved**: `pnpm audit` now reports zero vulnerabilities
- Applied security patches for ESLint ecosystem
- Updated Vite to address file serving and filesystem access vulnerabilities

### Maintenance
- Regular dependency audit and security vulnerability assessment
- Maintained OpenAI SDK at 1.54.4 (v2.x migration deferred to separate update cycle)
- Verified all updates are backward-compatible with no breaking changes

### Technical Details

**Commit Information**:
- Maintenance Type: Regular inspection and conservative updates
- Update Strategy: Security-first, backward-compatible changes only
- Testing: Dependency compatibility verified

**File Statistics**:
- Files changed: 3 (backend/requirements.txt, frontend/package.json, VERSION)
- Backend dependency updates: 6 packages
- Frontend security fixes: 4 vulnerabilities resolved
- Breaking changes: None

**Version Management**:
- This is a **beta release** for testing and validation
- Version naming: 1.2.2-beta (incremental beta versioning)
- Previous beta: 1.2.1-beta (2025-10-20)
- Latest stable: 1.2.0 (2025-10-13)
- Stable release will be 1.2.2 after validation

**Deferred Updates**:
- OpenAI SDK v2.x migration (major version update with breaking changes)
  - Current: 1.54.4 (stable and secure)
  - Latest: 2.6.1 (requires migration effort)
  - Plan: Separate update cycle with dedicated testing

## [1.2.1-beta] - 2025-10-20

### Changed
- **Backend Dependencies**: Conservative security and stability updates
  - Updated `fastapi` from 0.115.0 to 0.119.0 (security improvements and bug fixes)
  - Updated `sqlalchemy` from 2.0.35 to 2.0.43 (security recommendations)
- **Frontend Dependencies**: Minor stability update
  - Updated `vite` from 6.3.5 to 6.4.0 (bug fixes and performance improvements)

### Security
- Applied recommended security patches for FastAPI (ReDoS, CSRF, Information Leakage mitigations)
- Updated SQLAlchemy to address potential security concerns

### Maintenance
- Regular dependency audit and security vulnerability assessment
- Verified pandas 2.2.3 stability (CVE-2024-42992 was rejected/withdrawn)
- Maintained OpenAI SDK at 1.54.4 (avoiding v2.x breaking changes)

### Technical Details

**Commit Information**:
- Maintenance Type: Regular inspection and conservative updates
- Update Strategy: Security-first, backward-compatible changes only
- Testing: Dependency compatibility verified

**File Statistics**:
- Files changed: 3 (backend/requirements.txt, frontend/package.json, VERSION)
- Dependency updates: 3 packages
- Breaking changes: None

**Version Management**:
- This is a **beta release** for testing and validation
- Version naming: 1.2.1-beta (incremental beta versioning)
- Stable release will be 1.2.1 after validation

## [1.2.0] - 2025-10-13

### Added
- Comprehensive async Redis client support across backend modules
- New test suite for async Redis functionality (`tests/test_async_redis_clients.py` - 154 lines)
- AsyncFakeRedis mock class for testing without actual Redis instance
- Market time calculation test suite (`test_market_time.py` - 37 lines)
- Helper methods for market trading day validation and date advancement
  - `_next_calendar_day()`: Safe date increment using timedelta
  - `_is_trading_day()`: Weekend and holiday validation
  - `_advance_to_next_trading_day()`: Intelligent trading day navigation

### Changed
- **Breaking**: Migrated Redis clients from synchronous to asynchronous (`redis.asyncio.Redis`)
  - Updated `backend/app/ai_quality_manager.py` (AIUsageOptimizer, AIQualityMonitor)
  - Updated `backend/app/cost_optimizer.py` (CostTracker, BudgetManager)
  - Updated `backend/app/realtime_data_manager.py` (SmartCache, MultiSourceDataProvider, RealTimeDataManager)
- Improved type hints using `TYPE_CHECKING` for better IDE support and optional dependency handling
- Refactored `next_market_open()` logic in `backend/app/utils/market_time.py`
  - Replaced complex while loops with dedicated helper methods
  - Improved code readability and maintainability
  - Eliminated manual date arithmetic errors

### Fixed
- **Critical**: Fixed date rollover bug in market session calculations
  - Resolved month-end boundary issues (e.g., Jan 31 → Feb 1)
  - Resolved year-end holiday handling (e.g., Dec 31 → Jan 2)
  - Fixed Independence Day and other holiday skip logic
  - Prevented incorrect date calculations using `timedelta(days=1)`
- Added proper bytes decoding for Redis cached data
- Improved timestamp parsing with ISO format fallback handling (handles both standard and 'Z' suffix)
- Fixed potential data type issues in Redis responses (bytes vs string)

### Performance
- Enhanced system scalability through async I/O operations
- Improved Redis response handling with proper encoding/decoding
- Reduced blocking operations in data access layers

### Testing
- Added 154 lines of async Redis client tests covering:
  - SmartCache async operations
  - AIQualityMonitor metrics recording
  - AIUsageOptimizer graceful degradation without Redis
  - CostTracker async storage operations
- Added 37 lines of market time calculation tests covering:
  - Month-end rollover scenarios
  - Year-end holiday handling
  - Independence Day and special holiday cases

### Technical Details

**Commit Information**:
- Latest Commit: `e7d4e9b416276953bd2e77480c93c32abbfad44f`
- Commit Date: 2025-10-13 10:09:21 +0900
- Merged PRs: 
  - #2: Fix market session next open rollover handling
  - #1: Switch backend Redis usage to redis.asyncio

**File Statistics**:
- Total files changed: 6
- Lines added: 270
- Lines deleted: 34
- New files created: 2

**Dependencies**:
- Requires `redis-py` with asyncio support (`redis.asyncio`)
- Python 3.7+ for async/await support
- Compatible with existing synchronous codebase through gradual migration

**Migration Notes**:
- All Redis client instantiations now use `AsyncRedis` type hint
- Redis operations are now awaitable (use `await` keyword)
- Backward compatibility maintained through optional Redis client parameters

## [1.1.0] - 2025-09-27

### Added
- **Backend Server**: Created `backend/main.py` with Flask-based API server
- **OpenAI Wrapper**: Added `backend/openai_wrapper.py` with retry logic, timeout handling, and error recovery
- **Environment Configuration**: Added `.env.example` with comprehensive configuration options
- **Frontend API Client**: Created `frontend/src/utils/api.js` for secure backend communication
- **CI/CD Pipeline**: Added GitHub Actions workflow for automated testing
- **Integration Tests**: Added comprehensive backend integration tests
- **Security Enhancements**: Improved .gitignore to prevent sensitive data exposure

### Fixed
- **Database Concurrency**: Enabled SQLite WAL mode for better concurrent access
- **Requirements**: Removed invalid `sqlite3` entry from requirements.txt (built-in module)
- **CORS Configuration**: Added proper CORS setup for frontend-backend communication
- **Node.js Compatibility**: Relaxed Node.js requirement from 22+ to 20+ (LTS)
- **API Key Security**: Ensured sensitive keys are only used in backend, never exposed to frontend

### Changed
- **Data Source Accuracy**: Updated "Live market data" to "Near real-time market data (with potential delays)"
- **Setup Instructions**: Improved README with proper backend server startup commands
- **Environment Variables**: Enhanced configuration with separate frontend and backend env files
- **Error Handling**: Added comprehensive error handling and logging throughout the system

### Security
- **API Key Protection**: Implemented secure API key handling with environment variable validation
- **Input Validation**: Added input validation and sanitization for API endpoints
- **Rate Limiting**: Prepared infrastructure for API rate limiting
- **Vulnerability Scanning**: Added Trivy security scanning to CI pipeline

### Technical Improvements
- **Database Performance**: Optimized SQLite configuration with WAL mode and performance pragmas
- **API Reliability**: Implemented exponential backoff retry logic for OpenAI API calls
- **Token Management**: Added token counting and usage tracking for OpenAI API
- **Health Monitoring**: Added comprehensive health check endpoint with database connectivity test
- **Logging**: Enhanced logging configuration with configurable levels and file output

### Documentation
- **Setup Guide**: Improved installation and configuration instructions
- **API Documentation**: Added inline documentation for all API endpoints
- **Environment Setup**: Detailed environment variable configuration guide
- **Testing Guide**: Added instructions for running tests and CI pipeline

### Infrastructure
- **Multi-Environment Support**: Added support for development, testing, and production environments
- **Container Ready**: Prepared configuration for containerization
- **Monitoring Ready**: Added endpoints and logging for monitoring integration
- **Scalability**: Prepared architecture for horizontal scaling

## [1.0.0] - Initial Release

### Added
- Multi-agent AI analysis system
- Basic frontend with React and Tailwind CSS
- SQLite database integration
- Yahoo Finance data collection
- OpenAI API integration
- Basic portfolio management features


