"""
AI Stock Trading System - Backend Main Server
Flask 기반 백엔드 API 서버
"""

import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from datetime import datetime
import sqlite3
import traceback

# 환경변수 로드 (루트 디렉토리와 백엔드 디렉토리 모두 확인)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 앱 생성
app = Flask(__name__)

# CORS 설정
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
CORS(app, origins=cors_origins)

# 환경변수 검증
required_env_vars = ['OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.warning(f"Missing environment variables: {missing_vars}")

@app.errorhandler(Exception)
def handle_exception(e):
    """전역 예외 처리"""
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'error': 'Internal server error',
        'message': str(e) if app.debug else 'An unexpected error occurred'
    }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    try:
        # 데이터베이스 연결 테스트
        db_path = os.getenv('DATABASE_PATH', 'data/stock_data.db')
        with sqlite3.connect(db_path) as conn:
            conn.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'environment': {
                'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
                'cors_origins': cors_origins
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """클라이언트용 설정 정보 반환 (민감한 정보 제외)"""
    return jsonify({
        'backend_url': os.getenv('BACKEND_URL', 'http://localhost:8000'),
        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        'features': {
            'ai_analysis': bool(os.getenv('OPENAI_API_KEY')),
            'cloud_storage': bool(os.getenv('AWS_ACCESS_KEY_ID')),
            'redis_cache': bool(os.getenv('REDIS_URL'))
        }
    })

@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """주식 데이터 조회"""
    try:
        # 여기에 실제 주식 데이터 조회 로직 구현
        # 현재는 예시 응답
        return jsonify({
            'symbol': symbol.upper(),
            'price': 150.25,
            'change': 2.35,
            'change_percent': 1.59,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        return jsonify({'error': f'Failed to fetch data for {symbol}'}), 500

@app.route('/api/analysis/<symbol>', methods=['POST'])
def analyze_stock(symbol):
    """AI 주식 분석"""
    try:
        if not os.getenv('OPENAI_API_KEY'):
            return jsonify({'error': 'OpenAI API key not configured'}), 503
        
        # 여기에 실제 AI 분석 로직 구현
        # 현재는 예시 응답
        return jsonify({
            'symbol': symbol.upper(),
            'recommendation': 'BUY',
            'confidence': 0.75,
            'target_price': 165.00,
            'analysis': {
                'optimistic': {'score': 0.8, 'reasoning': 'Strong growth potential'},
                'pessimistic': {'score': 0.6, 'reasoning': 'Market volatility concerns'},
                'risk_manager': {'score': 0.7, 'reasoning': 'Moderate risk profile'}
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {str(e)}")
        return jsonify({'error': f'Failed to analyze {symbol}'}), 500

if __name__ == '__main__':
    # 개발 서버 실행
    host = os.getenv('BACKEND_HOST', 'localhost')
    port = int(os.getenv('BACKEND_PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"CORS origins: {cors_origins}")
    
    app.run(host=host, port=port, debug=debug)
