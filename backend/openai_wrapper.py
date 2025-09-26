"""
OpenAI API 안정화 래퍼
재시도, 타임아웃, 에러 처리 등을 포함한 안정적인 OpenAI API 호출
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIWrapper:
    """OpenAI API 안정화 래퍼 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        OpenAI 클라이언트 초기화
        
        Args:
            api_key: OpenAI API 키 (None이면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.timeout = int(os.getenv('OPENAI_TIMEOUT', '30'))
        self.max_retries = 3
        self.base_delay = 1  # 초기 재시도 지연 시간 (초)
        
        # 토큰 계산을 위한 인코더
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # 모델을 찾을 수 없으면 기본 인코딩 사용
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """텍스트의 토큰 수 계산"""
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            # 대략적인 추정 (1 토큰 ≈ 4 문자)
            return len(text) // 4
    
    def validate_input(self, messages: List[Dict[str, str]], max_tokens: int = 4000) -> bool:
        """입력 메시지 유효성 검사"""
        total_tokens = 0
        for message in messages:
            total_tokens += self.count_tokens(message.get('content', ''))
        
        if total_tokens > max_tokens:
            logger.warning(f"Input too long: {total_tokens} tokens (max: {max_tokens})")
            return False
        
        return True
    
    def chat_completion_with_retry(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        재시도 로직이 포함된 채팅 완성 요청
        
        Args:
            messages: 채팅 메시지 리스트
            temperature: 응답의 창의성 (0.0-2.0)
            max_tokens: 최대 응답 토큰 수
            **kwargs: 추가 OpenAI API 파라미터
        
        Returns:
            API 응답 또는 None (실패 시)
        """
        # 입력 유효성 검사
        if not self.validate_input(messages):
            return None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"OpenAI API call attempt {attempt + 1}/{self.max_retries}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # 성공적인 응답 처리
                result = {
                    'content': response.choices[0].message.content,
                    'model': response.model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'finish_reason': response.choices[0].finish_reason
                }
                
                logger.info(f"OpenAI API call successful. Tokens used: {result['usage']['total_tokens']}")
                return result
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"OpenAI API call failed (attempt {attempt + 1}): {error_msg}")
                
                # 특정 에러 타입에 따른 처리
                if "rate_limit" in error_msg.lower():
                    # 레이트 리밋 에러 - 더 긴 대기
                    delay = self.base_delay * (2 ** attempt) * 2
                    logger.info(f"Rate limit hit, waiting {delay} seconds...")
                    time.sleep(delay)
                elif "timeout" in error_msg.lower():
                    # 타임아웃 에러 - 짧은 대기 후 재시도
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Timeout occurred, waiting {delay} seconds...")
                    time.sleep(delay)
                elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                    # 할당량 초과 - 재시도 중단
                    logger.error("OpenAI quota exceeded or billing issue")
                    break
                else:
                    # 기타 에러 - 지수적 백오프
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Unknown error, waiting {delay} seconds...")
                    time.sleep(delay)
        
        logger.error("OpenAI API call failed after all retries")
        return None
    
    def analyze_stock_sentiment(self, symbol: str, news_data: str, financial_data: str) -> Optional[Dict[str, Any]]:
        """
        주식 감정 분석을 위한 특화된 메서드
        
        Args:
            symbol: 주식 심볼
            news_data: 뉴스 데이터
            financial_data: 재무 데이터
        
        Returns:
            분석 결과 또는 None
        """
        messages = [
            {
                "role": "system",
                "content": """You are a professional stock analyst. Analyze the provided information and give a structured response with:
1. Overall sentiment (POSITIVE/NEGATIVE/NEUTRAL)
2. Confidence score (0.0-1.0)
3. Key factors influencing the sentiment
4. Risk assessment
5. Short-term outlook (1-3 months)

Respond in JSON format."""
            },
            {
                "role": "user",
                "content": f"""Analyze {symbol}:

News Data:
{news_data[:2000]}  # 토큰 제한을 위해 자름

Financial Data:
{financial_data[:1000]}

Please provide a comprehensive analysis."""
            }
        ]
        
        return self.chat_completion_with_retry(
            messages=messages,
            temperature=0.3,  # 분석에는 낮은 창의성
            max_tokens=1000
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """현재 설정된 모델 정보 반환"""
        return {
            'model': self.model,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'api_key_configured': bool(self.api_key)
        }

# 전역 인스턴스 (싱글톤 패턴)
_openai_wrapper = None

def get_openai_wrapper() -> OpenAIWrapper:
    """OpenAI 래퍼 인스턴스 반환 (싱글톤)"""
    global _openai_wrapper
    if _openai_wrapper is None:
        _openai_wrapper = OpenAIWrapper()
    return _openai_wrapper

# 사용 예시
if __name__ == "__main__":
    # 테스트 코드
    wrapper = OpenAIWrapper()
    
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    result = wrapper.chat_completion_with_retry(test_messages)
    if result:
        print(f"Response: {result['content']}")
        print(f"Tokens used: {result['usage']['total_tokens']}")
    else:
        print("API call failed")
