"""
AI Provider 팩토리
다양한 AI 모델 어댑터를 생성하고 관리하는 팩토리 클래스
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path

from .ai_provider import (
    AIProvider, ModelType, MODEL_REGISTRY, get_model_info,
    AIProviderError, ModelNotAvailableError
)
from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter, is_gemini_available

class AIProviderFactory:
    """AI Provider 팩토리 클래스"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        팩토리 초기화
        
        Args:
            config_path: 설정 파일 경로 (없으면 기본 설정 사용)
        """
        self.config = self._load_config(config_path)
        self._provider_cache: Dict[str, AIProvider] = {}
    
    def create_provider(self, model_type: ModelType, api_key: Optional[str] = None) -> AIProvider:
        """
        AI Provider 생성
        
        Args:
            model_type: 모델 타입
            api_key: API 키 (없으면 환경변수에서 자동 탐지)
            
        Returns:
            AIProvider: 생성된 AI Provider
        """
        # 캐시에서 확인
        cache_key = f"{model_type.value}_{api_key or 'default'}"
        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]
        
        # 모델 정보 가져오기
        model_info = get_model_info(model_type)
        
        # API 키 결정
        if api_key is None:
            api_key = self._get_api_key_for_provider(model_info.provider)
        
        # Provider 생성
        provider = self._create_provider_instance(model_type, model_info, api_key)
        
        # 캐시에 저장
        self._provider_cache[cache_key] = provider
        
        return provider
    
    def create_provider_by_name(self, model_name: str, api_key: Optional[str] = None) -> AIProvider:
        """
        모델 이름으로 AI Provider 생성
        
        Args:
            model_name: 모델 이름 (예: "openai_gpt4o", "google_gemini_pro")
            api_key: API 키
            
        Returns:
            AIProvider: 생성된 AI Provider
        """
        try:
            model_type = ModelType(model_name)
            return self.create_provider(model_type, api_key)
        except ValueError:
            raise AIProviderError(f"Unknown model name: {model_name}")
    
    def get_available_providers(self) -> List[ModelType]:
        """
        사용 가능한 Provider 목록 반환
        
        Returns:
            List[ModelType]: 사용 가능한 모델 타입 목록
        """
        available = []
        
        for model_type in ModelType:
            try:
                model_info = get_model_info(model_type)
                api_key = self._get_api_key_for_provider(model_info.provider)
                
                if api_key and self._is_provider_available(model_type):
                    available.append(model_type)
            except Exception:
                continue
        
        return available
    
    def get_cheapest_provider(self, available_only: bool = True) -> Optional[ModelType]:
        """
        가장 저렴한 Provider 반환
        
        Args:
            available_only: 사용 가능한 것만 고려할지 여부
            
        Returns:
            Optional[ModelType]: 가장 저렴한 모델 타입
        """
        candidates = self.get_available_providers() if available_only else list(ModelType)
        
        if not candidates:
            return None
        
        cheapest = min(
            candidates,
            key=lambda x: (
                get_model_info(x).cost_per_input_token + 
                get_model_info(x).cost_per_output_token
            )
        )
        
        return cheapest
    
    def get_most_capable_provider(self, available_only: bool = True) -> Optional[ModelType]:
        """
        가장 성능이 좋은 Provider 반환
        
        Args:
            available_only: 사용 가능한 것만 고려할지 여부
            
        Returns:
            Optional[ModelType]: 가장 성능이 좋은 모델 타입
        """
        candidates = self.get_available_providers() if available_only else list(ModelType)
        
        if not candidates:
            return None
        
        most_capable = max(
            candidates,
            key=lambda x: get_model_info(x).max_tokens
        )
        
        return most_capable
    
    def create_cascading_providers(self, primary: ModelType, fallback: ModelType) -> 'CascadingProvider':
        """
        캐스케이딩 Provider 생성 (주 모델 실패 시 대체 모델 사용)
        
        Args:
            primary: 주 모델
            fallback: 대체 모델
            
        Returns:
            CascadingProvider: 캐스케이딩 Provider
        """
        primary_provider = self.create_provider(primary)
        fallback_provider = self.create_provider(fallback)
        
        return CascadingProvider(primary_provider, fallback_provider)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """설정 파일 로드"""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Failed to load config file {config_path}: {e}")
        
        # 기본 설정 반환
        return {
            "api_keys": {},
            "model_preferences": {
                "default": "openai_gpt4o_mini",
                "high_performance": "openai_gpt4o",
                "cost_effective": "google_gemini_flash"
            }
        }
    
    def _get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """Provider별 API 키 가져오기"""
        # 설정 파일에서 먼저 확인
        if provider in self.config.get("api_keys", {}):
            return self.config["api_keys"][provider]
        
        # 환경변수에서 확인
        env_key_map = {
            "openai": ["OPENAI_API_KEY"],
            "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"]
        }
        
        for env_key in env_key_map.get(provider, []):
            api_key = os.getenv(env_key)
            if api_key:
                return api_key
        
        return None
    
    def _create_provider_instance(self, model_type: ModelType, model_info, api_key: str) -> AIProvider:
        """Provider 인스턴스 생성"""
        if model_info.provider == "openai":
            return OpenAIAdapter(model_info, api_key)
        elif model_info.provider == "google":
            if not is_gemini_available():
                raise AIProviderError("Google Generative AI library not installed")
            return GeminiAdapter(model_info, api_key)
        else:
            raise AIProviderError(f"Unsupported provider: {model_info.provider}")
    
    def _is_provider_available(self, model_type: ModelType) -> bool:
        """Provider 사용 가능 여부 확인"""
        try:
            model_info = get_model_info(model_type)
            
            # 라이브러리 가용성 확인
            if model_info.provider == "google" and not is_gemini_available():
                return False
            
            return True
        except Exception:
            return False

class CascadingProvider(AIProvider):
    """캐스케이딩 Provider (주 모델 실패 시 대체 모델 사용)"""
    
    def __init__(self, primary: AIProvider, fallback: AIProvider):
        self.primary = primary
        self.fallback = fallback
        self.model_info = primary.model_info  # 주 모델 정보 사용
    
    def _initialize_client(self):
        """클라이언트는 이미 초기화됨"""
        pass
    
    def generate_analysis(self, request):
        """분석 생성 (캐스케이딩)"""
        try:
            return self.primary.generate_analysis(request)
        except Exception as e:
            print(f"Primary model failed ({e}), falling back to secondary model")
            response = self.fallback.generate_analysis(request)
            # 메타데이터에 폴백 정보 추가
            response.metadata = response.metadata or {}
            response.metadata["fallback_used"] = True
            response.metadata["primary_error"] = str(e)
            return response
    
    def estimate_cost(self, prompt: str, max_tokens: int = 1000) -> float:
        """비용 추정 (주 모델 기준)"""
        return self.primary.estimate_cost(prompt, max_tokens)
    
    def count_tokens(self, text: str) -> int:
        """토큰 수 계산 (주 모델 기준)"""
        return self.primary.count_tokens(text)

# 전역 팩토리 인스턴스
_global_factory: Optional[AIProviderFactory] = None

def get_factory() -> AIProviderFactory:
    """전역 팩토리 인스턴스 반환"""
    global _global_factory
    if _global_factory is None:
        _global_factory = AIProviderFactory()
    return _global_factory

def create_provider(model_type: ModelType, api_key: Optional[str] = None) -> AIProvider:
    """편의 함수: Provider 생성"""
    return get_factory().create_provider(model_type, api_key)

def create_provider_by_name(model_name: str, api_key: Optional[str] = None) -> AIProvider:
    """편의 함수: 이름으로 Provider 생성"""
    return get_factory().create_provider_by_name(model_name, api_key)
