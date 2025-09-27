"""
FastAPI Backend Integration Tests
FastAPI 기반 백엔드 통합 테스트
"""

import pytest
import os
import sys
import tempfile
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

# 백엔드 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.main import app
from backend.app.settings import settings
from backend.app.database import init_db

# 테스트 환경 설정
os.environ['APP_ENV'] = 'testing'
os.environ['OPENAI_API_KEY'] = 'test_key'
os.environ['DATABASE_PATH'] = ':memory:'

@pytest.fixture
async def client():
    """FastAPI 테스트 클라이언트"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
async def setup_test_db():
    """테스트용 데이터베이스 설정"""
    await init_db()

class TestHealthEndpoint:
    """헬스 체크 엔드포인트 테스트"""
    
    async def test_health_check_success(self, client):
        """정상적인 헬스 체크"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert data["services"]["database"] == "connected"

    async def test_health_check_structure(self, client):
        """헬스 체크 응답 구조 검증"""
        response = await client.get("/health")
        data = response.json()
        
        required_fields = ["status", "timestamp", "version", "environment", "services"]
        for field in required_fields:
            assert field in data

class TestConfigEndpoint:
    """설정 엔드포인트 테스트"""
    
    async def test_get_config(self, client):
        """설정 정보 조회"""
        response = await client.get("/api/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "backend_url" in data
        assert "openai_model" in data
        assert "features" in data
        assert "version" in data

    async def test_config_features(self, client):
        """기능 플래그 확인"""
        response = await client.get("/api/config")
        data = response.json()
        
        features = data["features"]
        assert "ai_analysis" in features
        assert "database" in features
        assert "real_time_data" in features

class TestStockEndpoints:
    """주식 관련 엔드포인트 테스트"""
    
    async def test_get_stock_data(self, client):
        """주식 데이터 조회"""
        response = await client.get("/api/stocks/AAPL")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "price" in data
        assert "timestamp" in data
        assert "source" in data

    async def test_get_stock_data_lowercase(self, client):
        """소문자 심볼 처리"""
        response = await client.get("/api/stocks/aapl")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "AAPL"

    @patch('backend.app.main.openai_client')
    async def test_analyze_stock_success(self, mock_client, client):
        """성공적인 주식 분석"""
        # Mock OpenAI client
        mock_analysis = {
            "recommendation": "BUY",
            "confidence": 0.8,
            "target_price": 180.0,
            "key_factors": ["Strong earnings", "Market growth"],
            "risk_level": "MEDIUM",
            "time_horizon": "LONG"
        }
        
        mock_client.analyze_stock = AsyncMock(return_value=mock_analysis)
        
        response = await client.post("/api/analysis/AAPL")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["recommendation"] == "BUY"
        assert data["confidence"] == 0.8

    async def test_analyze_stock_without_openai(self, client):
        """OpenAI 클라이언트 없이 분석 시도"""
        with patch('backend.app.main.openai_client', None):
            response = await client.post("/api/analysis/AAPL")
            assert response.status_code == 503
            
            data = response.json()
            assert "not available" in data["detail"]

class TestPortfolioEndpoints:
    """포트폴리오 관련 엔드포인트 테스트"""
    
    async def test_get_portfolio_summary(self, client):
        """포트폴리오 요약 조회"""
        response = await client.get("/api/portfolio/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_value" in data
        assert "daily_change" in data
        assert "positions" in data
        assert "timestamp" in data

class TestErrorHandling:
    """에러 처리 테스트"""
    
    async def test_404_error(self, client):
        """404 에러 처리"""
        response = await client.get("/nonexistent")
        assert response.status_code == 404

    async def test_method_not_allowed(self, client):
        """허용되지 않은 메서드"""
        response = await client.post("/health")
        assert response.status_code == 405

class TestOpenAIClient:
    """OpenAI 클라이언트 테스트"""
    
    def test_client_initialization(self):
        """클라이언트 초기화 테스트"""
        from backend.app.openai_client import OpenAIClient
        
        client = OpenAIClient("test_key")
        assert client.api_key == "test_key"
        assert client.model == settings.OPENAI_MODEL

    def test_token_counting(self):
        """토큰 카운팅 테스트"""
        from backend.app.openai_client import OpenAIClient
        
        client = OpenAIClient("test_key")
        count = client.count_tokens("Hello world")
        assert count > 0
        assert isinstance(count, int)

    @patch('httpx.AsyncClient')
    async def test_chat_completion_success(self, mock_client):
        """성공적인 채팅 완성"""
        from backend.app.openai_client import OpenAIClient
        
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}, "finish_reason": "stop"}],
            "model": "gpt-4o-mini",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        client = OpenAIClient("test_key")
        messages = [{"role": "user", "content": "Hello"}]
        
        result = await client.chat_completion(messages)
        
        assert result["content"] == "Test response"
        assert result["usage"]["total_tokens"] == 15

class TestDatabase:
    """데이터베이스 테스트"""
    
    async def test_database_health_check(self):
        """데이터베이스 헬스 체크"""
        from backend.app.database import health_check_db
        
        result = await health_check_db()
        assert result is True

    async def test_database_session(self):
        """데이터베이스 세션 테스트"""
        from backend.app.database import get_db_session
        from sqlalchemy import text
        
        async with get_db_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

class TestSettings:
    """설정 테스트"""
    
    def test_settings_validation(self):
        """설정 유효성 검사"""
        assert settings.APP_ENV == "testing"
        assert settings.OPENAI_API_KEY == "test_key"
        assert settings.BACKEND_PORT == 8000

    def test_async_db_url(self):
        """비동기 DB URL 변환"""
        assert "sqlite+aiosqlite" in settings.async_db_url

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
