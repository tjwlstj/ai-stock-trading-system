"""
Backend Integration Tests
백엔드 통합 테스트
"""

import pytest
import os
import sys
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock

# 백엔드 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import app
from backend.database import DatabaseManager
from backend.openai_wrapper import OpenAIWrapper

@pytest.fixture
def client():
    """Flask 테스트 클라이언트"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def temp_db():
    """임시 데이터베이스"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # 환경변수 설정
    os.environ['DATABASE_PATH'] = db_path
    
    yield db_path
    
    # 정리
    try:
        os.unlink(db_path)
        os.unlink(f"{db_path}-wal")
        os.unlink(f"{db_path}-shm")
    except FileNotFoundError:
        pass

class TestHealthEndpoint:
    """헬스 체크 엔드포인트 테스트"""
    
    def test_health_check_success(self, client, temp_db):
        """정상적인 헬스 체크"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['database'] == 'connected'

    def test_health_check_with_missing_db(self, client):
        """데이터베이스 없을 때 헬스 체크"""
        os.environ['DATABASE_PATH'] = '/nonexistent/path.db'
        
        response = client.get('/health')
        assert response.status_code == 500
        
        data = response.get_json()
        assert data['status'] == 'unhealthy'

class TestConfigEndpoint:
    """설정 엔드포인트 테스트"""
    
    def test_get_config(self, client):
        """설정 정보 조회"""
        response = client.get('/api/config')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'backend_url' in data
        assert 'openai_model' in data
        assert 'features' in data

class TestStockEndpoints:
    """주식 관련 엔드포인트 테스트"""
    
    def test_get_stock_data(self, client):
        """주식 데이터 조회"""
        response = client.get('/api/stocks/AAPL')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['symbol'] == 'AAPL'
        assert 'price' in data
        assert 'timestamp' in data

    def test_get_stock_data_invalid_symbol(self, client):
        """잘못된 심볼로 주식 데이터 조회"""
        response = client.get('/api/stocks/INVALID123')
        # 현재는 모든 심볼을 허용하므로 200 반환
        assert response.status_code == 200

    @patch('backend.main.os.getenv')
    def test_analyze_stock_without_api_key(self, mock_getenv, client):
        """API 키 없이 주식 분석"""
        mock_getenv.return_value = None
        
        response = client.post('/api/analysis/AAPL')
        assert response.status_code == 503
        
        data = response.get_json()
        assert 'OpenAI API key not configured' in data['error']

    def test_analyze_stock_with_api_key(self, client):
        """API 키 있을 때 주식 분석"""
        os.environ['OPENAI_API_KEY'] = 'test_key'
        
        response = client.post('/api/analysis/AAPL')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['symbol'] == 'AAPL'
        assert 'recommendation' in data
        assert 'confidence' in data

class TestDatabaseManager:
    """데이터베이스 매니저 테스트"""
    
    def test_database_connection(self, temp_db):
        """데이터베이스 연결 테스트"""
        db_manager = DatabaseManager(temp_db)
        
        with db_manager.get_connection() as conn:
            # WAL 모드 확인
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            result = cursor.fetchone()
            assert result[0].upper() == 'WAL'

    def test_database_query_execution(self, temp_db):
        """데이터베이스 쿼리 실행 테스트"""
        db_manager = DatabaseManager(temp_db)
        
        # 테스트 테이블 생성
        with db_manager.get_connection() as conn:
            conn.execute('''
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')
            conn.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
            conn.commit()
        
        # 쿼리 실행 테스트
        results = db_manager.execute_query("SELECT * FROM test_table")
        assert len(results) == 1
        assert results[0]['name'] == 'test'

class TestOpenAIWrapper:
    """OpenAI 래퍼 테스트"""
    
    def test_wrapper_initialization_without_key(self):
        """API 키 없이 초기화"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not found"):
                OpenAIWrapper()

    def test_wrapper_initialization_with_key(self):
        """API 키로 초기화"""
        wrapper = OpenAIWrapper(api_key="test_key")
        assert wrapper.api_key == "test_key"
        assert wrapper.model == "gpt-4o-mini"  # 기본값

    def test_token_counting(self):
        """토큰 카운팅 테스트"""
        wrapper = OpenAIWrapper(api_key="test_key")
        
        # 간단한 텍스트
        count = wrapper.count_tokens("Hello world")
        assert count > 0
        assert isinstance(count, int)

    def test_input_validation(self):
        """입력 유효성 검사"""
        wrapper = OpenAIWrapper(api_key="test_key")
        
        # 짧은 메시지
        short_messages = [{"role": "user", "content": "Hello"}]
        assert wrapper.validate_input(short_messages) == True
        
        # 긴 메시지
        long_content = "x" * 10000
        long_messages = [{"role": "user", "content": long_content}]
        assert wrapper.validate_input(long_messages, max_tokens=100) == False

    @patch('backend.openai_wrapper.OpenAI')
    def test_chat_completion_success(self, mock_openai):
        """성공적인 채팅 완성"""
        # Mock 설정
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.choices[0].finish_reason = "stop"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 테스트 실행
        wrapper = OpenAIWrapper(api_key="test_key")
        messages = [{"role": "user", "content": "Hello"}]
        
        result = wrapper.chat_completion_with_retry(messages)
        
        assert result is not None
        assert result['content'] == "Test response"
        assert result['usage']['total_tokens'] == 15

    @patch('backend.openai_wrapper.OpenAI')
    def test_chat_completion_retry_on_failure(self, mock_openai):
        """실패 시 재시도 테스트"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            Exception("rate_limit"),  # 첫 번째 시도 실패
            Exception("timeout"),     # 두 번째 시도 실패
            Exception("unknown")      # 세 번째 시도 실패
        ]
        mock_openai.return_value = mock_client
        
        wrapper = OpenAIWrapper(api_key="test_key")
        wrapper.max_retries = 3
        wrapper.base_delay = 0.1  # 테스트 속도 향상
        
        messages = [{"role": "user", "content": "Hello"}]
        result = wrapper.chat_completion_with_retry(messages)
        
        assert result is None
        assert mock_client.chat.completions.create.call_count == 3

class TestErrorHandling:
    """에러 처리 테스트"""
    
    def test_404_error(self, client):
        """404 에러 처리"""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """허용되지 않은 메서드"""
        response = client.post('/health')
        assert response.status_code == 405

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
