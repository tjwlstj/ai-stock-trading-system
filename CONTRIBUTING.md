# 🤝 Contributing to AI Stock Trading System

Thank you for your interest in contributing to the AI Stock Trading System! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Community](#community)

## 📜 Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and help them get started
- **Be collaborative**: Work together to improve the project
- **Be constructive**: Provide helpful feedback and suggestions
- **Be professional**: Maintain a professional tone in all interactions

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** installed
- **Node.js 20+** (LTS version)
- **Git** for version control
- **Docker** (optional, for containerized development)
- **OpenAI API Key** for testing AI features

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-stock-trading-system.git
   cd ai-stock-trading-system
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/tjwlstj/ai-stock-trading-system.git
   ```

## 🛠️ Development Setup

### Environment Configuration

1. **Copy environment files**:
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env.local
   ```

2. **Configure environment variables**:
   ```env
   # .env
   OPENAI_API_KEY=sk-your-test-key-here
   OPENAI_MODEL=gpt-4o-mini
   LOG_LEVEL=DEBUG
   ```

3. **Install dependencies**:
   ```bash
   # Using Make (recommended)
   make setup
   
   # Or manually
   cd backend && pip install -r requirements.txt
   cd ../frontend && pnpm install
   ```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Start development servers**:
   ```bash
   make start
   # Or manually:
   # Terminal 1: cd backend && python -m uvicorn app.main:app --reload
   # Terminal 2: cd frontend && pnpm run dev
   ```

3. **Make your changes** and test thoroughly

4. **Run tests**:
   ```bash
   make test
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug fixes**: Fix issues and improve stability
- ✨ **New features**: Add functionality that benefits users
- 📚 **Documentation**: Improve guides, API docs, and examples
- 🧪 **Tests**: Add or improve test coverage
- 🎨 **UI/UX**: Enhance user interface and experience
- ⚡ **Performance**: Optimize code and improve efficiency
- 🔒 **Security**: Address security vulnerabilities
- 🌐 **Internationalization**: Add language support

### What We're Looking For

**High Priority:**
- AI analysis improvements and new models
- Frontend UI/UX enhancements
- Performance optimizations
- Security improvements
- Test coverage expansion
- Documentation improvements

**Medium Priority:**
- New data sources integration
- Additional chart types and visualizations
- Mobile responsiveness improvements
- Accessibility enhancements

**Low Priority:**
- Code refactoring (unless it improves performance/readability significantly)
- Minor style changes
- Non-essential feature additions

## 🔄 Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Rebase your feature branch**:
   ```bash
   git checkout feature/your-feature-name
   git rebase main
   ```

3. **Run the full test suite**:
   ```bash
   make test
   pytest --cov=backend/app --cov-report=term-missing
   ```

4. **Check code quality**:
   ```bash
   # Python
   black backend/
   flake8 backend/
   mypy backend/
   
   # Frontend
   cd frontend
   pnpm run lint
   pnpm run type-check
   ```

### Pull Request Template

When creating a pull request, please include:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Testing** in development environment
4. **Documentation** review if applicable
5. **Approval** and merge by maintainer

## 🎯 Coding Standards

### Python (Backend)

**Style Guide:**
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **type hints** for all functions
- Maximum line length: **88 characters**

**Code Quality:**
```python
# Good: Type hints and docstrings
async def get_stock_quote(symbol: str) -> StockQuote:
    """
    Fetch stock quote for the given symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        
    Returns:
        StockQuote object with current market data
        
    Raises:
        ValueError: If symbol format is invalid
        HTTPException: If data source is unavailable
    """
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        raise ValueError(f"Invalid symbol format: {symbol}")
    
    # Implementation here
    pass

# Bad: No type hints or documentation
def get_quote(s):
    return some_function(s)
```

**Error Handling:**
```python
# Good: Specific exception handling
try:
    response = await http_client.get(url)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    logger.error(f"HTTP error {e.response.status_code}: {e}")
    raise HTTPException(status_code=503, detail="Data source unavailable")
except httpx.RequestError as e:
    logger.error(f"Request error: {e}")
    raise HTTPException(status_code=503, detail="Network error")

# Bad: Generic exception handling
try:
    response = requests.get(url)
except Exception as e:
    print(f"Error: {e}")
    return None
```

### TypeScript/React (Frontend)

**Style Guide:**
- Use **TypeScript** for all new code
- Follow **React best practices**
- Use **functional components** with hooks
- Use **Tailwind CSS** for styling

**Component Structure:**
```tsx
// Good: Proper TypeScript interface and component structure
interface StockQuoteProps {
  symbol: string
  onAnalyze?: (symbol: string) => void
  className?: string
}

export function StockQuote({ symbol, onAnalyze, className }: StockQuoteProps) {
  const [quote, setQuote] = useState<StockQuote | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Implementation here
  
  return (
    <div className={cn("p-4 border rounded-lg", className)}>
      {/* Component JSX */}
    </div>
  )
}

// Bad: No TypeScript, unclear props
function StockQuote(props) {
  // Implementation without types
}
```

### Database

**Migration Guidelines:**
- Always create **reversible migrations**
- Test migrations on **sample data**
- Document **breaking changes**
- Use **descriptive migration names**

```python
# Good: Clear migration with proper naming
"""Add user_preferences table

Revision ID: 001_add_user_preferences
Revises: 000_initial_schema
Create Date: 2025-09-27 12:00:00.000000
"""

def upgrade():
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('theme', sa.String(20), default='light'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('user_preferences')
```

## 🧪 Testing Requirements

### Test Coverage

- **Minimum coverage**: 80% overall
- **Critical paths**: 95% coverage required
- **New features**: Must include comprehensive tests

### Test Types

**Unit Tests:**
```python
# test_stock_validator.py
import pytest
from backend.app.utils.symbol_validator import SymbolValidator

class TestSymbolValidator:
    def test_valid_symbol(self):
        assert SymbolValidator.validate("AAPL") == "AAPL"
        assert SymbolValidator.validate("googl") == "GOOGL"
    
    def test_invalid_symbol(self):
        with pytest.raises(ValueError):
            SymbolValidator.validate("INVALID123")
        
        with pytest.raises(ValueError):
            SymbolValidator.validate("")
```

**Integration Tests:**
```python
# test_api_integration.py
@pytest.mark.asyncio
async def test_stock_quote_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/stocks/AAPL")
        
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "price" in data
    assert isinstance(data["price"], (int, float))
```

**Frontend Tests:**
```tsx
// StockQuote.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { StockQuote } from './StockQuote'

describe('StockQuote', () => {
  it('displays stock information correctly', async () => {
    render(<StockQuote symbol="AAPL" />)
    
    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument()
      expect(screen.getByText(/\$\d+\.\d+/)).toBeInTheDocument()
    })
  })
})
```

## 📚 Documentation

### Code Documentation

- **Docstrings**: All public functions must have docstrings
- **Type hints**: Required for all Python functions
- **Comments**: Explain complex logic and business rules
- **README updates**: Update relevant documentation

### API Documentation

- **OpenAPI/Swagger**: Automatically generated from FastAPI
- **Examples**: Include request/response examples
- **Error codes**: Document all possible error responses

```python
@app.post("/api/analysis/{symbol}", response_model=AnalysisResponse)
async def analyze_stock(
    symbol: str = Path(..., description="Stock symbol (e.g., 'AAPL')"),
    request: AnalysisRequest = Body(..., description="Analysis parameters")
) -> AnalysisResponse:
    """
    Generate AI-powered stock analysis.
    
    This endpoint provides comprehensive stock analysis using multiple AI models
    and data sources to generate investment recommendations.
    
    - **symbol**: Valid stock symbol (1-5 uppercase letters)
    - **analysis_type**: Type of analysis to perform
    - **include_technical**: Whether to include technical indicators
    
    Returns detailed analysis with recommendation, confidence score, and rationale.
    """
    # Implementation here
```

## 🌟 Recognition

### Contributors

We recognize contributors in several ways:

- **GitHub Contributors**: Automatic recognition in repository
- **Changelog**: Major contributions mentioned in releases
- **Documentation**: Contributors listed in project documentation
- **Special Recognition**: Outstanding contributions highlighted

### Contribution Levels

- **🥉 Bronze**: 1-5 merged PRs
- **🥈 Silver**: 6-15 merged PRs or significant feature contribution
- **🥇 Gold**: 16+ merged PRs or major architectural contribution
- **💎 Diamond**: Long-term maintainer or exceptional contribution

## 💬 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community chat
- **Pull Requests**: Code review and technical discussions

### Getting Help

- **Documentation**: Check existing guides and API docs
- **Search Issues**: Look for similar problems or questions
- **Ask Questions**: Create a GitHub Discussion for help
- **Join Community**: Participate in code reviews and discussions

### Mentorship

New contributors can get help from experienced maintainers:

- **Good First Issues**: Labeled issues perfect for newcomers
- **Mentorship**: Maintainers available to guide new contributors
- **Pair Programming**: Available for complex features (by arrangement)

## 🎉 Thank You!

Every contribution, no matter how small, helps make this project better. We appreciate:

- 🐛 Bug reports and fixes
- 💡 Feature suggestions and implementations
- 📝 Documentation improvements
- 🧪 Test additions and improvements
- 💬 Community participation and support

**Happy coding!** 🚀
