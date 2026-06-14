# 🤖 AI Stock Trading System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-red.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **⚠️ Research & Educational Tool Only**  
> This system is designed for market analysis and educational purposes. It does NOT execute trades or provide financial advice.

A sophisticated AI-powered stock analysis system that combines multiple data sources with advanced language models to provide comprehensive market insights and research capabilities.

> ### 🇰🇷 프로젝트 방향 (2026~)
> 본 프로젝트는 **국내(KRX) 시장 기준의, 실거래까지 연결 가능한 AI 보조 트레이딩 시스템**으로 재설계 중입니다.
> 브로커는 어댑터로 추상화하며(개발=PaperBroker/KIS 모의투자, 실거래 타깃=토스증권 Open API), **LLM은 신호만 생성하고 주문은 RiskGuard·수동 확인 게이트를 반드시 통과**합니다.
> 전체 설계·증권사 API 비교·로드맵은 **[국내(KRX) 아키텍처 설계 문서](docs/ARCHITECTURE_KRX.md)** 를 참고하세요.
>
> **현재 상태(정직 고지)**: 아직 주문 실행 기능은 없습니다(분석 전용). 위 설계는 단계적으로 구현됩니다. README의 일부 기능 설명은 목표치이며 실제 구현과 다를 수 있습니다.

## ✨ Features

### 🧠 **Multi-Agent AI Analysis**
- **OpenAI GPT-4o Mini Integration**: Latest OpenAI model with modern API compatibility
- **Structured Analysis Output**: JSON-formatted responses with confidence scores
- **Consensus-Based Decisions**: Multiple AI agents provide weighted recommendations  
- **Technical & Fundamental Analysis**: Comprehensive evaluation of market conditions
- **Risk Assessment**: Intelligent risk profiling and scenario analysis
- **Fallback AI Providers**: Multiple AI provider support for enhanced reliability

### 📊 **Real-Time Market Data**
- **Near Real-Time Quotes**: Yahoo Finance integration with smart caching (15-20 min delay)
- **Market Hours Awareness**: Intelligent data freshness based on trading sessions
- **Multi-Exchange Support**: US, UK, Japan, Hong Kong, and Chinese markets
- **Fallback Mechanisms**: Robust error handling and data source redundancy
- **Data Validation**: Anomaly detection and data quality checks

### 🏗️ **Production-Ready Architecture**
- **FastAPI Backend**: High-performance async API with automatic documentation
- **React Frontend**: Modern, responsive user interface with real-time updates
- **SQLite with WAL Mode**: Optimized database with concurrent access support
- **PostgreSQL Support**: Production-grade database option
- **Docker Support**: Containerized deployment with docker-compose
- **API Versioning**: Structured API versioning for backward compatibility

### 🔒 **Enterprise Security**
- **Environment-Based Configuration**: Secure API key management
- **Input Validation**: Comprehensive request/response validation with Pydantic
- **Rate Limiting**: Advanced API protection with user-based and IP-based limits
- **Audit Logging**: Complete activity tracking for compliance
- **CORS Security**: Production-ready CORS configuration
- **Secrets Management**: Support for external secret management systems

### 🚀 **Performance & Monitoring**
- **Redis Caching**: Optional Redis integration for enhanced performance
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Monitoring**: Comprehensive health checks and metrics
- **Error Tracking**: Advanced error handling and reporting
- **Performance Metrics**: Built-in performance monitoring

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (recommended: 3.11 or 3.12)
- **Node.js 20+** (LTS version recommended)
- **pnpm** (package manager)
- **Redis** (optional, for enhanced caching)

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/tjwlstj/ai-stock-trading-system.git
cd ai-stock-trading-system

# Verify environment
./scripts/verify_env.sh
```

### 2. Configuration

```bash
# Copy environment templates
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# Edit .env and add your API keys
nano .env
```

**Required Environment Variables:**

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OPENAI_API_KEY` | - | ✅ **Yes** | OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys) |
| `BACKEND_PORT` | `8000` | No | Backend server port |
| `CORS_ALLOW_ORIGINS` | `http://localhost:5173` | No | Allowed frontend origins (comma-separated) |
| `VITE_API_BASE` | `http://localhost:8000` | No | Backend API URL for frontend |
| `REDIS_URL` | - | No | Redis connection URL for caching |

**Enhanced .env file:**
```env
# OpenAI Configuration [REQUIRED]
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
OPENAI_MAX_RETRY=5

# Backend Configuration
BACKEND_PORT=8000
APP_ENV=development
CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173

# Database Configuration
DATABASE_PATH=data/stock_data.db
DATABASE_TYPE=sqlite
YF_CACHE_DIR=.cache/yf

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=3600

# Security Configuration
SECRET_KEY=your-secret-key-here
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_CORRELATION_ID=true

# Monitoring Configuration
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=30
```

**Enhanced frontend/.env.local file:**
```env
# Frontend Configuration
VITE_API_BASE=http://localhost:8000
VITE_API_TIMEOUT=10000
VITE_APP_NAME=AI Stock Trading System
VITE_ENABLE_DEBUG=true
VITE_API_VERSION=v1
```

### 3. Installation & Launch

**Option A: Using Make (Recommended)**
```bash
make setup    # Install dependencies
make start    # Start both backend and frontend
```

**Option B: Manual Setup**
```bash
# Backend (FastAPI with Uvicorn)
cd backend
pip install -r requirements.txt

# Development mode (with auto-reload)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the main.py entry point
python main.py

# Frontend (in new terminal)
cd frontend
pnpm install
pnpm run dev --host 0.0.0.0 --port 5173
```

**Option C: Docker with Redis**
```bash
# Start with Redis caching
docker-compose -f docker-compose.yml -f docker-compose.redis.yml up -d

# Or basic setup
docker-compose up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📖 Documentation

### Core Guides
- 📋 **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference with examples
- 🗄️ **[Database Guide](docs/DATABASE_GUIDE.md)** - SQLite optimization & PostgreSQL migration
- 🧪 **[Testing Guide](docs/TESTING_GUIDE.md)** - Comprehensive testing strategies
- 🔒 **[Security Guide](docs/SECURITY_GUIDE.md)** - Security best practices & compliance
- 🎨 **[Frontend Guide](docs/FRONTEND_GUIDE.md)** - UI/UX patterns & React best practices

### Quick References
- 🔧 **Configuration**: Environment variables and settings
- 🐳 **Docker**: Containerized deployment options
- 📊 **Monitoring**: Health checks and performance metrics
- 🚨 **Troubleshooting**: Common issues and solutions

## 🏛️ Architecture

### Enhanced System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  External APIs  │
│                 │    │                 │    │                 │
│ • Dashboard     │◄──►│ • Stock Data    │◄──►│ • Yahoo Finance │
│ • Analysis UI   │    │ • AI Analysis   │    │ • OpenAI GPT    │
│ • Portfolio     │    │ • Portfolio Mgmt│    │ • Market Data   │
│ • Error Boundary│    │ • Rate Limiting │    │ • Backup APIs   │
└─────────────────┘    │ • Caching Layer │    └─────────────────┘
                       │ • Monitoring    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  SQLite/PgSQL   │    │  Redis Cache    │
                       │                 │    │                 │
                       │ • Stock Quotes  │    │ • API Responses │
                       │ • Analysis Data │    │ • Market Data   │
                       │ • User Portfolio│    │ • Session Data  │
                       │ • Audit Logs    │    └─────────────────┘
                       └─────────────────┘
```

### Technology Stack

**Backend**
- **FastAPI**: Modern Python web framework with automatic API documentation
- **SQLAlchemy**: Async ORM with SQLite (WAL mode) and PostgreSQL support
- **Pydantic**: Data validation and serialization
- **OpenAI GPT-4o Mini**: Latest model with modern Chat Completions API
- **httpx**: Async HTTP client for external APIs
- **Tenacity**: Retry logic and circuit breakers
- **Redis**: Optional caching layer for enhanced performance
- **Prometheus**: Metrics collection and monitoring

**Frontend**
- **React 18**: Modern UI library with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Responsive chart library
- **React Query**: Data fetching and caching
- **Error Boundaries**: Comprehensive error handling

**Infrastructure**
- **Docker**: Containerization and deployment
- **SQLite**: Default database with WAL mode optimization
- **PostgreSQL**: Production database option
- **Redis**: Caching and session management
- **GitHub Actions**: CI/CD pipeline
- **Prometheus + Grafana**: Monitoring stack

## 🔧 Enhanced Configuration Reference

### Backend Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | **Required**: OpenAI API key for AI analysis |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model for analysis |
| `OPENAI_TIMEOUT` | `30` | API timeout in seconds |
| `OPENAI_MAX_RETRY` | `5` | Maximum retry attempts |
| `BACKEND_PORT` | `8000` | Backend server port |
| `DATABASE_PATH` | `data/stock_data.db` | SQLite database file path |
| `DATABASE_TYPE` | `sqlite` | Database type (sqlite/postgresql) |
| `REDIS_URL` | - | Redis connection URL |
| `REDIS_TTL` | `3600` | Redis cache TTL in seconds |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed frontend origins |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `json` | Log format (json/text) |
| `RATE_LIMIT_PER_MINUTE` | `60` | API rate limit per minute |
| `SECRET_KEY` | - | Application secret key |

### Frontend Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | `http://localhost:8000` | Backend API URL |
| `VITE_API_TIMEOUT` | `10000` | API request timeout (ms) |
| `VITE_APP_NAME` | `AI Stock Trading System` | Application name |
| `VITE_API_VERSION` | `v1` | API version to use |

### Database Configuration

**SQLite (Default)**
- ✅ **WAL Mode**: Enabled for better concurrent access
- ✅ **Optimized Settings**: Cache size, synchronous mode, foreign keys
- ⚠️ **Concurrency**: Limited to ~100 concurrent users
- 📝 **Note**: For production with high concurrency, consider PostgreSQL

**PostgreSQL (Production)**
```env
DATABASE_TYPE=postgresql
DB_URL=postgresql://username:password@localhost:5432/stock_trading
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_ECHO=false
```

**Redis Configuration**
```env
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=3600
REDIS_MAX_CONNECTIONS=10
```

## 🧪 Enhanced Testing

### Running Tests
```bash
# All tests with coverage
make test-coverage

# Specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests
pytest tests/performance/   # Performance tests

# With detailed coverage report
pytest --cov=backend/app --cov-report=html --cov-report=term-missing
```

### Test Structure
- **Unit Tests**: Individual component testing (90%+ coverage target)
- **Integration Tests**: API endpoint testing (100% coverage target)
- **E2E Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability and penetration testing

### Quality Gates
- **Code Coverage**: Minimum 80% overall, 90% for business logic
- **Performance**: API response time < 500ms (95th percentile)
- **Security**: No high/critical vulnerabilities
- **Reliability**: 99.9% uptime target

## 📊 Enhanced API Endpoints

### Core Endpoints (v1)

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `GET` | `/health` | System health check | None |
| `GET` | `/api/v1/config` | Client configuration | 10/min |
| `GET` | `/api/v1/stocks/{symbol}` | Stock quote data | 60/min |
| `POST` | `/api/v1/analysis/{symbol}` | AI stock analysis | 10/min |
| `GET` | `/api/v1/portfolio/summary` | Portfolio overview | 30/min |
| `POST` | `/api/v1/stocks/batch` | Multiple stock quotes | 20/min |
| `GET` | `/api/v1/metrics` | System metrics | Admin only |

### Example Usage

**Get Stock Quote with Error Handling**
```bash
curl -H "X-API-Version: v1" \
     -H "X-Correlation-ID: $(uuidgen)" \
     http://localhost:8000/api/v1/stocks/AAPL
```

**Request AI Analysis with Confidence Threshold**
```bash
curl -X POST http://localhost:8000/api/v1/analysis/AAPL \
  -H "Content-Type: application/json" \
  -H "X-API-Version: v1" \
  -d '{
    "analysis_type": "comprehensive",
    "confidence_threshold": 0.8,
    "include_technical": true,
    "include_fundamental": true
  }'
```

## 🔒 Enhanced Security & Compliance

### Security Features
- 🔐 **API Key Protection**: Backend-only secret management with rotation support
- 🛡️ **Input Validation**: Comprehensive request validation with sanitization
- 🚫 **Prompt Injection Prevention**: AI input sanitization and filtering
- 📝 **Audit Logging**: Complete activity tracking with correlation IDs
- 🔄 **Rate Limiting**: Advanced API protection with burst allowance
- 🌐 **CORS Security**: Production-ready CORS with origin validation
- 🔒 **Secrets Management**: Support for AWS Secrets Manager, Azure Key Vault

### Advanced Security Configuration
```env
# Security Settings
SECRET_KEY=your-256-bit-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Rate Limiting
RATE_LIMIT_STRATEGY=sliding_window
RATE_LIMIT_REDIS_URL=redis://localhost:6379/1

# CORS Security
CORS_ALLOW_CREDENTIALS=true
CORS_MAX_AGE=86400

# Input Validation
MAX_REQUEST_SIZE=1048576
ENABLE_REQUEST_LOGGING=true
SANITIZE_INPUTS=true
```

### Compliance Notes
- 📊 **Research Tool**: For analysis and educational purposes only
- 🚫 **Not Financial Advice**: All outputs are informational
- 📈 **No Trading Automation**: Does not execute trades
- ⚖️ **User Responsibility**: Users make their own investment decisions
- 🔍 **Data Privacy**: GDPR and CCPA compliance considerations
- 📋 **Audit Trail**: Complete request/response logging for compliance

### Data Sources & Disclaimers
- **Stock Data**: Yahoo Finance (delayed 15-20 minutes)
- **AI Analysis**: OpenAI GPT models (not real-time)
- **Market Hours**: Data freshness varies by trading session
- **Data Quality**: Automated validation and anomaly detection

## 🚀 Enhanced Deployment

### Development
```bash
# Using Make (Recommended)
make start  # Start both backend and frontend with hot reload

# With Redis caching
make start-with-redis

# Manual FastAPI Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Manual Frontend with API proxy
cd frontend  
pnpm run dev --host 0.0.0.0 --port 5173
```

### Production Deployment

**Option 1: Docker with Monitoring (Recommended)**
```bash
# Full production stack with monitoring
docker-compose -f docker-compose.prod.yml up -d

# With custom environment
docker-compose --env-file .env.prod up -d

# Health check
curl http://localhost:8000/health
```

**Option 2: Kubernetes Deployment**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=ai-stock-trading
```

**Option 3: Manual Production Setup**
```bash
# Backend with Gunicorn + Uvicorn workers
cd backend
pip install "gunicorn[standard]" uvicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
         --bind 0.0.0.0:8000 \
         --access-logfile - \
         --error-logfile - \
         app.main:app

# Frontend build and serve
cd frontend
pnpm run build
# Serve dist/ with nginx or similar
```

### Environment-Specific Recommendations

| Environment | Database | Caching | Deployment | Monitoring |
|-------------|----------|---------|------------|------------|
| **Development** | SQLite | In-memory | Local | Basic logging |
| **Staging** | PostgreSQL | Redis | Docker | Health checks + Metrics |
| **Production** | PostgreSQL | Redis Cluster | K8s/Docker | Full monitoring stack |

### Performance Optimization

**Backend Optimizations**
- Connection pooling for database
- Redis caching for API responses
- Async request handling
- Response compression
- CDN for static assets

**Frontend Optimizations**
- Code splitting and lazy loading
- Service worker for caching
- Image optimization
- Bundle size optimization
- Progressive Web App features

## 📊 Monitoring & Observability

### Metrics Collection
```bash
# Prometheus metrics endpoint
curl http://localhost:8000/metrics

# Custom business metrics
- stock_analysis_requests_total
- api_response_time_seconds
- cache_hit_ratio
- error_rate_by_endpoint
```

### Health Checks
```bash
# Comprehensive health check
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/health/db

# External services
curl http://localhost:8000/health/external
```

### Logging Structure
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "correlation_id": "req-123456",
  "service": "stock-analysis",
  "endpoint": "/api/v1/analysis/AAPL",
  "duration_ms": 245,
  "status_code": 200,
  "user_id": "user-789",
  "message": "Analysis completed successfully"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 and TypeScript best practices
- Write tests for new features (minimum 80% coverage)
- Update documentation for API changes
- Use conventional commit messages
- Run security scans before submitting PRs

### Code Quality Standards
- **Linting**: ESLint, Prettier, Black, isort
- **Type Checking**: mypy for Python, TypeScript strict mode
- **Security**: Bandit, Safety, npm audit
- **Performance**: Load testing for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Check the guides in the [`docs/`](docs/) directory
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussions**: Join GitHub Discussions for questions

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Yahoo Finance** for market data
- **FastAPI** and **React** communities
- **Redis Labs** for caching solutions
- All contributors and users of this project

---

**⚠️ Important Disclaimer**: This system is for research and educational purposes only. It does not provide financial advice and does not execute trades. Users are responsible for their own investment decisions. All data may be delayed or inaccurate. Past performance does not guarantee future results.

**🔒 Security Notice**: Always use environment variables for sensitive configuration. Never commit API keys or secrets to version control. Regularly update dependencies and monitor for security vulnerabilities.
