"""
OpenAI API 어댑터
OpenAI의 GPT 모델들을 위한 구체적인 구현체
"""

import os
import time
import tiktoken
from typing import Dict, Any, Optional
from openai import OpenAI

from .ai_provider import (
    AIProvider, AnalysisRequest, AnalysisResponse, ModelInfo,
    AIProviderError, ModelNotAvailableError, APIQuotaExceededError,
    InvalidRequestError
)

class OpenAIAdapter(AIProvider):
    """OpenAI API 어댑터"""
    
    def _initialize_client(self):
        """OpenAI 클라이언트 초기화"""
        try:
            self.client = OpenAI(api_key=self.api_key)
            # 토큰 인코더 초기화
            self.encoding = tiktoken.encoding_for_model(self.model_info.model_id)
        except Exception as e:
            raise AIProviderError(f"Failed to initialize OpenAI client: {e}")
    
    def generate_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """주식 분석 생성"""
        start_time = time.time()
        
        try:
            # 프롬프트 구성
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(request.prompt, request.stock_data)
            
            # API 호출
            response = self.client.chat.completions.create(
                model=self.model_info.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )
            
            # 응답 처리
            if request.stream:
                content = self._handle_streaming_response(response)
            else:
                content = response.choices[0].message.content
            
            # 토큰 사용량 계산
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
            
            # 비용 계산
            cost_estimate = self._calculate_cost(
                response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                response.usage.completion_tokens if hasattr(response, 'usage') else 0
            )
            
            processing_time = time.time() - start_time
            
            return AnalysisResponse(
                content=content,
                model_used=self.model_info.model_id,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                processing_time=processing_time,
                confidence_score=self._extract_confidence_score(content),
                metadata={
                    "provider": "openai",
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                }
            )
            
        except Exception as e:
            self._handle_api_error(e)
    
    def estimate_cost(self, prompt: str, max_tokens: int = 1000) -> float:
        """API 호출 비용 추정"""
        input_tokens = self.count_tokens(prompt)
        output_tokens = max_tokens  # 최대 출력 토큰으로 추정
        
        return self._calculate_cost(input_tokens, output_tokens)
    
    def count_tokens(self, text: str) -> int:
        """텍스트의 토큰 수 계산"""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # 대략적인 추정 (1 토큰 ≈ 4 문자)
            return len(text) // 4
    
    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 구성"""
        return """You are a professional stock market analyst with expertise in financial analysis and investment recommendations. 
        
Your role is to provide comprehensive, data-driven analysis of stocks based on the provided market data and context. 
Always structure your response with clear reasoning, risk assessment, and actionable insights.

Response format should include:
1. Analysis summary
2. Key findings
3. Risk factors
4. Recommendation (BUY/HOLD/SELL)
5. Confidence level (0-100%)
6. Target price (if applicable)

Be objective, thorough, and professional in your analysis."""
    
    def _build_user_prompt(self, prompt: str, stock_data: Dict[str, Any]) -> str:
        """사용자 프롬프트 구성"""
        stock_info = ""
        if stock_data:
            stock_info = f"""
Stock Data:
- Symbol: {stock_data.get('symbol', 'N/A')}
- Current Price: ${stock_data.get('current_price', 'N/A')}
- Volume: {stock_data.get('volume', 'N/A')}
- Market Cap: {stock_data.get('market_cap', 'N/A')}
- P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
- 52-Week High: ${stock_data.get('week_52_high', 'N/A')}
- 52-Week Low: ${stock_data.get('week_52_low', 'N/A')}
- Additional Data: {stock_data.get('additional_info', {})}
"""
        
        return f"""
{stock_info}

Analysis Request:
{prompt}

Please provide a comprehensive analysis based on the above information.
"""
    
    def _handle_streaming_response(self, response) -> str:
        """스트리밍 응답 처리"""
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
        return content
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """비용 계산"""
        input_cost = input_tokens * self.model_info.cost_per_input_token
        output_cost = output_tokens * self.model_info.cost_per_output_token
        return input_cost + output_cost
    
    def _extract_confidence_score(self, content: str) -> Optional[float]:
        """응답에서 신뢰도 점수 추출"""
        import re
        
        # 신뢰도 패턴 매칭 (예: "Confidence: 85%", "신뢰도: 90%")
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
    
    def _handle_api_error(self, error: Exception):
        """API 오류 처리"""
        error_message = str(error).lower()
        
        if "rate limit" in error_message or "quota" in error_message:
            raise APIQuotaExceededError(f"OpenAI API quota exceeded: {error}")
        elif "invalid" in error_message or "bad request" in error_message:
            raise InvalidRequestError(f"Invalid request to OpenAI API: {error}")
        elif "model" in error_message and "not found" in error_message:
            raise ModelNotAvailableError(f"OpenAI model not available: {error}")
        else:
            raise AIProviderError(f"OpenAI API error: {error}")

# 편의 함수들
def create_openai_gpt4o_adapter(api_key: Optional[str] = None) -> OpenAIAdapter:
    """GPT-4o 어댑터 생성"""
    from .ai_provider import MODEL_REGISTRY, ModelType
    
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
    
    model_info = MODEL_REGISTRY[ModelType.OPENAI_GPT4O]
    return OpenAIAdapter(model_info, api_key)

def create_openai_gpt4o_mini_adapter(api_key: Optional[str] = None) -> OpenAIAdapter:
    """GPT-4o Mini 어댑터 생성"""
    from .ai_provider import MODEL_REGISTRY, ModelType
    
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
    
    model_info = MODEL_REGISTRY[ModelType.OPENAI_GPT4O_MINI]
    return OpenAIAdapter(model_info, api_key)

def create_openai_gpt35_turbo_adapter(api_key: Optional[str] = None) -> OpenAIAdapter:
    """GPT-3.5 Turbo 어댑터 생성"""
    from .ai_provider import MODEL_REGISTRY, ModelType
    
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
    
    model_info = MODEL_REGISTRY[ModelType.OPENAI_GPT35_TURBO]
    return OpenAIAdapter(model_info, api_key)
