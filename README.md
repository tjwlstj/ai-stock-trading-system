# 🤖 AI Stock Trading System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-red.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **⚠️ Research & Educational Tool Only**  
> This system is designed for market analysis and educational purposes. It does NOT execute trades or provide financial advice.

A sophisticated AI-powered stock analysis system that combines multiple data sources with advanced language models to provide comprehensive market insights and research capabilities.

## ✨ Features

### 🧠 **Multi-Agent AI Analysis**
- **GPT-4o Mini Integration**: Advanced natural language processing for market analysis
- **Consensus-Based Decisions**: Multiple AI agents provide weighted recommendations
- **Technical & Fundamental Analysis**: Comprehensive evaluation of market conditions
- **Risk Assessment**: Intelligent risk profiling and scenario analysis

### 📊 **Real-Time Market Data**
- **Near Real-Time Quotes**: Yahoo Finance integration with smart caching (15-20 min delay)
- **Market Hours Awareness**: Intelligent data freshness based on trading sessions
- **Multi-Exchange Support**: US, UK, Japan, Hong Kong, and Chinese markets
- **Fallback Mechanisms**: Robust error handling and data source redundancy

### 🏗️ **Production-Ready Architecture**
- **FastAPI Backend**: High-performance async API with automatic documentation
- **React Frontend**: Modern, responsive user interface with real-time updates
- **SQLite with WAL Mode**: Optimized database with concurrent access support
- **Docker Support**: Containerized deployment with docker-compose

### 🔒 **Enterprise Security**
- **Environment-Based Configuration**: Secure API key management
- **Input Validation**: Comprehensive request/response validation with Pydantic
- **Rate Limiting**: API protection against abuse
- **Audit Logging**: Complete activity tracking for compliance

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (recommended: 3.11 or 3.12)
- **Node.js 20+** (LTS version recommended)
- **pnpm** (package manager)

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
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
OPENAI_MAX_RETRY=5

# Backend Configuration
BACKEND_PORT=8000
CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173

# Frontend Configuration (in frontend/.env.local)
VITE_API_BASE=http://localhost:8000
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

**Option C: Docker**
```bash
docker-compose up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Documentation

### Core Guides
- 📋 **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference with examples
- 🗄️ **[Database Guide](DATABASE_GUIDE.md)** - SQLite optimization & PostgreSQL migration
- 🧪 **[Testing Guide](TESTING_GUIDE.md)** - Comprehensive testing strategies
- 🔒 **[Security Guide](SECURITY_GUIDE.md)** - Security best practices & compliance
- 🎨 **[Frontend Guide](FRONTEND_GUIDE.md)** - UI/UX patterns & React best practices

### Quick References
- 🔧 **Configuration**: Environment variables and settings
- 🐳 **Docker**: Containerized deployment options
- 📊 **Monitoring**: Health checks and performance metrics
- 🚨 **Troubleshooting**: Common issues and solutions

## 🏛️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  External APIs  │
│                 │    │                 │    │                 │
│ • Dashboard     │◄──►│ • Stock Data    │◄──►│ • Yahoo Finance │
│ • Analysis UI   │    │ • AI Analysis   │    │ • OpenAI GPT    │
│ • Portfolio     │    │ • Portfolio Mgmt│    │ • Market Data   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  SQLite Database │
                       │                 │
                       │ • Stock Quotes  │
                       │ • Analysis Data │
                       │ • User Portfolio│
                       └─────────────────┘
```

### Technology Stack

**Backend**
- **FastAPI**: Modern Python web framework with automatic API documentation
- **SQLAlchemy**: Async ORM with SQLite (WAL mode) and PostgreSQL support
- **Pydantic**: Data validation and serialization
- **OpenAI**: GPT-4o Mini for AI analysis
- **httpx**: Async HTTP client for external APIs
- **Tenacity**: Retry logic and circuit breakers

**Frontend**
- **React 18**: Modern UI library with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Responsive chart library

**Infrastructure**
- **Docker**: Containerization and deployment
- **SQLite**: Default database with WAL mode optimization
- **PostgreSQL**: Production database option
- **GitHub Actions**: CI/CD pipeline (optional)

## 🔧 Configuration Reference

### Backend Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | **Required**: OpenAI API key for AI analysis |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model for analysis |
| `OPENAI_TIMEOUT` | `30` | API timeout in seconds |
| `OPENAI_MAX_RETRY` | `5` | Maximum retry attempts |
| `BACKEND_PORT` | `8000` | Backend server port |
| `DATABASE_PATH` | `data/stock_data.db` | SQLite database file path |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed frontend origins |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Frontend Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | `http://localhost:8000` | Backend API URL |
| `VITE_API_TIMEOUT` | `10000` | API request timeout (ms) |
| `VITE_APP_NAME` | `AI Stock Trading System` | Application name |

### Database Configuration

**SQLite (Default)**
- ✅ **WAL Mode**: Enabled for better concurrent access
- ✅ **Optimized Settings**: Cache size, synchronous mode, foreign keys
- ⚠️ **Concurrency**: Limited to ~100 concurrent users
- 📝 **Note**: For production with high concurrency, consider PostgreSQL

**PostgreSQL (Production)**
```env
DB_URL=postgresql://username:password@localhost:5432/stock_trading
DATABASE_TYPE=postgresql
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

## 🧪 Testing

### Running Tests
```bash
# All tests
make test

# Specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests

# With coverage
pytest --cov=backend/app --cov-report=html
```

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/api/config` | Client configuration |
| `GET` | `/api/stocks/{symbol}` | Stock quote data |
| `POST` | `/api/analysis/{symbol}` | AI stock analysis |
| `GET` | `/api/portfolio/summary` | Portfolio overview |
| `POST` | `/api/stocks/batch` | Multiple stock quotes |

### Example Usage

**Get Stock Quote**
```bash
curl http://localhost:8000/api/stocks/AAPL
```

**Request AI Analysis**
```bash
curl -X POST http://localhost:8000/api/analysis/AAPL \
  -H "Content-Type: application/json" \
  -d '{"analysis_type": "comprehensive"}'
```

## 🔒 Security & Compliance

### Security Features
- 🔐 **API Key Protection**: Backend-only secret management
- 🛡️ **Input Validation**: Comprehensive request validation
- 🚫 **Prompt Injection Prevention**: AI input sanitization
- 📝 **Audit Logging**: Complete activity tracking
- 🔄 **Rate Limiting**: API abuse protection

### Compliance Notes
- 📊 **Research Tool**: For analysis and educational purposes only
- 🚫 **Not Financial Advice**: All outputs are informational
- 📈 **No Trading Automation**: Does not execute trades
- ⚖️ **User Responsibility**: Users make their own investment decisions

### Data Sources & Disclaimers
- **Stock Data**: Yahoo Finance (delayed 15-20 minutes)
- **AI Analysis**: OpenAI GPT models (not real-time)
- **Market Hours**: Data freshness varies by trading session

## 🚀 Deployment

### Development
```bash
make start  # Local development servers
```

### Production with Docker
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# With custom environment
docker-compose --env-file .env.prod up -d
```

### Environment-Specific Recommendations

| Environment | Database | Deployment | Monitoring |
|-------------|----------|------------|------------|
| **Development** | SQLite | Local | Basic logging |
| **Staging** | SQLite/PostgreSQL | Docker | Health checks |
| **Production** | PostgreSQL | Docker + Load Balancer | Full monitoring |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 and TypeScript best practices
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Check the guides in the `/docs` directory
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussions**: Join GitHub Discussions for questions
- 📧 **Contact**: For enterprise support, contact the maintainers

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Yahoo Finance** for market data
- **FastAPI** and **React** communities
- All contributors and users of this project

---

**⚠️ Important Disclaimer**: This system is for research and educational purposes only. It does not provide financial advice and does not execute trades. Users are responsible for their own investment decisions. All data may be delayed or inaccurate.
