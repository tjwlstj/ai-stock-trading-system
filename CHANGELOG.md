# Changelog

All notable changes to the AI Stock Trading System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
