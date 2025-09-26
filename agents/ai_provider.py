"""
AI Provider 추상화 계층
다양한 AI 모델을 통합하여 사용할 수 있는 추상 인터페이스를 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """지원하는 AI 모델 타입"""
    OPENAI_GPT41_MINI = "gpt-4.1-mini"
    OPENAI_GPT41_NANO = "gpt-4.1-nano"
    GOOGLE_GEMINI_25_FLASH = "gemini-2.5-flash"
    # 레거시 모델들 (참조용)
    OPENAI_GPT4O = "openai_gpt4o"
    OPENAI_GPT4O_MINI = "openai_gpt4o_mini"
    GOOGLE_GEMINI_PRO = "google_gemini_pro"
    GOOGLE_GEMINI_FLASH = "google_gemini_flash"

@dataclass
class ModelInfo:
    """AI 모델 정보"""
    name: str
    provider: str
    model_id: str
    cost_per_input_token: float
    cost_per_output_token: float
    max_tokens: int
    supports_streaming: bool = False
    supports_function_calling: bool = False

@dataclass
class AnalysisRequest:
    """분석 요청 데이터 구조"""
    prompt: str
    stock_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    stream: bool = False

@dataclass
class AnalysisResponse:
    """분석 응답 데이터 구조"""
    content: str
    model_used: str
    tokens_used: int
    cost_estimate: float
    processing_time: float
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class AIProvider(ABC):
    """AI 모델 제공자 추상 클래스"""
    
    def __init__(self, model_info: ModelInfo, api_key: str):
        self.model_info = model_info
        self.api_key = api_key
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """AI 클라이언트 초기화"""
        pass
    
    @abstractmethod
    def generate_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        주식 분석 생성
        
        Args:
            request: 분석 요청 데이터
            
        Returns:
            AnalysisResponse: 분석 결과
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, prompt: str, max_tokens: int = 1000) -> float:
        """
        API 호출 비용 추정
        
        Args:
            prompt: 입력 프롬프트
            max_tokens: 최대 출력 토큰 수
            
        Returns:
            float: 예상 비용 (USD)
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        텍스트의 토큰 수 계산
        
        Args:
            text: 계산할 텍스트
            
        Returns:
            int: 토큰 수
        """
        pass
    
    def get_model_info(self) -> ModelInfo:
        """모델 정보 반환"""
        return self.model_info
    
    def is_available(self) -> bool:
        """모델 사용 가능 여부 확인"""
        try:
            # 간단한 테스트 요청으로 가용성 확인
            test_request = AnalysisRequest(
                prompt="Test",
                stock_data={},
                max_tokens=10
            )
            response = self.generate_analysis(test_request)
            return response is not None
        except Exception as e:
            logger.error(f"Model availability check failed: {e}")
            return False

class AIProviderError(Exception):
    """AI Provider 관련 예외"""
    pass

class ModelNotAvailableError(AIProviderError):
    """모델 사용 불가 예외"""
    pass

class APIQuotaExceededError(AIProviderError):
    """API 할당량 초과 예외"""
    pass

class InvalidRequestError(AIProviderError):
    """잘못된 요청 예외"""
    pass

# 모델 정보 레지스트리
MODEL_REGISTRY = {
    ModelType.OPENAI_GPT41_MINI: ModelInfo(
        name="GPT-4.1 Mini",
        provider="openai",
        model_id="gpt-4.1-mini",
        cost_per_input_token=0.00000015,
        cost_per_output_token=0.0000006,
        max_tokens=128000,
        supports_streaming=True,
        supports_function_calling=True
    ),
    ModelType.OPENAI_GPT41_NANO: ModelInfo(
        name="GPT-4.1 Nano",
        provider="openai",
        model_id="gpt-4.1-nano",
        cost_per_input_token=0.00000005,
        cost_per_output_token=0.0000002,
        max_tokens=64000,
        supports_streaming=True,
        supports_function_calling=True
    ),
    ModelType.GOOGLE_GEMINI_25_FLASH: ModelInfo(
        name="Gemini 2.5 Flash",
        provider="google",
        model_id="gemini-2.5-flash",
        cost_per_input_token=0.000000075,
        cost_per_output_token=0.0000003,
        max_tokens=1048576,
        supports_streaming=True,
        supports_function_calling=True
    ),
    # 레거시 모델들 (호환성 유지)
    ModelType.OPENAI_GPT4O: ModelInfo(
        name="GPT-4o",
        provider="openai",
        model_id="gpt-4o",
        cost_per_input_token=0.000005,
        cost_per_output_token=0.000015,
        max_tokens=128000,
        supports_streaming=True,
        supports_function_calling=True
    ),
    ModelType.OPENAI_GPT4O_MINI: ModelInfo(
        name="GPT-4o Mini",
        provider="openai", 
        model_id="gpt-4o-mini",
        cost_per_input_token=0.00000015,
        cost_per_output_token=0.0000006,
        max_tokens=128000,
        supports_streaming=True,
        supports_function_calling=True
    ),
    ModelType.GOOGLE_GEMINI_PRO: ModelInfo(
        name="Gemini 1.5 Pro",
        provider="google",
        model_id="gemini-1.5-pro",
        cost_per_input_token=0.0000035,
        cost_per_output_token=0.0000105,
        max_tokens=2097152,
        supports_streaming=True,
        supports_function_calling=True
    ),
    ModelType.GOOGLE_GEMINI_FLASH: ModelInfo(
        name="Gemini 1.5 Flash",
        provider="google",
        model_id="gemini-1.5-flash",
        cost_per_input_token=0.000000075,
        cost_per_output_token=0.0000003,
        max_tokens=1048576,
        supports_streaming=True,
        supports_function_calling=True
    )
}

def get_model_info(model_type: ModelType) -> ModelInfo:
    """모델 타입으로 모델 정보 조회"""
    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported model type: {model_type}")
    return MODEL_REGISTRY[model_type]

def list_available_models() -> List[ModelType]:
    """사용 가능한 모델 목록 반환"""
    return list(MODEL_REGISTRY.keys())

def get_cheapest_model() -> ModelType:
    """가장 저렴한 모델 반환"""
    cheapest = min(
        MODEL_REGISTRY.items(),
        key=lambda x: x[1].cost_per_input_token + x[1].cost_per_output_token
    )
    return cheapest[0]

def get_most_capable_model() -> ModelType:
    """가장 성능이 좋은 모델 반환 (토큰 수 기준)"""
    most_capable = max(
        MODEL_REGISTRY.items(),
        key=lambda x: x[1].max_tokens
    )
    return most_capable[0]
