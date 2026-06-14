"""
AI Stock Trading System - Cloud Storage Module
클라우드 스토리지 연동 및 데이터 백업 모듈 (자격증명 오류 처리 포함)
"""

import os
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CloudStorageManager:
    """클라우드 스토리지 관리 클래스 (시뮬레이션)"""
    
    def __init__(self, bucket_name: str = "ai-stock-trading-data", 
                 aws_access_key: Optional[str] = None,
                 aws_secret_key: Optional[str] = None,
                 region: str = "us-east-1"):
        """
        클라우드 스토리지 매니저 초기화
        
        Args:
            bucket_name: S3 버킷 이름
            aws_access_key: AWS 액세스 키
            aws_secret_key: AWS 시크릿 키
            region: AWS 리전
        """
        self.bucket_name = bucket_name
        self.region = region
        
        # AWS 자격증명 확인
        aws_key = aws_access_key or os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret = aws_secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if aws_key and aws_secret:
            try:
                import boto3
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_key,
                    aws_secret_access_key=aws_secret,
                    region_name=region
                )
                self.storage_available = True
                logger.info("클라우드 스토리지 연결 성공")
            except Exception as e:
                logger.warning(f"클라우드 스토리지 연결 실패: {str(e)}")
                self.s3_client = None
                self.storage_available = False
        else:
            logger.info("AWS 자격증명이 없어 로컬 스토리지를 사용합니다")
            self.s3_client = None
            self.storage_available = False
            
        # 로컬 스토리지 대안 설정
        self.local_storage = LocalStorageManager()
    
    def upload_database_backup(self, db_path: str, backup_name: Optional[str] = None) -> bool:
        """
        데이터베이스 백업 (클라우드 또는 로컬)
        
        Args:
            db_path: 로컬 데이터베이스 파일 경로
            backup_name: 백업 파일 이름
            
        Returns:
            업로드 성공 여부
        """
        if self.storage_available:
            return self._upload_to_cloud(db_path, backup_name)
        else:
            return self.local_storage.backup_database(db_path, backup_name)
    
    def _upload_to_cloud(self, db_path: str, backup_name: Optional[str] = None) -> bool:
        """실제 클라우드 업로드 (AWS 자격증명이 있는 경우)"""
        if not os.path.exists(db_path):
            logger.error(f"데이터베이스 파일이 존재하지 않음: {db_path}")
            return False
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"database_backup_{timestamp}.db"
        
        try:
            s3_key = f"backups/{backup_name}"
            self.s3_client.upload_file(db_path, self.bucket_name, s3_key)
            logger.info(f"클라우드 백업 업로드 성공: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"클라우드 백업 업로드 실패: {str(e)}")
            return False
    
    def upload_analysis_results(self, analysis_data: Dict[str, Any], 
                              symbol: str, analysis_type: str) -> bool:
        """
        분석 결과 업로드 (클라우드 또는 로컬)
        
        Args:
            analysis_data: 분석 결과 데이터
            symbol: 주식 심볼
            analysis_type: 분석 타입
            
        Returns:
            업로드 성공 여부
        """
        if self.storage_available:
            return self._upload_analysis_to_cloud(analysis_data, symbol, analysis_type)
        else:
            return self.local_storage.save_analysis_result(analysis_data, symbol, analysis_type)
    
    def _upload_analysis_to_cloud(self, analysis_data: Dict[str, Any], 
                                symbol: str, analysis_type: str) -> bool:
        """실제 클라우드 분석 결과 업로드"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"analysis/{symbol}/{analysis_type}_{timestamp}.json"
            
            json_data = json.dumps(analysis_data, indent=2, ensure_ascii=False)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            
            logger.info(f"클라우드 분석 결과 업로드 성공: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"클라우드 분석 결과 업로드 실패: {str(e)}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        스토리지 통계 정보 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        if self.storage_available:
            return self._get_cloud_stats()
        else:
            return self.local_storage.get_storage_stats()
    
    def _get_cloud_stats(self) -> Dict[str, Any]:
        """클라우드 스토리지 통계"""
        try:
            stats = {'type': 'cloud', 'available': True}
            
            # 백업 파일 수
            backup_response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='backups/'
            )
            stats['backup_count'] = backup_response.get('KeyCount', 0)
            
            # 분석 결과 파일 수
            analysis_response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='analysis/'
            )
            stats['analysis_count'] = analysis_response.get('KeyCount', 0)
            
            return stats
        except Exception as e:
            logger.error(f"클라우드 통계 조회 실패: {str(e)}")
            return {'type': 'cloud', 'available': False, 'error': str(e)}

class LocalStorageManager:
    """로컬 스토리지 관리 클래스"""
    
    def __init__(self, storage_path: str = "data/storage"):
        """
        로컬 스토리지 매니저 초기화
        
        Args:
            storage_path: 로컬 저장소 경로
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        os.makedirs(os.path.join(storage_path, 'backups'), exist_ok=True)
        os.makedirs(os.path.join(storage_path, 'analysis'), exist_ok=True)
    
    def backup_database(self, db_path: str, backup_name: Optional[str] = None) -> bool:
        """
        데이터베이스 로컬 백업
        
        Args:
            db_path: 데이터베이스 파일 경로
            backup_name: 백업 파일 이름
            
        Returns:
            백업 성공 여부
        """
        if not os.path.exists(db_path):
            logger.error(f"데이터베이스 파일이 존재하지 않음: {db_path}")
            return False
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"database_backup_{timestamp}.db"
        
        try:
            import shutil
            backup_path = os.path.join(self.storage_path, 'backups', backup_name)
            shutil.copy2(db_path, backup_path)
            
            logger.info(f"로컬 백업 완료: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"로컬 백업 실패: {str(e)}")
            return False
    
    def save_analysis_result(self, analysis_data: Dict[str, Any], 
                           symbol: str, analysis_type: str) -> bool:
        """
        분석 결과 로컬 저장
        
        Args:
            analysis_data: 분석 결과 데이터
            symbol: 주식 심볼
            analysis_type: 분석 타입
            
        Returns:
            저장 성공 여부
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 심볼별 디렉토리 생성
            symbol_dir = os.path.join(self.storage_path, 'analysis', symbol)
            os.makedirs(symbol_dir, exist_ok=True)
            
            # 파일 저장
            filename = f"{analysis_type}_{timestamp}.json"
            filepath = os.path.join(symbol_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"분석 결과 로컬 저장 완료: {filepath}")
            return True
        except Exception as e:
            logger.error(f"분석 결과 로컬 저장 실패: {str(e)}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        로컬 스토리지 통계 정보
        
        Returns:
            통계 정보 딕셔너리
        """
        stats = {'type': 'local', 'available': True}
        
        try:
            # 백업 파일 수
            backup_dir = os.path.join(self.storage_path, 'backups')
            if os.path.exists(backup_dir):
                stats['backup_count'] = len([f for f in os.listdir(backup_dir) 
                                           if f.endswith('.db')])
            else:
                stats['backup_count'] = 0
            
            # 분석 결과 파일 수
            analysis_dir = os.path.join(self.storage_path, 'analysis')
            analysis_count = 0
            if os.path.exists(analysis_dir):
                for symbol_dir in os.listdir(analysis_dir):
                    symbol_path = os.path.join(analysis_dir, symbol_dir)
                    if os.path.isdir(symbol_path):
                        analysis_count += len([f for f in os.listdir(symbol_path) 
                                             if f.endswith('.json')])
            stats['analysis_count'] = analysis_count
            
            # 총 저장 용량
            total_size = 0
            for root, dirs, files in os.walk(self.storage_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    total_size += os.path.getsize(filepath)
            
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
        except Exception as e:
            logger.error(f"로컬 스토리지 통계 조회 실패: {str(e)}")
            stats['error'] = str(e)
        
        return stats
    
    def load_analysis_results(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        로컬에서 분석 결과 로드
        
        Args:
            symbol: 주식 심볼
            limit: 최대 로드 개수
            
        Returns:
            분석 결과 리스트
        """
        results = []
        
        try:
            symbol_dir = os.path.join(self.storage_path, 'analysis', symbol)
            
            if not os.path.exists(symbol_dir):
                return results
            
            # 파일 목록을 수정 시간 순으로 정렬
            files = []
            for filename in os.listdir(symbol_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(symbol_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    files.append((mtime, filepath, filename))
            
            # 최신 순으로 정렬
            files.sort(reverse=True)
            
            # 제한된 개수만큼 로드
            for _, filepath, filename in files[:limit]:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    results.append({
                        'filename': filename,
                        'filepath': filepath,
                        'data': data,
                        'modified_time': datetime.fromtimestamp(os.path.getmtime(filepath))
                    })
                except Exception as e:
                    logger.error(f"파일 로드 실패 {filepath}: {str(e)}")
            
        except Exception as e:
            logger.error(f"분석 결과 로드 실패: {str(e)}")
        
        return results

# 테스트 및 예제 실행
if __name__ == "__main__":
    print("=== AI Stock Trading System - Cloud Storage Manager ===")
    
    # 클라우드 스토리지 매니저 테스트
    cloud_storage = CloudStorageManager()
    
    # 테스트 분석 데이터
    test_analysis = {
        'symbol': 'AAPL',
        'prediction': 'BUY',
        'confidence': 0.85,
        'reasoning': 'Strong technical indicators and positive sentiment',
        'timestamp': datetime.now().isoformat()
    }
    
    # 분석 결과 저장 테스트
    analysis_success = cloud_storage.upload_analysis_results(
        test_analysis, 'AAPL', 'optimistic_analysis'
    )
    print(f"✅ 분석 결과 저장: {'성공' if analysis_success else '실패'}")
    
    # 데이터베이스 백업 테스트
    db_path = "data/stock_data.db"
    if os.path.exists(db_path):
        backup_success = cloud_storage.upload_database_backup(db_path)
        print(f"✅ 데이터베이스 백업: {'성공' if backup_success else '실패'}")
    else:
        print("⚠️ 데이터베이스 파일이 존재하지 않음")
    
    # 스토리지 통계
    stats = cloud_storage.get_storage_stats()
    print(f"\n📊 스토리지 통계:")
    print(f"  - 타입: {stats.get('type', 'unknown')}")
    print(f"  - 사용 가능: {stats.get('available', False)}")
    print(f"  - 백업 파일: {stats.get('backup_count', 0)}개")
    print(f"  - 분석 결과: {stats.get('analysis_count', 0)}개")
    
    if 'total_size_mb' in stats:
        print(f"  - 총 용량: {stats['total_size_mb']} MB")
    
    # 로컬 스토리지에서 분석 결과 로드 테스트
    if not cloud_storage.storage_available:
        print(f"\n📁 AAPL 분석 결과 로드 테스트:")
        local_results = cloud_storage.local_storage.load_analysis_results('AAPL', limit=3)
        
        if local_results:
            for i, result in enumerate(local_results, 1):
                print(f"  {i}. {result['filename']} - {result['modified_time']}")
        else:
            print("  저장된 분석 결과가 없습니다.")
    
    print(f"\n💡 {'클라우드' if cloud_storage.storage_available else '로컬'} 스토리지를 사용 중입니다.")
