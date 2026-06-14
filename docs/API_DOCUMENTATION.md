# 🔌 API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required for development. In production, implement proper API key authentication.

## Core Endpoints

### 1. Health Check
**GET** `/health`

Check system health and service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-27T12:00:00.000000",
  "version": "1.1.0",
  "environment": "PROD",
  "services": {
    "database": "connected",
    "openai": "configured"
  }
}
```

**Status Codes:**
- `200`: System healthy
- `503`: System unhealthy

---

### 2. System Configuration
**GET** `/api/config`

Get client configuration and feature flags.

**Response:**
```json
{
  "backend_url": "http://localhost:8000",
  "openai_model": "gpt-4o-mini",
  "environment": "PROD",
  "features": {
    "ai_analysis": true,
    "database": true,
    "real_time_data": true
  },
  "version": "1.1.0"
}
```

---

### 3. Stock Quote
**GET** `/api/stocks/{symbol}`

Get current stock quote and basic information.

**Parameters:**
- `symbol` (path): Stock symbol (e.g., "AAPL", "GOOGL")

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "change": 2.35,
  "change_percent": 1.59,
  "volume": 1234567,
  "market_cap": "2.5T",
  "pe_ratio": 28.5,
  "dividend_yield": 0.52,
  "fifty_two_week_high": 198.23,
  "fifty_two_week_low": 124.17,
  "timestamp": "2025-09-27T12:00:00.000000",
  "source": "yahoo_finance"
}
```

**Status Codes:**
- `200`: Success
- `404`: Symbol not found
- `422`: Invalid symbol format
- `503`: Data source unavailable

---

### 4. AI Stock Analysis
**POST** `/api/analysis/{symbol}`

Get AI-powered analysis for a stock.

**Parameters:**
- `symbol` (path): Stock symbol

**Request Body:**
```json
{
  "analysis_type": "comprehensive",
  "include_technical": true,
  "include_fundamental": true,
  "time_horizon": "medium_term"
}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "analysis": {
    "summary": "Apple Inc. shows strong fundamentals...",
    "recommendation": "BUY",
    "confidence": 0.85,
    "price_target": 165.00,
    "risk_level": "MEDIUM"
  },
  "technical_indicators": {
    "rsi": 58.2,
    "macd": "bullish",
    "moving_averages": {
      "sma_20": 148.50,
      "sma_50": 145.20
    }
  },
  "fundamental_metrics": {
    "pe_ratio": 28.5,
    "peg_ratio": 1.2,
    "debt_to_equity": 1.73
  },
  "timestamp": "2025-09-27T12:00:00.000000",
  "model_used": "gpt-4o-mini"
}
```

---

### 5. Portfolio Summary
**GET** `/api/portfolio/summary`

Get portfolio overview and performance metrics.

**Response:**
```json
{
  "total_value": 125000.00,
  "total_gain_loss": 8500.00,
  "total_gain_loss_percent": 7.29,
  "positions": [
    {
      "symbol": "AAPL",
      "shares": 100,
      "current_price": 150.25,
      "market_value": 15025.00,
      "gain_loss": 1025.00,
      "gain_loss_percent": 7.32
    }
  ],
  "cash_balance": 5000.00,
  "last_updated": "2025-09-27T12:00:00.000000"
}
```

---

### 6. Multiple Stock Quotes
**POST** `/api/stocks/batch`

Get quotes for multiple stocks in a single request.

**Request Body:**
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"],
  "include_details": true
}
```

**Response:**
```json
{
  "quotes": {
    "AAPL": {
      "symbol": "AAPL",
      "price": 150.25,
      "change": 2.35,
      "change_percent": 1.59,
      "timestamp": "2025-09-27T12:00:00.000000"
    },
    "GOOGL": {
      "symbol": "GOOGL",
      "price": 2750.80,
      "change": -15.20,
      "change_percent": -0.55,
      "timestamp": "2025-09-27T12:00:00.000000"
    }
  },
  "failed_symbols": [],
  "total_requested": 4,
  "total_successful": 4
}
```

## Error Responses

All endpoints return structured error responses:

```json
{
  "detail": {
    "error": "Symbol not found",
    "code": "SYMBOL_NOT_FOUND",
    "timestamp": "2025-09-27T12:00:00.000000",
    "request_id": "req_123456789"
  }
}
```

## Rate Limiting

- **Development**: No rate limiting
- **Production**: 100 requests per minute per IP

## Data Sources & Disclaimers

- **Stock Data**: Yahoo Finance (delayed 15-20 minutes)
- **AI Analysis**: OpenAI GPT models
- **Market Hours**: Data freshness varies based on market status

⚠️ **Important**: This system is for research and analysis purposes only. Not financial advice.

## Example Usage

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Get stock quote
curl http://localhost:8000/api/stocks/AAPL

# Get AI analysis
curl -X POST http://localhost:8000/api/analysis/AAPL \
  -H "Content-Type: application/json" \
  -d '{"analysis_type": "comprehensive"}'

# Batch quotes
curl -X POST http://localhost:8000/api/stocks/batch \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL"]}'
```

### JavaScript/TypeScript Examples

```typescript
// Using fetch API
const response = await fetch('http://localhost:8000/api/stocks/AAPL');
const quote = await response.json();

// Using axios
import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
});

const quote = await client.get('/api/stocks/AAPL');
const analysis = await client.post('/api/analysis/AAPL', {
  analysis_type: 'comprehensive'
});
```

## WebSocket Endpoints (Future)

Real-time data streaming will be available via WebSocket:

```
ws://localhost:8000/ws/quotes/{symbol}
ws://localhost:8000/ws/portfolio
```
