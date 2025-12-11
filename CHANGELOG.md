# CHANGELOG

## [1.3.0] - 2025-12-11

### Changed
- **Stable Release**: Promoted from v1.2.8-beta after successful testing and validation
- **Backend Dependencies**: Comprehensive updates with security patches and stability improvements
  - Updated `fastapi` from 0.115.0 to 0.124.0 (9 minor versions)
    - New dependency scopes feature
    - OpenAPI generation bug fixes
    - Enhanced tracebacks with endpoint metadata
    - Improved dependency caching
  - Updated `uvicorn` from 0.30.6 to 0.38.0 (performance improvements)
  - Updated `pydantic` from 2.9.2 to 2.12.5 (regression fixes, stability improvements)
  - Updated `sqlalchemy` from 2.0.35 to 2.0.44 (Python 3.14 compatibility)
  - Updated `httpx` from 0.27.2 to 0.28.1 (HTTP/2 improvements)
  - Updated `aiofiles` from 24.1.0 to 25.1.0 (async file I/O improvements)
  - Updated `aiosqlite` from 0.20.0 to 0.21.0 (async SQLite improvements)
  - Updated `python-dotenv` from 1.0.1 to 1.2.1 (environment variable handling)
  - Updated `tenacity` from 9.0.0 to 9.1.2 (retry logic improvements)
  - Updated `tiktoken` from 0.8.0 to 0.12.0 (token calculation accuracy)
  - Updated `pandas` from 2.2.3 to 2.3.3 (performance improvements)
  - Updated `yfinance` from 0.2.44 to 0.2.66 (bug fixes, stability)
  - Updated `pytz` from 2024.2 to 2025.2 (latest timezone data)

### Security
- **Frontend Dependencies**: Resolved 4+ security vulnerabilities
  - Fixed `@modelcontextprotocol/sdk` (GHSA-w48q-cv73-mx4w) - High severity DNS rebinding protection issue
  - Fixed `js-yaml` (CVE-2025-64718) - Prototype pollution vulnerability
  - Fixed `body-parser` (CVE-2025-13466) - DoS vulnerability with URL encoding
  - All known vulnerabilities resolved

### Fixed
- Inherited bug fixes from FastAPI 0.115.0 → 0.124.0
  - Fixed `Depends(func, scope='function')` for top-level dependencies
  - Fixed security schemes in OpenAPI when added at the top-level app
  - Reduced internal cyclic recursion in dependencies
  - Improved dependency caching for dependencies without scopes
- Inherited bug fixes from Pydantic 2.9.2 → 2.12.5
  - Fixed forward references in parent `TypedDict` classes (Python 3.14+)
  - Fixed IP address type serialization with `serialize_as_any`
  - Fixed `collections.defaultdict` default value handling
  - Fixed field serializers on nested typed dictionaries
  - Fixed MISSING sentinel issue

### Technical Details

**Release Information**:
- Release Type: Stable release (promoted from beta)
- Beta Period: 7 weeks (2025-10-20 to 2025-12-08)
- Beta Versions: 8 versions (v1.2.1-beta through v1.2.8-beta)
- Update Strategy: Conservative, security-first, backward-compatible changes only
- Testing: 16 tests passed, 0 failed (see [TEST_RESULTS_2025-12-11.md](./TEST_RESULTS_2025-12-11.md))

**File Statistics**:
- Files changed: 4 (VERSION, CHANGELOG.md, VERSION_HISTORY.md, TEST_RESULTS_2025-12-11.md)
- Backend dependency updates: 14 packages
- Frontend security fixes: 4+ vulnerabilities resolved
- Breaking changes: None

**Version Management**:
- Previous stable: v1.2.0 (2025-10-13)
- Version increment: MINOR (1.2.0 → 1.3.0)
- Reasoning: Multiple minor dependency updates, security patches, and stability improvements
- Semantic Versioning: Adheres to SemVer 2.0.0 (no breaking changes, backward compatible)

**Deferred Updates**:
- OpenAI SDK v2.x migration (major version update with breaking changes)
  - Current: 1.54.4 (stable and secure)
  - Latest: 2.x.x (requires migration effort and testing)
  - Plan: Separate update cycle with dedicated testing in future release

**Reference Documents**:
- [Test Results](./TEST_RESULTS_2025-12-11.md)
- [Comprehensive Analysis Report](./comprehensive_analysis_report.md)
- [Version Update Feasibility](./version_update_feasibility.md)
- [Beta Version Analysis](./beta_version_analysis.md)

---

## [1.2.8-beta] - 2025-12-08

### Changed
- **Backend Dependencies**: Conservative minor version update
  - Updated `fastapi` from 0.123.0 to 0.124.0 (traceback improvements with endpoint metadata)

### Security
- **Frontend Dependencies**: High-priority security vulnerability fix
  - Fixed `@modelcontextprotocol/sdk` vulnerability (GHSA-w48q-cv73-mx4w) - DNS rebinding protection issue
  - Applied automatic security patch via `pnpm audit --fix`
  - All known vulnerabilities resolved

### Fixed
- Inherited improvements from FastAPI 0.124.0 (released 2025-12-06)
  - Enhanced tracebacks by adding endpoint metadata for better debugging
  - Improved error context visibility during development

### Technical Details

**Commit Information**:
- Maintenance Type: Regular inspection and conservative updates
- Update Strategy: Security-first, debugging improvements, backward-compatible changes only
- Testing: Dependency compatibility verified, security audit passed

**File Statistics**:
- Files changed: 5 (backend/requirements.txt, frontend/package.json, VERSION, CHANGELOG.md, VERSION_HISTORY.md)
- Backend dependency updates: 1 package (FastAPI)
- Frontend security fixes: 1 high-severity vulnerability resolved (@modelcontextprotocol/sdk)
- Breaking changes: None

**Version Management**:
- This is a **beta release** for testing and validation
- Version naming: 1.2.8-beta (incremental beta versioning)
- Previous beta: 1.2.7-beta (2025-12-01)
- Latest stable: 1.2.0 (2025-10-13)
- Stable release will be 1.2.8 after validation

**Deferred Updates**:
- OpenAI SDK v2.x migration (major version update with breaking changes)
  - Current: 1.54.4 (stable and secure)
  - Latest: 2.x.x (requires migration effort and testing)
  - Plan: Separate update cycle with dedicated testing in v1.3.0

**Reference Documents**:
- [Inspection Report](./inspection_findings_2025-12-08.md)

---

## [1.2.7-beta] - 2025-12-01

### Changed
- **Backend Dependencies**: Conservative minor and patch updates for bug fixes and stability
  - Updated `fastapi` from 0.121.3 to 0.123.0 (dependency caching improvements)
  - Updated `pydantic` from 2.12.4 to 2.12.5 (MISSING sentinel fix, documentation improvements)

### Security
- **Frontend Dependencies**: Security vulnerability fixes
  - Fixed `js-yaml` vulnerability (CVE-2025-64718) - Prototype pollution issue
  - Fixed `body-parser` vulnerability (CVE-2025-13466) - DoS vulnerability with URL encoding
  - Applied automatic security patches via `pnpm audit --fix`
  - All known vulnerabilities resolved

### Fixed
- Inherited bug fixes from FastAPI 0.123.0 (released 2025-11-30)
  - Improved dependency caching for dependencies without scopes
- Inherited bug fixes from Pydantic 2.12.5 (released 2025-11-26)
  - Fixed MISSING sentinel issue
  - Documentation improvements

### Technical Details

**Commit Information**:
- Maintenance Type: Regular inspection and conservative updates
- Update Strategy: Security-first, bug-fix oriented, backward-compatible changes only
- Testing: Dependency compatibility verified, syntax checks passed

**File Statistics**:
- Files changed: 5 (backend/requirements.txt, frontend/package.json, VERSION, CHANGELOG.md, VERSION_HISTORY.md)
- Backend dependency updates: 2 packages (FastAPI, Pydantic)
- Frontend security fixes: 2 vulnerabilities resolved (js-yaml, body-parser)
- Breaking changes: None

**Version Management**:
- This is a **beta release** for testing and validation
- Version naming: 1.2.7-beta (incremental beta versioning)
- Previous beta: 1.2.6-beta (2025-11-24)
- Latest stable: 1.2.0 (2025-10-13)
- Stable release will be 1.2.7 after validation

**Deferred Updates**:
- OpenAI SDK v2.x migration (major version update with breaking changes)
  - Current: 1.54.4 (stable and secure)
  - Latest: 2.8.1 (requires migration effort and testing)
  - Plan: Separate update cycle with dedicated testing in v1.3.0

**Reference Documents**:
- [점검 중간 결과](./inspection_findings_2025-12-01.md)
- [기술 동향 조사](./tech_research_2025-12-01.md)

---

## [1.2.6-beta] - 2025-11-24

### Changed
- **Backend Dependencies**: Conservative patch update for bug fixes and stability
  - Updated `fastapi` from 0.121.2 to 0.121.3 (internal refactoring, dependency bump)

### Fixed
- Inherited bug fixes from FastAPI 0.121.3 (released 2025-11-19)

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
- Version naming: 1.2.6-beta (incremental beta versioning)
- Previous beta: 1.2.5-beta (2025-11-17)
- Latest stable: 1.2.0 (2025-10-13)
- Stable release will be 1.2.6 after validation

**Deferred Updates**:
- OpenAI SDK v2.x migration (major version update with breaking changes)
  - Current: 1.54.4 (stable and secure)
  - Latest: 2.8.1 (requires migration effort and testing)

---

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
- **Critical**: Fixed date rollover bug in `next_market_open()` calculation
  - Issue: When market was closed on a Friday at 23:00, the function would incorrectly return Monday 09:30 of the *same week* instead of the *next week*
  - Root cause: Direct date manipulation (`date.day + 1`) caused month/year overflow
  - Solution: Use `timedelta(days=1)` for safe date arithmetic
  - Impact: Affects all market time-dependent features (trading schedules, data collection timing)
- Improved error handling in async Redis operations
- Enhanced test coverage for edge cases in market time calculations

### Testing
- Added comprehensive test suite for async Redis clients (154 lines)
- Added market time calculation tests covering edge cases
- All tests passing with new async implementation
- Verified backward compatibility with existing codebase

### Documentation
- Updated inline documentation for async Redis usage
- Added docstrings for new helper methods in market time module
- Documented breaking changes and migration path

### Technical Details
- Python version: 3.11+
- Redis client: `redis.asyncio.Redis`
- Testing framework: pytest with pytest-asyncio
- Type checking: mypy-compatible type hints

---

**Migration Notes for v1.2.0**:
- If using Redis features, ensure async/await syntax is used
- Update any custom Redis client instantiation to use `redis.asyncio.Redis`
- Review market time-dependent logic for correctness with the bug fix

## [1.1.0] - 2025-09-27

### Added
- Flask-based backend server implementation
- OpenAI API wrapper with error handling and retry logic
- Environment variable configuration support
- Basic logging infrastructure

### Changed
- Migrated from prototype to production-ready backend architecture
- Improved API endpoint structure and naming conventions

### Technical Details
- Backend framework: Flask
- AI integration: OpenAI API
- Configuration: python-dotenv

## [1.0.0] - Initial Release

### Features
- Multi-agent AI analysis system with optimistic and pessimistic agents
- React-based frontend with Tailwind CSS styling
- SQLite database integration for data persistence
- Yahoo Finance data collection and processing
- OpenAI API integration for AI-powered stock analysis
- Basic portfolio management functionality
- Real-time stock data visualization
- User authentication and session management

### Technical Stack
- **Frontend**: React 19, Tailwind CSS 4, Vite 7
- **Backend**: FastAPI, SQLAlchemy
- **Database**: SQLite with async support
- **AI/ML**: OpenAI API, custom multi-agent system
- **Data Source**: Yahoo Finance (yfinance)

### Architecture
- Multi-agent AI system with coordinated decision-making
- RESTful API design
- Async/await pattern for improved performance
- Modular component structure

---

**Document Version**: 1.2
**Last Updated**: 2025-12-01
**Maintainer**: Manus AI
