"""
AI Stock Trading System - Data Collector Module
주식 데이터 수집을 담당하는 모듈
"""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Manus API 클라이언트 추가
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDataCollector:
    """주식 데이터 수집 클래스"""
    
    def __init__(self, db_path: str = "data/stock_data.db"):
        """
        데이터 수집기 초기화
        
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.api_client = ApiClient()
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 주식 기본 정보 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_info (
                    symbol TEXT PRIMARY KEY,
                    company_name TEXT,
                    exchange TEXT,
                    currency TEXT,
                    sector TEXT,
                    industry TEXT,
                    market_cap REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 주식 가격 데이터 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date DATE,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    adjusted_close REAL,
                    volume INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # 뉴스 데이터 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    title TEXT,
                    content TEXT,
                    source TEXT,
                    published_at TIMESTAMP,
                    sentiment_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 분석 결과 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    agent_type TEXT,
                    analysis_type TEXT,
                    result_data TEXT,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("데이터베이스 초기화 완료")
    
    def collect_stock_data(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """
        특정 종목의 주식 데이터 수집
        
        Args:
            symbol: 주식 심볼 (예: AAPL, GOOGL)
            period: 데이터 수집 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            수집된 데이터 딕셔너리
        """
        try:
            logger.info(f"주식 데이터 수집 시작: {symbol} ({period})")
            
            # Yahoo Finance API를 통한 데이터 수집
            response = self.api_client.call_api('YahooFinance/get_stock_chart', query={
                'symbol': symbol,
                'region': 'US',
                'interval': '1d',
                'range': period,
                'includeAdjustedClose': True,
                'events': 'div,split'
            })
            
            if not response or 'chart' not in response or not response['chart']['result']:
                logger.error(f"데이터 수집 실패: {symbol}")
                return {}
            
            result = response['chart']['result'][0]
            meta = result['meta']
            
            # 기본 정보 저장
            self._save_stock_info(symbol, meta)
            
            # 가격 데이터 저장
            if 'timestamp' in result and 'indicators' in result:
                self._save_price_data(symbol, result)
            
            logger.info(f"데이터 수집 완료: {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"데이터 수집 중 오류 발생: {symbol} - {str(e)}")
            return {}
    
    def _save_stock_info(self, symbol: str, meta: Dict[str, Any]):
        """주식 기본 정보 저장"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO stock_info 
                (symbol, company_name, exchange, currency, market_cap, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                meta.get('longName', ''),
                meta.get('exchangeName', ''),
                meta.get('currency', ''),
                meta.get('marketCap', 0),
                datetime.now()
            ))
            
            conn.commit()
    
    def _save_price_data(self, symbol: str, result: Dict[str, Any]):
        """주식 가격 데이터 저장"""
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]
        adjusted_close = result['indicators'].get('adjclose', [{}])[0].get('adjclose', [])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for i, timestamp in enumerate(timestamps):
                date = datetime.fromtimestamp(timestamp).date()
                
                # None 값 처리
                open_price = quotes['open'][i] if i < len(quotes['open']) and quotes['open'][i] is not None else 0
                high_price = quotes['high'][i] if i < len(quotes['high']) and quotes['high'][i] is not None else 0
                low_price = quotes['low'][i] if i < len(quotes['low']) and quotes['low'][i] is not None else 0
                close_price = quotes['close'][i] if i < len(quotes['close']) and quotes['close'][i] is not None else 0
                volume = quotes['volume'][i] if i < len(quotes['volume']) and quotes['volume'][i] is not None else 0
                adj_close = adjusted_close[i] if i < len(adjusted_close) and adjusted_close[i] is not None else close_price
                
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_prices 
                    (symbol, date, open_price, high_price, low_price, close_price, adjusted_close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, date, open_price, high_price, low_price, close_price, adj_close, volume))
            
            conn.commit()
    
    def collect_multiple_stocks(self, symbols: List[str], period: str = "1mo") -> Dict[str, Any]:
        """
        여러 종목의 데이터를 일괄 수집
        
        Args:
            symbols: 주식 심볼 리스트
            period: 데이터 수집 기간
            
        Returns:
            수집 결과 딕셔너리
        """
        results = {}
        
        for symbol in symbols:
            try:
                result = self.collect_stock_data(symbol, period)
                results[symbol] = result
            except Exception as e:
                logger.error(f"종목 {symbol} 데이터 수집 실패: {str(e)}")
                results[symbol] = {}
        
        return results
    
    def get_latest_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        최근 데이터 조회
        
        Args:
            symbol: 주식 심볼
            days: 조회할 일수
            
        Returns:
            최근 데이터 리스트
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM stock_prices 
                WHERE symbol = ? AND date >= date('now', '-{} days')
                ORDER BY date DESC
            '''.format(days), (symbol,))
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def save_analysis_result(self, symbol: str, agent_type: str, analysis_type: str, 
                           result_data: Dict[str, Any], confidence_score: float = 0.0):
        """
        AI 에이전트 분석 결과 저장
        
        Args:
            symbol: 주식 심볼
            agent_type: 에이전트 타입 (optimistic, pessimistic, fundamental, technical)
            analysis_type: 분석 타입 (prediction, recommendation, risk_assessment)
            result_data: 분석 결과 데이터
            confidence_score: 신뢰도 점수 (0.0 ~ 1.0)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results 
                (symbol, agent_type, analysis_type, result_data, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, agent_type, analysis_type, json.dumps(result_data), confidence_score))
            
            conn.commit()
    
    def get_analysis_results(self, symbol: str, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        분석 결과 조회
        
        Args:
            symbol: 주식 심볼
            agent_type: 특정 에이전트 타입 (선택사항)
            
        Returns:
            분석 결과 리스트
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if agent_type:
                cursor.execute('''
                    SELECT * FROM analysis_results 
                    WHERE symbol = ? AND agent_type = ?
                    ORDER BY created_at DESC
                ''', (symbol, agent_type))
            else:
                cursor.execute('''
                    SELECT * FROM analysis_results 
                    WHERE symbol = ?
                    ORDER BY created_at DESC
                ''', (symbol,))
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result = dict(zip(columns, row))
                result['result_data'] = json.loads(result['result_data'])
                results.append(result)
            
            return results

# 테스트 및 예제 실행
if __name__ == "__main__":
    # 데이터 수집기 초기화
    collector = StockDataCollector()
    
    # 테스트용 주식 심볼들
    test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
    
    print("=== AI Stock Trading System - Data Collector ===")
    print(f"테스트 종목: {', '.join(test_symbols)}")
    
    # 데이터 수집 실행
    results = collector.collect_multiple_stocks(test_symbols, period="1mo")
    
    # 결과 출력
    for symbol, data in results.items():
        if data:
            print(f"\n✅ {symbol}: 데이터 수집 성공")
        else:
            print(f"\n❌ {symbol}: 데이터 수집 실패")
    
    # 최근 데이터 조회 예제
    print(f"\n=== AAPL 최근 5일 데이터 ===")
    recent_data = collector.get_latest_data('AAPL', days=5)
    for data in recent_data[:5]:
        print(f"{data['date']}: ${data['close_price']:.2f} (거래량: {data['volume']:,})")
