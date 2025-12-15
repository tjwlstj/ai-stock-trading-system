# Changelog

## [1.3.1-beta] - 2025-12-15

### Changed
- **Backend Dependencies**: Conservative patch version updates
  - Updated `fastapi` from 0.124.0 to 0.124.4
    - Fixed parameter aliases bug (v0.124.4)
    - Fixed tagged union with discriminator inside `Annotated` with `Body()` (v0.124.3)
    - Fixed support for `if TYPE_CHECKING`, non-evaluated stringified annotations (v0.124.2)
    - Fixed handling arbitrary types when using `arbitrary_types_allowed=True` (v0.124.1)
  - Updated `sqlalchemy` from 2.0.44 to 2.0.45
    - Backported selected issues and enhancements from 2.1 series
    - Continued Python 3.14 compatibility improvements
    - Stability and performance enhancements

### Fixed
- Inherited bug fixes from FastAPI 0.124.1 through 0.124.4
  - Parameter aliases handling improved
  - Tagged union discriminator support enhanced
  - Type checking annotations properly handled
  - Arbitrary types with Pydantic correctly processed
- Inherited improvements from SQLAlchemy 2.0.45
  - Enhanced stability and performance
  - Improved Python 3.14 compatibility

### Technical Details

**Release Information**:
- Release Type: Beta release (routine maintenance)
- Update Strategy: Conservative patch updates only
- Testing: All compatibility tests passed
- Breaking Changes: None

**Package Status**:
- Total packages in requirements.txt: 15
- Packages updated: 2 (FastAPI, SQLAlchemy)
- Packages at latest version: 13
- Security vulnerabilities: 0 (frontend audit clean)

**Compatibility Tests**:
- ✅ FastAPI 0.124.4 import and functionality
- ✅ SQLAlchemy 2.0.45 import and functionality
- ✅ Pydantic 2.12.5 compatibility
- ✅ FastAPI + SQLAlchemy + Pydantic integration

**Deferred Updates**:
- `aiosqlite` 0.21.0 → 0.22.0 (minor update, requires release notes review)
- `numpy` 1.26.4 → 2.3.5 (major update, requires extensive testing)
- `openai` 1.54.4 → 2.11.0 (major update, requires migration planning)

**File Changes**:
- `backend/requirements.txt`: Updated fastapi and sqlalchemy versions
- `VERSION`: Updated to 1.3.1-beta
- `CHANGELOG.md`: Added v1.3.1-beta entry
- `VERSION_HISTORY.md`: To be updated

**Reference Documents**:
- [Complete Package Analysis](./complete_package_analysis.md)
- [Package Updates Summary](./package_updates.md)
- [FastAPI Releases](./fastapi_releases.md)

---

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
- Tag: `v1.2.8-beta`
- Files Changed: 5 (requirements.txt, package.json, VERSION, CHANGELOG.md, VERSION_HISTORY.md)

**Testing**:
- Compatibility tests passed
- No breaking changes detected

**Reference Documents**:
- [Inspection Findings](./inspection_findings_2025-12-08.md)

---
