"""
Google Gemini API 어댑터
Google의 Gemini 모델들을 위한 구체적인 구현체
"""

import os
import time
import re
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .ai_provider import (
    AIProvider, AnalysisRequest, AnalysisResponse, ModelInfo,
    AIProviderError, ModelNotAvailableError, APIQuotaExceededError,
    InvalidRequestError
)

class GeminiAdapter(AIProvider):
    """Google Gemini API 어댑터"""
    
    def _initialize_client(self):
        """Gemini 클라이언트 초기화"""
        if not GEMINI_AVAILABLE:
            raise AIProviderError("Google Generative AI library not installed. Install with: pip install google-generativeai")
        
        try:
            genai.configure(api_key=self.api_key)
            
            # 모델 초기화
            self.model = genai.GenerativeModel(
                model_name=self.model_info.model_id,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1000,
                ),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
        except Exception as e:
            raise AIProviderError(f"Failed to initialize Gemini client: {e}")
    
    def generate_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """주식 분석 생성"""
        start_time = time.time()
        
        try:
            # 프롬프트 구성
            full_prompt = self._build_full_prompt(request.prompt, request.stock_data)
            
            # 생성 설정 업데이트
            generation_config = genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            )
            
            # API 호출
            if request.stream:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                    stream=True
                )
                content = self._handle_streaming_response(response)
            else:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                content = response.text
            
            # 토큰 사용량 추정 (Gemini는 정확한 토큰 수를 제공하지 않음)
            tokens_used = self._estimate_tokens(full_prompt, content)
            
            # 비용 계산
            cost_estimate = self._calculate_cost_estimate(tokens_used)
            
            processing_time = time.time() - start_time
            
            return AnalysisResponse(
                content=content,
                model_used=self.model_info.model_id,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                processing_time=processing_time,
                confidence_score=self._extract_confidence_score(content),
                metadata={
                    "provider": "google",
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "model_version": self.model_info.model_id
                }
            )
            
        except Exception as e:
            self._handle_api_error(e)
    
    def estimate_cost(self, prompt: str, max_tokens: int = 1000) -> float:
        """API 호출 비용 추정"""
        input_tokens = self.count_tokens(prompt)
        output_tokens = max_tokens
        
        input_cost = input_tokens * self.model_info.cost_per_input_token
        output_cost = output_tokens * self.model_info.cost_per_output_token
        
        return input_cost + output_cost
    
    def count_tokens(self, text: str) -> int:
        """텍스트의 토큰 수 계산 (추정)"""
        try:
            # Gemini의 토큰 계산 방식 (대략적)
            # 한국어/영어 혼합 텍스트의 경우 대략 1토큰 = 3-4자
            return len(text) // 3
        except Exception:
            # 더 보수적인 추정
            return len(text) // 2
    
    def _build_full_prompt(self, prompt: str, stock_data: Dict[str, Any]) -> str:
        """전체 프롬프트 구성"""
        system_context = """You are a professional stock market analyst with expertise in financial analysis and investment recommendations.

Your role is to provide comprehensive, data-driven analysis of stocks based on the provided market data and context.
Always structure your response with clear reasoning, risk assessment, and actionable insights.

Response format should include:
1. Analysis summary
2. Key findings  
3. Risk factors
4. Recommendation (BUY/HOLD/SELL)
5. Confidence level (0-100%)
6. Target price (if applicable)

Be objective, thorough, and professional in your analysis.

"""
        
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
        
        user_request = f"""
Analysis Request:
{prompt}

Please provide a comprehensive analysis based on the above information.
"""
        
        return system_context + stock_info + user_request
    
    def _handle_streaming_response(self, response) -> str:
        """스트리밍 응답 처리"""
        content = ""
        try:
            for chunk in response:
                if chunk.text:
                    content += chunk.text
        except Exception as e:
            raise AIProviderError(f"Error processing streaming response: {e}")
        
        return content
    
    def _estimate_tokens(self, input_text: str, output_text: str) -> int:
        """토큰 사용량 추정"""
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        return input_tokens + output_tokens
    
    def _calculate_cost_estimate(self, total_tokens: int) -> float:
        """비용 추정 (입력:출력 = 7:3 비율로 가정)"""
        input_tokens = int(total_tokens * 0.7)
        output_tokens = int(total_tokens * 0.3)
        
        input_cost = input_tokens * self.model_info.cost_per_input_token
        output_cost = output_tokens * self.model_info.cost_per_output_token
        
        return input_cost + output_cost
    
    def _extract_confidence_score(self, content: str) -> Optional[float]:
        """응답에서 신뢰도 점수 추출"""
        patterns = [
            r'confidence[:\s]+(\d+)%',
            r'신뢰도[:\s]+(\d+)%',
            r'확신도[:\s]+(\d+)%',
            r'confidence[:\s]+(\d+)/100',
            r'신뢰도[:\s]+(\d+)/100'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content.lower())
            if match:
                score = float(match.group(1))
                return score / 100.0 if score > 1 else score
        
        return None
    
    def _handle_api_error(self, error: Exception):
        """API 오류 처리"""
        error_message = str(error).lower()
        
        if "quota" in error_message or "rate limit" in error_message:
            raise APIQuotaExceededError(f"Gemini API quota exceeded: {error}")
        elif "invalid" in error_message or "bad request" in error_message:
            raise InvalidRequestError(f"Invalid request to Gemini API: {error}")
        elif "model" in error_message and ("not found" in error_message or "unavailable" in error_message):
            raise ModelNotAvailableError(f"Gemini model not available: {error}")
        elif "safety" in error_message:
            raise InvalidRequestError(f"Content blocked by Gemini safety filters: {error}")
        else:
            raise AIProviderError(f"Gemini API error: {error}")

# 편의 함수들
def create_gemini_pro_adapter(api_key: Optional[str] = None) -> GeminiAdapter:
    """Gemini 1.5 Pro 어댑터 생성"""
    from .ai_provider import MODEL_REGISTRY, ModelType
    
    if api_key is None:
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required")
    
    model_info = MODEL_REGISTRY[ModelType.GOOGLE_GEMINI_PRO]
    return GeminiAdapter(model_info, api_key)

def create_gemini_flash_adapter(api_key: Optional[str] = None) -> GeminiAdapter:
    """Gemini 1.5 Flash 어댑터 생성"""
    from .ai_provider import MODEL_REGISTRY, ModelType
    
    if api_key is None:
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Google API key is required")
    
    model_info = MODEL_REGISTRY[ModelType.GOOGLE_GEMINI_FLASH]
    return GeminiAdapter(model_info, api_key)

def is_gemini_available() -> bool:
    """Gemini 사용 가능 여부 확인"""
    return GEMINI_AVAILABLE
