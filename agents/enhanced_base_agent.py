"""
Enhanced Base Agent
AI Provider 추상화 계층을 사용하는 향상된 기본 에이전트 클래스
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from .ai_provider import AnalysisRequest, AnalysisResponse, ModelType
from .ai_provider_factory import AIProviderFactory, create_provider_by_name

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBaseAgent(ABC):
    """향상된 기본 AI 에이전트 클래스"""
    
    def __init__(self, 
                 agent_name: str,
                 primary_model: str = "openai_gpt4o_mini",
                 fallback_model: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        에이전트 초기화
        
        Args:
            agent_name: 에이전트 이름
            primary_model: 주 사용 모델
            fallback_model: 대체 모델
            config: 추가 설정
        """
        self.agent_name = agent_name
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.config = config or {}
        
        # AI Provider 팩토리 초기화
        self.factory = AIProviderFactory()
        
        # Provider 생성
        self._setup_providers()
        
        # 성능 메트릭
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "average_response_time": 0.0,
            "fallback_usage": 0
        }
    
    def _setup_providers(self):
        """AI Provider 설정"""
        try:
            # 주 모델 Provider
            self.primary_provider = create_provider_by_name(self.primary_model)
            logger.info(f"Primary provider initialized: {self.primary_model}")
            
            # 대체 모델 Provider (있는 경우)
            self.fallback_provider = None
            if self.fallback_model:
                try:
                    self.fallback_provider = create_provider_by_name(self.fallback_model)
                    logger.info(f"Fallback provider initialized: {self.fallback_model}")
                except Exception as e:
                    logger.warning(f"Failed to initialize fallback provider: {e}")
            
        except Exception as e:
            logger.error(f"Failed to setup providers: {e}")
            raise
    
    def analyze_stock(self, 
                     symbol: str, 
                     stock_data: Dict[str, Any],
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        주식 분석 수행
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            context: 추가 컨텍스트
            
        Returns:
            Dict[str, Any]: 분석 결과
        """
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # 분석 프롬프트 생성
            prompt = self._build_analysis_prompt(symbol, stock_data, context)
            
            # 분석 요청 생성
            request = AnalysisRequest(
                prompt=prompt,
                stock_data=stock_data,
                context=context,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1500)
            )
            
            # 분석 실행
            response = self._execute_analysis(request)
            
            # 결과 후처리
            result = self._process_analysis_result(response, symbol, stock_data)
            
            # 메트릭 업데이트
            self._update_metrics(response, time.time() - start_time, success=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            self.metrics["failed_requests"] += 1
            
            # 기본 응답 반환
            return self._create_error_response(symbol, str(e))
    
    def _execute_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """분석 실행 (폴백 로직 포함)"""
        try:
            # 주 모델로 분석 시도
            return self.primary_provider.generate_analysis(request)
            
        except Exception as e:
            logger.warning(f"Primary model failed: {e}")
            
            # 대체 모델로 시도
            if self.fallback_provider:
                try:
                    logger.info("Attempting with fallback model")
                    self.metrics["fallback_usage"] += 1
                    response = self.fallback_provider.generate_analysis(request)
                    
                    # 폴백 사용 표시
                    response.metadata = response.metadata or {}
                    response.metadata["fallback_used"] = True
                    
                    return response
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback model also failed: {fallback_error}")
                    raise fallback_error
            else:
                raise e
    
    @abstractmethod
    def _build_analysis_prompt(self, 
                              symbol: str, 
                              stock_data: Dict[str, Any],
                              context: Optional[Dict[str, Any]] = None) -> str:
        """
        분석 프롬프트 구성 (각 에이전트에서 구현)
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            context: 추가 컨텍스트
            
        Returns:
            str: 구성된 프롬프트
        """
        pass
    
    @abstractmethod
    def _get_agent_role(self) -> str:
        """에이전트 역할 반환 (각 에이전트에서 구현)"""
        pass
    
    def _process_analysis_result(self, 
                               response: AnalysisResponse,
                               symbol: str,
                               stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """분석 결과 후처리"""
        # 기본 결과 구조
        result = {
            "agent": self.agent_name,
            "symbol": symbol,
            "analysis": response.content,
            "recommendation": self._extract_recommendation(response.content),
            "confidence": response.confidence_score or self._extract_confidence(response.content),
            "target_price": self._extract_target_price(response.content),
            "risk_level": self._extract_risk_level(response.content),
            "timestamp": time.time(),
            "model_used": response.model_used,
            "tokens_used": response.tokens_used,
            "cost": response.cost_estimate,
            "processing_time": response.processing_time,
            "metadata": response.metadata or {}
        }
        
        # 에이전트별 추가 처리
        result.update(self._additional_processing(response, symbol, stock_data))
        
        return result
    
    def _extract_recommendation(self, content: str) -> str:
        """추천 의견 추출"""
        content_lower = content.lower()
        
        if "strong buy" in content_lower or "적극 매수" in content_lower:
            return "STRONG_BUY"
        elif "buy" in content_lower or "매수" in content_lower:
            return "BUY"
        elif "strong sell" in content_lower or "적극 매도" in content_lower:
            return "STRONG_SELL"
        elif "sell" in content_lower or "매도" in content_lower:
            return "SELL"
        else:
            return "HOLD"
    
    def _extract_confidence(self, content: str) -> Optional[float]:
        """신뢰도 추출"""
        import re
        
        patterns = [
            r'confidence[:\s]+(\d+)%',
            r'신뢰도[:\s]+(\d+)%',
            r'확신도[:\s]+(\d+)%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content.lower())
            if match:
                return float(match.group(1)) / 100.0
        
        return None
    
    def _extract_target_price(self, content: str) -> Optional[float]:
        """목표 가격 추출"""
        import re
        
        patterns = [
            r'target price[:\s]+\$?(\d+\.?\d*)',
            r'목표가[:\s]+\$?(\d+\.?\d*)',
            r'목표 가격[:\s]+\$?(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content.lower())
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_risk_level(self, content: str) -> str:
        """리스크 레벨 추출"""
        content_lower = content.lower()
        
        if "high risk" in content_lower or "고위험" in content_lower:
            return "HIGH"
        elif "low risk" in content_lower or "저위험" in content_lower:
            return "LOW"
        else:
            return "MEDIUM"
    
    def _additional_processing(self, 
                             response: AnalysisResponse,
                             symbol: str,
                             stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트별 추가 처리 (오버라이드 가능)"""
        return {}
    
    def _create_error_response(self, symbol: str, error_message: str) -> Dict[str, Any]:
        """오류 응답 생성"""
        return {
            "agent": self.agent_name,
            "symbol": symbol,
            "analysis": f"분석 중 오류가 발생했습니다: {error_message}",
            "recommendation": "HOLD",
            "confidence": 0.0,
            "target_price": None,
            "risk_level": "HIGH",
            "timestamp": time.time(),
            "error": True,
            "error_message": error_message
        }
    
    def _update_metrics(self, response: AnalysisResponse, processing_time: float, success: bool):
        """메트릭 업데이트"""
        if success:
            self.metrics["successful_requests"] += 1
            self.metrics["total_cost"] += response.cost_estimate
            self.metrics["total_tokens"] += response.tokens_used
            
            # 평균 응답 시간 업데이트
            total_time = (self.metrics["average_response_time"] * 
                         (self.metrics["successful_requests"] - 1) + processing_time)
            self.metrics["average_response_time"] = total_time / self.metrics["successful_requests"]
    
    def get_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 반환"""
        success_rate = (self.metrics["successful_requests"] / 
                       max(self.metrics["total_requests"], 1))
        
        return {
            **self.metrics,
            "success_rate": success_rate,
            "fallback_rate": self.metrics["fallback_usage"] / max(self.metrics["total_requests"], 1)
        }
    
    def estimate_cost(self, symbol: str, stock_data: Dict[str, Any]) -> float:
        """분석 비용 추정"""
        prompt = self._build_analysis_prompt(symbol, stock_data)
        return self.primary_provider.estimate_cost(prompt, self.config.get("max_tokens", 1500))
    
    def switch_model(self, new_model: str):
        """모델 변경"""
        try:
            old_model = self.primary_model
            self.primary_model = new_model
            self.primary_provider = create_provider_by_name(new_model)
            logger.info(f"Model switched from {old_model} to {new_model}")
        except Exception as e:
            logger.error(f"Failed to switch model: {e}")
            raise
