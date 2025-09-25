"""
AI Stock Trading System - Cloud Storage Module
클라우드 스토리지 연동 및 데이터 백업 모듈
"""

import os
import json
import boto3
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class CloudStorageManager:
    """클라우드 스토리지 관리 클래스"""
    
    def __init__(self, bucket_name: str = "ai-stock-trading-data", 
                 aws_access_key: Optional[str] = None,
                 aws_secret_key: Optional[str] = None,
                 region: str = "us-east-1"):
        """
        클라우드 스토리지 매니저 초기화
        
        Args:
            bucket_name: S3 버킷 이름
            aws_access_key: AWS 액세스 키 (환경변수에서 자동 로드)
            aws_secret_key: AWS 시크릿 키 (환경변수에서 자동 로드)
            region: AWS 리전
        """
        self.bucket_name = bucket_name
        self.region = region
        
        # AWS 자격증명 설정
        try:
            if aws_access_key and aws_secret_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region
                )
            else:
                # 환경변수나 IAM 역할에서 자격증명 로드
                self.s3_client = boto3.client('s3', region_name=region)
            
            self.storage_available = True
            logger.info("클라우드 스토리지 연결 성공")
            
        except (NoCredentialsError, Exception) as e:
            logger.warning(f"클라우드 스토리지 연결 실패: {str(e)}")
            self.s3_client = None
            self.storage_available = False
    
    def create_bucket_if_not_exists(self) -> bool:
        """
        버킷이 존재하지 않으면 생성
        
        Returns:
            생성 성공 여부
        """
        if not self.storage_available:
            return False
        
        try:
            # 버킷 존재 확인
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"버킷 '{self.bucket_name}' 이미 존재")
            return True
            
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            
            if error_code == 404:
                # 버킷이 존재하지 않음 - 생성 시도
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    
                    logger.info(f"버킷 '{self.bucket_name}' 생성 성공")
                    return True
                    
                except ClientError as create_error:
                    logger.error(f"버킷 생성 실패: {str(create_error)}")
                    return False
            else:
                logger.error(f"버킷 확인 실패: {str(e)}")
                return False
    
    def upload_database_backup(self, db_path: str, backup_name: Optional[str] = None) -> bool:
        """
        데이터베이스 백업을 클라우드에 업로드
        
        Args:
            db_path: 로컬 데이터베이스 파일 경로
            backup_name: 백업 파일 이름 (기본값: 타임스탬프 포함)
            
        Returns:
            업로드 성공 여부
        """
        if not self.storage_available:
            logger.warning("클라우드 스토리지를 사용할 수 없음")
            return False
        
        if not os.path.exists(db_path):
            logger.error(f"데이터베이스 파일이 존재하지 않음: {db_path}")
            return False
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"database_backup_{timestamp}.db"
        
        try:
            # S3에 업로드
            s3_key = f"backups/{backup_name}"
            self.s3_client.upload_file(db_path, self.bucket_name, s3_key)
            
            logger.info(f"데이터베이스 백업 업로드 성공: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"데이터베이스 백업 업로드 실패: {str(e)}")
            return False
    
    def upload_analysis_results(self, analysis_data: Dict[str, Any], 
                              symbol: str, analysis_type: str) -> bool:
        """
        분석 결과를 클라우드에 업로드
        
        Args:
            analysis_data: 분석 결과 데이터
            symbol: 주식 심볼
            analysis_type: 분석 타입
            
        Returns:
            업로드 성공 여부
        """
        if not self.storage_available:
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"analysis/{symbol}/{analysis_type}_{timestamp}.json"
            
            # JSON 데이터를 문자열로 변환
            json_data = json.dumps(analysis_data, indent=2, ensure_ascii=False)
            
            # S3에 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            
            logger.info(f"분석 결과 업로드 성공: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"분석 결과 업로드 실패: {str(e)}")
            return False
    
    def download_analysis_results(self, symbol: str, analysis_type: str, 
                                limit: int = 10) -> List[Dict[str, Any]]:
        """
        클라우드에서 분석 결과 다운로드
        
        Args:
            symbol: 주식 심볼
            analysis_type: 분석 타입
            limit: 최대 다운로드 개수
            
        Returns:
            분석 결과 리스트
        """
        if not self.storage_available:
            return []
        
        try:
            prefix = f"analysis/{symbol}/"
            
            # 객체 목록 조회
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            results = []
            
            if 'Contents' in response:
                # 최신 순으로 정렬
                objects = sorted(response['Contents'], 
                               key=lambda x: x['LastModified'], reverse=True)
                
                for obj in objects:
                    if analysis_type in obj['Key']:
                        # 객체 다운로드
                        obj_response = self.s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        
                        # JSON 데이터 파싱
                        content = obj_response['Body'].read().decode('utf-8')
                        data = json.loads(content)
                        
                        results.append({
                            'key': obj['Key'],
                            'last_modified': obj['LastModified'],
                            'data': data
                        })
            
            logger.info(f"분석 결과 다운로드 완료: {len(results)}개")
            return results
            
        except Exception as e:
            logger.error(f"분석 결과 다운로드 실패: {str(e)}")
            return []
    
    def sync_local_to_cloud(self, local_db_path: str) -> Dict[str, Any]:
        """
        로컬 데이터베이스를 클라우드와 동기화
        
        Args:
            local_db_path: 로컬 데이터베이스 경로
            
        Returns:
            동기화 결과 딕셔너리
        """
        if not self.storage_available:
            return {'success': False, 'error': 'Cloud storage not available'}
        
        try:
            # 1. 데이터베이스 백업 업로드
            backup_success = self.upload_database_backup(local_db_path)
            
            # 2. 최근 분석 결과들을 클라우드에 업로드
            uploaded_analyses = 0
            
            with sqlite3.connect(local_db_path) as conn:
                cursor = conn.cursor()
                
                # 최근 24시간 내 분석 결과 조회
                cursor.execute('''
                    SELECT symbol, agent_type, analysis_type, result_data, created_at
                    FROM analysis_results 
                    WHERE created_at >= datetime('now', '-1 day')
                    ORDER BY created_at DESC
                ''')
                
                for row in cursor.fetchall():
                    symbol, agent_type, analysis_type, result_data, created_at = row
                    
                    analysis_data = {
                        'symbol': symbol,
                        'agent_type': agent_type,
                        'analysis_type': analysis_type,
                        'result_data': json.loads(result_data),
                        'created_at': created_at
                    }
                    
                    if self.upload_analysis_results(analysis_data, symbol, 
                                                  f"{agent_type}_{analysis_type}"):
                        uploaded_analyses += 1
            
            return {
                'success': True,
                'backup_uploaded': backup_success,
                'analyses_uploaded': uploaded_analyses,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"클라우드 동기화 실패: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_cloud_storage_stats(self) -> Dict[str, Any]:
        """
        클라우드 스토리지 통계 정보 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        if not self.storage_available:
            return {'available': False}
        
        try:
            stats = {'available': True}
            
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
            
            # 총 저장 용량 (근사치)
            total_size = 0
            if 'Contents' in backup_response:
                total_size += sum(obj['Size'] for obj in backup_response['Contents'])
            if 'Contents' in analysis_response:
                total_size += sum(obj['Size'] for obj in analysis_response['Contents'])
            
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"클라우드 스토리지 통계 조회 실패: {str(e)}")
            return {'available': False, 'error': str(e)}

class LocalStorageManager:
    """로컬 스토리지 관리 클래스 (클라우드 대안)"""
    
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

# 테스트 및 예제 실행
if __name__ == "__main__":
    print("=== AI Stock Trading System - Cloud Storage Manager ===")
    
    # 로컬 스토리지 매니저 테스트
    local_storage = LocalStorageManager()
    
    # 테스트 분석 데이터
    test_analysis = {
        'symbol': 'AAPL',
        'prediction': 'BUY',
        'confidence': 0.85,
        'reasoning': 'Strong technical indicators and positive sentiment',
        'timestamp': datetime.now().isoformat()
    }
    
    # 로컬 저장 테스트
    local_success = local_storage.save_analysis_result(
        test_analysis, 'AAPL', 'optimistic_analysis'
    )
    print(f"✅ 로컬 저장 테스트: {'성공' if local_success else '실패'}")
    
    # 데이터베이스 백업 테스트
    db_path = "data/stock_data.db"
    if os.path.exists(db_path):
        backup_success = local_storage.backup_database(db_path)
        print(f"✅ 로컬 백업 테스트: {'성공' if backup_success else '실패'}")
    
    # 클라우드 스토리지 매니저 테스트 (자격증명이 있는 경우에만)
    cloud_storage = CloudStorageManager()
    
    if cloud_storage.storage_available:
        print("☁️ 클라우드 스토리지 사용 가능")
        
        # 버킷 생성 테스트
        bucket_created = cloud_storage.create_bucket_if_not_exists()
        print(f"✅ 버킷 생성/확인: {'성공' if bucket_created else '실패'}")
        
        # 클라우드 통계
        stats = cloud_storage.get_cloud_storage_stats()
        print(f"📊 클라우드 통계: {stats}")
        
    else:
        print("⚠️ 클라우드 스토리지 사용 불가 (자격증명 필요)")
        print("💡 로컬 스토리지를 대안으로 사용합니다.")
