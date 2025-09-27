# 🧪 Testing Guide

## Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_collectors.py
├── integration/            # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_openai.py
├── e2e/                   # End-to-end tests
│   └── test_workflows.py
└── conftest.py            # Pytest configuration
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
make test

# Or manually
./scripts/run_tests.sh

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # E2E tests only
```

### Detailed Test Commands

```bash
# Run with coverage
pytest --cov=backend/app --cov-report=html

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/integration/test_api.py

# Run specific test function
pytest tests/integration/test_api.py::test_health_endpoint

# Run tests matching pattern
pytest -k "test_stock"
```

## Test Categories

### 1. Unit Tests

Test individual components in isolation.

**Example: Testing Stock Quote Model**
```python
# tests/unit/test_models.py
import pytest
from datetime import datetime
from backend.app.collectors.yahoo_finance import StockQuote

def test_stock_quote_creation():
    quote = StockQuote(
        symbol="AAPL",
        price=150.25,
        change=2.35,
        change_percent=1.59,
        volume=1234567,
        timestamp=datetime.now()
    )
    
    assert quote.symbol == "AAPL"
    assert quote.price == 150.25
    assert quote.change_percent == 1.59

def test_stock_quote_to_dict():
    quote = StockQuote(
        symbol="AAPL",
        price=150.25,
        change=2.35,
        change_percent=1.59,
        volume=1234567
    )
    
    data = quote.to_dict()
    assert isinstance(data, dict)
    assert data["symbol"] == "AAPL"
    assert data["price"] == 150.25
```

### 2. Integration Tests

Test component interactions and API endpoints.

**Example: Testing API Endpoints**
```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

@pytest.mark.asyncio
async def test_stock_quote_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/stocks/AAPL")
        
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "price" in data
    assert "timestamp" in data

@pytest.mark.asyncio
async def test_invalid_symbol():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/stocks/INVALID123")
        
    assert response.status_code == 422
```

### 3. End-to-End Tests

Test complete user workflows.

**Example: Complete Analysis Workflow**
```python
# tests/e2e/test_workflows.py
import pytest
from httpx import AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_complete_analysis_workflow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Check system health
        health_response = await client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Get stock quote
        quote_response = await client.get("/api/stocks/AAPL")
        assert quote_response.status_code == 200
        quote_data = quote_response.json()
        
        # 3. Request AI analysis
        analysis_response = await client.post(
            "/api/analysis/AAPL",
            json={"analysis_type": "comprehensive"}
        )
        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()
        
        # 4. Verify analysis contains expected fields
        assert analysis_data["symbol"] == "AAPL"
        assert "analysis" in analysis_data
        assert "recommendation" in analysis_data["analysis"]
```

## Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests (skip in CI)
```

### conftest.py
```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from backend.app.main import app
from backend.app.database import init_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Set up test database."""
    await init_db()

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [{
            "message": {
                "content": "This is a test analysis for AAPL stock."
            }
        }]
    }
```

## Mocking External Services

### Mock Yahoo Finance API
```python
# tests/unit/test_collectors.py
import pytest
from unittest.mock import AsyncMock, patch
from backend.app.collectors.yahoo_finance import YahooFinanceCollector

@pytest.mark.asyncio
async def test_yahoo_finance_collector_success():
    collector = YahooFinanceCollector()
    
    mock_response = {
        "chart": {
            "result": [{
                "meta": {
                    "regularMarketPrice": 150.25,
                    "previousClose": 147.90,
                    "regularMarketVolume": 1234567
                }
            }]
        }
    }
    
    with patch.object(collector, '_fetch_quote_data', return_value=mock_response):
        quote = await collector.get_quote("AAPL")
        
    assert quote.symbol == "AAPL"
    assert quote.price == 150.25
    assert quote.volume == 1234567

@pytest.mark.asyncio
async def test_yahoo_finance_collector_error():
    collector = YahooFinanceCollector()
    
    with patch.object(collector, '_fetch_quote_data', side_effect=Exception("API Error")):
        with pytest.raises(ValueError):
            await collector.get_quote("AAPL")
```

### Mock OpenAI API
```python
# tests/unit/test_openai.py
import pytest
from unittest.mock import AsyncMock, patch
from backend.app.openai_client import OpenAIClient

@pytest.mark.asyncio
async def test_openai_analysis():
    client = OpenAIClient("test-key")
    
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.content = "Test analysis result"
    
    with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
        result = await client.analyze_stock("AAPL", {"price": 150.25})
        
    assert "Test analysis result" in result
```

## Performance Testing

### Load Testing with pytest-benchmark
```python
# tests/performance/test_load.py
import pytest
from backend.app.collectors.yahoo_finance import YahooFinanceCollector

def test_quote_performance(benchmark):
    collector = YahooFinanceCollector()
    
    # Benchmark the quote fetching
    result = benchmark(collector.get_quote, "AAPL")
    assert result.symbol == "AAPL"

@pytest.mark.asyncio
async def test_concurrent_quotes():
    collector = YahooFinanceCollector()
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    
    import time
    start_time = time.time()
    
    quotes = await collector.get_multiple_quotes(symbols)
    
    end_time = time.time()
    duration = end_time - start_time
    
    assert len(quotes) == len(symbols)
    assert duration < 5.0  # Should complete within 5 seconds
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=backend/app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Data Management

### Fixtures for Test Data
```python
# tests/fixtures/stock_data.py
SAMPLE_QUOTES = {
    "AAPL": {
        "symbol": "AAPL",
        "price": 150.25,
        "change": 2.35,
        "change_percent": 1.59,
        "volume": 1234567
    },
    "GOOGL": {
        "symbol": "GOOGL",
        "price": 2750.80,
        "change": -15.20,
        "change_percent": -0.55,
        "volume": 987654
    }
}

SAMPLE_ANALYSIS = {
    "AAPL": {
        "summary": "Apple Inc. shows strong fundamentals...",
        "recommendation": "BUY",
        "confidence": 0.85,
        "price_target": 165.00
    }
}
```

## Coverage Requirements

Maintain minimum test coverage:
- **Unit Tests**: 90%+
- **Integration Tests**: 80%+
- **Overall Coverage**: 85%+

### Generate Coverage Report
```bash
# HTML report
pytest --cov=backend/app --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=backend/app --cov-report=term-missing

# XML report (for CI)
pytest --cov=backend/app --cov-report=xml
```

## Best Practices

### 1. Test Naming
```python
# Good: Descriptive test names
def test_stock_quote_returns_valid_data_for_existing_symbol():
    pass

def test_stock_quote_raises_error_for_invalid_symbol():
    pass

# Bad: Vague test names
def test_quote():
    pass

def test_error():
    pass
```

### 2. Test Organization
- One test file per module
- Group related tests in classes
- Use descriptive docstrings
- Keep tests independent

### 3. Assertions
```python
# Good: Specific assertions
assert response.status_code == 200
assert "AAPL" in response.json()["symbol"]
assert response.json()["price"] > 0

# Bad: Generic assertions
assert response
assert response.json()
```

### 4. Test Data
- Use fixtures for reusable test data
- Keep test data minimal and focused
- Use factories for complex objects
- Mock external dependencies

## Debugging Tests

### Running Tests in Debug Mode
```bash
# Run with pdb on failure
pytest --pdb

# Run with verbose output
pytest -v -s

# Run single test with debugging
pytest tests/integration/test_api.py::test_health_endpoint -v -s --pdb
```

### VS Code Test Configuration
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.autoTestDiscoverOnSaveEnabled": true
}
```
