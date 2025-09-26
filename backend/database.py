"""
AI Stock Trading System - Database Management Module
데이터베이스 관리 및 유틸리티 모듈
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "data/stock_data.db"):
        """
        데이터베이스 매니저 초기화
        
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결 반환 (WAL 모드 활성화)"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        
        # WAL 모드 활성화 (동시성 개선)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        SELECT 쿼리 실행
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            쿼리 결과 리스트
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        INSERT/UPDATE/DELETE 쿼리 실행
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            영향받은 행 수
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def get_stock_price_data(self, symbol: str, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """
        주식 가격 데이터를 DataFrame으로 반환
        
        Args:
            symbol: 주식 심볼
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            주식 가격 데이터 DataFrame
        """
        query = """
            SELECT date, open_price, high_price, low_price, close_price, 
                   adjusted_close, volume
            FROM stock_prices 
            WHERE symbol = ?
        """
        params = [symbol]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date"
        
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            return df
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        포트폴리오 요약 정보 반환
        
        Returns:
            포트폴리오 요약 딕셔너리
        """
        # 보유 종목 수
        stock_count_query = "SELECT COUNT(DISTINCT symbol) as count FROM stock_prices"
        stock_count = self.execute_query(stock_count_query)[0]['count']
        
        # 최근 분석 결과 수
        analysis_count_query = """
            SELECT COUNT(*) as count FROM analysis_results 
            WHERE created_at >= date('now', '-7 days')
        """
        analysis_count = self.execute_query(analysis_count_query)[0]['count']
        
        # 최근 업데이트된 종목들
        recent_updates_query = """
            SELECT symbol, MAX(date) as last_update
            FROM stock_prices 
            GROUP BY symbol 
            ORDER BY last_update DESC 
            LIMIT 10
        """
        recent_updates = self.execute_query(recent_updates_query)
        
        return {
            'total_stocks': stock_count,
            'recent_analyses': analysis_count,
            'recent_updates': recent_updates,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_analysis_summary(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        특정 종목의 분석 요약 정보
        
        Args:
            symbol: 주식 심볼
            days: 조회할 일수
            
        Returns:
            분석 요약 딕셔너리
        """
        query = """
            SELECT agent_type, analysis_type, AVG(confidence_score) as avg_confidence,
                   COUNT(*) as analysis_count, MAX(created_at) as last_analysis
            FROM analysis_results 
            WHERE symbol = ? AND created_at >= date('now', '-{} days')
            GROUP BY agent_type, analysis_type
            ORDER BY last_analysis DESC
        """.format(days)
        
        results = self.execute_query(query, (symbol,))
        
        # 최근 분석 결과들
        recent_query = """
            SELECT * FROM analysis_results 
            WHERE symbol = ? AND created_at >= date('now', '-{} days')
            ORDER BY created_at DESC 
            LIMIT 10
        """.format(days)
        
        recent_analyses = self.execute_query(recent_query, (symbol,))
        
        # JSON 데이터 파싱
        for analysis in recent_analyses:
            analysis['result_data'] = json.loads(analysis['result_data'])
        
        return {
            'symbol': symbol,
            'summary': results,
            'recent_analyses': recent_analyses
        }
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """
        오래된 데이터 정리
        
        Args:
            days_to_keep: 보관할 일수
        """
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date()
        
        # 오래된 가격 데이터 삭제
        price_query = "DELETE FROM stock_prices WHERE date < ?"
        deleted_prices = self.execute_update(price_query, (cutoff_date,))
        
        # 오래된 분석 결과 삭제
        analysis_query = "DELETE FROM analysis_results WHERE created_at < ?"
        deleted_analyses = self.execute_update(analysis_query, (cutoff_date,))
        
        # 오래된 뉴스 데이터 삭제
        news_query = "DELETE FROM news_data WHERE created_at < ?"
        deleted_news = self.execute_update(news_query, (cutoff_date,))
        
        logger.info(f"데이터 정리 완료: 가격 데이터 {deleted_prices}개, "
                   f"분석 결과 {deleted_analyses}개, 뉴스 {deleted_news}개 삭제")
        
        return {
            'deleted_prices': deleted_prices,
            'deleted_analyses': deleted_analyses,
            'deleted_news': deleted_news
        }
    
    def backup_database(self, backup_path: str):
        """
        데이터베이스 백업
        
        Args:
            backup_path: 백업 파일 경로
        """
        import shutil
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"데이터베이스 백업 완료: {backup_path}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        데이터베이스 통계 정보 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        stats = {}
        
        # 각 테이블의 행 수
        tables = ['stock_info', 'stock_prices', 'news_data', 'analysis_results']
        
        for table in tables:
            query = f"SELECT COUNT(*) as count FROM {table}"
            result = self.execute_query(query)
            stats[f'{table}_count'] = result[0]['count']
        
        # 데이터베이스 파일 크기
        import os
        if os.path.exists(self.db_path):
            stats['db_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0
        
        # 가장 오래된/최신 데이터
        oldest_query = "SELECT MIN(date) as oldest_date FROM stock_prices"
        newest_query = "SELECT MAX(date) as newest_date FROM stock_prices"
        
        oldest_result = self.execute_query(oldest_query)
        newest_result = self.execute_query(newest_query)
        
        stats['oldest_data'] = oldest_result[0]['oldest_date'] if oldest_result[0]['oldest_date'] else None
        stats['newest_data'] = newest_result[0]['newest_date'] if newest_result[0]['newest_date'] else None
        
        return stats

class DataValidator:
    """데이터 유효성 검증 클래스"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def validate_price_data(self, symbol: str) -> Dict[str, Any]:
        """
        가격 데이터 유효성 검증
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            검증 결과 딕셔너리
        """
        df = self.db_manager.get_stock_price_data(symbol)
        
        if df.empty:
            return {'valid': False, 'error': 'No data found'}
        
        issues = []
        
        # 가격 데이터 검증
        if (df['close_price'] <= 0).any():
            issues.append('Invalid close prices (<=0) found')
        
        if (df['volume'] < 0).any():
            issues.append('Invalid volume (<0) found')
        
        if (df['high_price'] < df['low_price']).any():
            issues.append('High price less than low price found')
        
        # 데이터 연속성 검증
        date_gaps = df.index.to_series().diff().dt.days
        large_gaps = date_gaps[date_gaps > 7]  # 7일 이상 간격
        
        if not large_gaps.empty:
            issues.append(f'Large date gaps found: {len(large_gaps)} gaps > 7 days')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'data_points': len(df),
            'date_range': {
                'start': df.index.min().strftime('%Y-%m-%d'),
                'end': df.index.max().strftime('%Y-%m-%d')
            }
        }
    
    def validate_all_stocks(self) -> Dict[str, Any]:
        """
        모든 종목의 데이터 유효성 검증
        
        Returns:
            전체 검증 결과 딕셔너리
        """
        query = "SELECT DISTINCT symbol FROM stock_prices"
        symbols = [row['symbol'] for row in self.db_manager.execute_query(query)]
        
        results = {}
        total_issues = 0
        
        for symbol in symbols:
            validation = self.validate_price_data(symbol)
            results[symbol] = validation
            if not validation['valid']:
                total_issues += len(validation['issues'])
        
        return {
            'total_stocks': len(symbols),
            'valid_stocks': sum(1 for r in results.values() if r['valid']),
            'total_issues': total_issues,
            'details': results
        }

# 테스트 및 예제 실행
if __name__ == "__main__":
    # 데이터베이스 매니저 초기화
    db_manager = DatabaseManager()
    validator = DataValidator(db_manager)
    
    print("=== AI Stock Trading System - Database Manager ===")
    
    # 데이터베이스 통계
    stats = db_manager.get_database_stats()
    print(f"\n📊 데이터베이스 통계:")
    print(f"  - 종목 정보: {stats['stock_info_count']}개")
    print(f"  - 가격 데이터: {stats['stock_prices_count']}개")
    print(f"  - 분석 결과: {stats['analysis_results_count']}개")
    print(f"  - DB 크기: {stats['db_size_mb']} MB")
    print(f"  - 데이터 범위: {stats['oldest_data']} ~ {stats['newest_data']}")
    
    # 포트폴리오 요약
    portfolio = db_manager.get_portfolio_summary()
    print(f"\n📈 포트폴리오 요약:")
    print(f"  - 총 종목 수: {portfolio['total_stocks']}개")
    print(f"  - 최근 분석: {portfolio['recent_analyses']}개")
    
    # 데이터 유효성 검증
    print(f"\n🔍 데이터 유효성 검증:")
    validation_results = validator.validate_all_stocks()
    print(f"  - 총 종목: {validation_results['total_stocks']}개")
    print(f"  - 유효한 종목: {validation_results['valid_stocks']}개")
    print(f"  - 총 이슈: {validation_results['total_issues']}개")
    
    # AAPL 데이터 예제
    if validation_results['total_stocks'] > 0:
        print(f"\n📊 AAPL 데이터 샘플:")
        df = db_manager.get_stock_price_data('AAPL')
        if not df.empty:
            print(f"  - 데이터 포인트: {len(df)}개")
            print(f"  - 최근 종가: ${df['close_price'].iloc[-1]:.2f}")
            print(f"  - 최근 거래량: {df['volume'].iloc[-1]:,}")
