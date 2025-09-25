"""
AI Stock Trading System - Base Agent Module
AI 에이전트 기본 클래스 및 공통 기능
"""

import os
import json
import openai
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """AI 에이전트 기본 클래스"""
    
    def __init__(self, agent_name: str, agent_type: str, 
                 api_key: Optional[str] = None, model: str = "gpt-4.1-mini"):
        """
        기본 에이전트 초기화
        
        Args:
            agent_name: 에이전트 이름
            agent_type: 에이전트 타입 (optimistic, pessimistic, fundamental, technical, risk)
            api_key: OpenAI API 키
            model: 사용할 GPT 모델
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.model = model
        
        # OpenAI API 설정
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.ai_available = True
            logger.info(f"{agent_name} 에이전트 초기화 완료 (AI 사용 가능)")
        else:
            self.ai_available = False
            logger.warning(f"{agent_name} 에이전트 초기화 (AI 사용 불가 - 시뮬레이션 모드)")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """에이전트별 시스템 프롬프트 반환"""
        pass
    
    @abstractmethod
    def analyze_stock(self, symbol: str, stock_data: Dict[str, Any], 
                     market_context: Dict[str, Any]) -> Dict[str, Any]:
        """주식 분석 수행"""
        pass
    
    def call_openai_api(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.7) -> Optional[str]:
        """
        OpenAI API 호출
        
        Args:
            messages: 메시지 리스트
            temperature: 창의성 수준 (0.0 ~ 1.0)
            
        Returns:
            AI 응답 텍스트
        """
        if not self.ai_available:
            return self._simulate_ai_response(messages)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API 호출 실패: {str(e)}")
            return self._simulate_ai_response(messages)
    
    def _simulate_ai_response(self, messages: List[Dict[str, str]]) -> str:
        """AI 응답 시뮬레이션 (API 키가 없는 경우)"""
        user_message = messages[-1].get('content', '')
        
        # 간단한 키워드 기반 시뮬레이션
        if 'AAPL' in user_message or 'Apple' in user_message:
            if self.agent_type == 'optimistic':
                return json.dumps({
                    "recommendation": "BUY",
                    "confidence": 0.75,
                    "reasoning": "Apple shows strong fundamentals with consistent innovation and market leadership in technology sector.",
                    "target_price": 280.0,
                    "risk_level": "MEDIUM"
                })
            elif self.agent_type == 'pessimistic':
                return json.dumps({
                    "recommendation": "HOLD",
                    "confidence": 0.65,
                    "reasoning": "While Apple is strong, current market conditions and high valuation suggest caution.",
                    "target_price": 240.0,
                    "risk_level": "MEDIUM-HIGH"
                })
        
        # 기본 시뮬레이션 응답
        return json.dumps({
            "recommendation": "HOLD",
            "confidence": 0.5,
            "reasoning": f"Simulated response from {self.agent_name} - API key required for actual AI analysis",
            "target_price": 0.0,
            "risk_level": "UNKNOWN"
        })
    
    def format_stock_data_for_prompt(self, symbol: str, stock_data: Dict[str, Any]) -> str:
        """
        주식 데이터를 프롬프트용으로 포맷팅
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            
        Returns:
            포맷팅된 데이터 문자열
        """
        if not stock_data:
            return f"No data available for {symbol}"
        
        # 최근 가격 정보 추출
        recent_prices = stock_data.get('recent_prices', [])
        if recent_prices:
            latest = recent_prices[0]
            formatted_data = f"""
Stock: {symbol}
Current Price: ${latest.get('close_price', 0):.2f}
Volume: {latest.get('volume', 0):,}
Date: {latest.get('date', 'N/A')}

Recent Price Trend (Last 5 days):
"""
            for i, price_data in enumerate(recent_prices[:5]):
                formatted_data += f"Day {i+1}: ${price_data.get('close_price', 0):.2f} (Vol: {price_data.get('volume', 0):,})\n"
        else:
            formatted_data = f"Stock: {symbol}\nLimited data available"
        
        return formatted_data
    
    def parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        AI 응답을 파싱하여 구조화된 데이터로 변환
        
        Args:
            response: AI 응답 텍스트
            
        Returns:
            파싱된 분석 결과
        """
        try:
            # JSON 형태로 응답이 온 경우
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # 텍스트 응답을 구조화
            result = {
                'recommendation': 'HOLD',
                'confidence': 0.5,
                'reasoning': response,
                'target_price': 0.0,
                'risk_level': 'MEDIUM',
                'raw_response': response
            }
            
            # 키워드 기반 추천 추출
            response_lower = response.lower()
            if 'buy' in response_lower or 'bullish' in response_lower:
                result['recommendation'] = 'BUY'
                result['confidence'] = 0.7
            elif 'sell' in response_lower or 'bearish' in response_lower:
                result['recommendation'] = 'SELL'
                result['confidence'] = 0.7
            
            return result
            
        except json.JSONDecodeError:
            logger.warning(f"AI 응답 파싱 실패: {response[:100]}...")
            return {
                'recommendation': 'HOLD',
                'confidence': 0.3,
                'reasoning': 'Failed to parse AI response',
                'target_price': 0.0,
                'risk_level': 'UNKNOWN',
                'raw_response': response
            }
    
    def calculate_confidence_score(self, analysis_result: Dict[str, Any]) -> float:
        """
        분석 결과의 신뢰도 점수 계산
        
        Args:
            analysis_result: 분석 결과
            
        Returns:
            신뢰도 점수 (0.0 ~ 1.0)
        """
        base_confidence = analysis_result.get('confidence', 0.5)
        
        # 추가 요소들을 고려한 신뢰도 조정
        adjustments = 0.0
        
        # 추천의 명확성
        recommendation = analysis_result.get('recommendation', 'HOLD')
        if recommendation in ['BUY', 'SELL']:
            adjustments += 0.1
        
        # 근거의 길이 (더 자세한 분석일수록 신뢰도 증가)
        reasoning = analysis_result.get('reasoning', '')
        if len(reasoning) > 100:
            adjustments += 0.1
        
        # 목표 가격 제시 여부
        target_price = analysis_result.get('target_price', 0)
        if target_price > 0:
            adjustments += 0.05
        
        # 최종 신뢰도 계산 (최대 1.0)
        final_confidence = min(1.0, base_confidence + adjustments)
        
        return round(final_confidence, 2)
    
    def log_analysis(self, symbol: str, analysis_result: Dict[str, Any]):
        """
        분석 결과 로깅
        
        Args:
            symbol: 주식 심볼
            analysis_result: 분석 결과
        """
        logger.info(f"[{self.agent_name}] {symbol} 분석 완료")
        logger.info(f"  추천: {analysis_result.get('recommendation', 'N/A')}")
        logger.info(f"  신뢰도: {analysis_result.get('confidence', 0):.2f}")
        logger.info(f"  근거: {analysis_result.get('reasoning', 'N/A')[:100]}...")

class PromptTemplates:
    """AI 에이전트용 프롬프트 템플릿"""
    
    @staticmethod
    def get_optimistic_analyst_prompt() -> str:
        """낙관적 분석가 프롬프트"""
        return """
You are an optimistic stock analyst who focuses on growth potential and positive market opportunities. 
Your role is to identify bullish signals, growth catalysts, and upside potential in stocks.

Key characteristics:
- Focus on positive news, growth trends, and market opportunities
- Emphasize innovation, market expansion, and competitive advantages
- Look for technical breakouts and momentum indicators
- Consider long-term growth potential over short-term volatility

When analyzing a stock, provide:
1. Recommendation (BUY/HOLD/SELL)
2. Confidence level (0.0 to 1.0)
3. Detailed reasoning focusing on positive aspects
4. Target price estimate
5. Risk assessment

Respond in JSON format with these fields:
{
  "recommendation": "BUY/HOLD/SELL",
  "confidence": 0.0-1.0,
  "reasoning": "detailed analysis",
  "target_price": number,
  "risk_level": "LOW/MEDIUM/HIGH"
}
"""
    
    @staticmethod
    def get_pessimistic_analyst_prompt() -> str:
        """비관적 분석가 프롬프트"""
        return """
You are a pessimistic stock analyst who focuses on risks, challenges, and potential downsides. 
Your role is to identify bearish signals, market risks, and downside potential in stocks.

Key characteristics:
- Focus on negative news, market risks, and potential challenges
- Emphasize valuation concerns, competitive threats, and market headwinds
- Look for technical breakdowns and weakness indicators
- Consider short-term volatility and market corrections

When analyzing a stock, provide:
1. Recommendation (BUY/HOLD/SELL)
2. Confidence level (0.0 to 1.0)
3. Detailed reasoning focusing on risks and challenges
4. Target price estimate (often lower than current price)
5. Risk assessment

Respond in JSON format with these fields:
{
  "recommendation": "BUY/HOLD/SELL",
  "confidence": 0.0-1.0,
  "reasoning": "detailed analysis focusing on risks",
  "target_price": number,
  "risk_level": "LOW/MEDIUM/HIGH"
}
"""
    
    @staticmethod
    def get_fundamental_analyst_prompt() -> str:
        """기본적 분석가 프롬프트"""
        return """
You are a fundamental analyst who focuses on company financials, business model, and intrinsic value.
Your role is to evaluate stocks based on financial metrics, business fundamentals, and long-term value.

Key characteristics:
- Analyze financial statements, ratios, and business metrics
- Focus on revenue growth, profitability, and cash flow
- Consider industry position, competitive moats, and management quality
- Evaluate fair value based on fundamental analysis

When analyzing a stock, provide:
1. Recommendation based on fundamental value
2. Confidence level in the analysis
3. Detailed reasoning based on financial and business fundamentals
4. Fair value estimate
5. Risk assessment based on business fundamentals

Respond in JSON format with these fields:
{
  "recommendation": "BUY/HOLD/SELL",
  "confidence": 0.0-1.0,
  "reasoning": "fundamental analysis details",
  "target_price": number,
  "risk_level": "LOW/MEDIUM/HIGH"
}
"""
    
    @staticmethod
    def get_risk_manager_prompt() -> str:
        """리스크 매니저 프롬프트"""
        return """
You are a risk manager who evaluates portfolio risk and provides risk management recommendations.
Your role is to assess various risk factors and suggest appropriate risk mitigation strategies.

Key characteristics:
- Analyze market risk, volatility, and correlation factors
- Consider position sizing and portfolio diversification
- Evaluate stop-loss levels and risk-reward ratios
- Focus on capital preservation and risk-adjusted returns

When analyzing investment recommendations, provide:
1. Overall risk assessment
2. Recommended position size (as % of portfolio)
3. Stop-loss recommendations
4. Risk mitigation strategies
5. Portfolio impact analysis

Respond in JSON format with these fields:
{
  "risk_assessment": "LOW/MEDIUM/HIGH",
  "position_size_percent": number,
  "stop_loss_level": number,
  "risk_factors": ["list of key risks"],
  "mitigation_strategies": ["list of strategies"]
}
"""

# 테스트 및 예제 실행
if __name__ == "__main__":
    print("=== AI Stock Trading System - Base Agent ===")
    
    # 기본 에이전트 테스트 (시뮬레이션 모드)
    class TestAgent(BaseAgent):
        def get_system_prompt(self):
            return "You are a test agent."
        
        def analyze_stock(self, symbol, stock_data, market_context):
            return {"test": "analysis"}
    
    # 테스트 에이전트 생성
    test_agent = TestAgent("TestAgent", "test")
    
    # 시뮬레이션 응답 테스트
    test_messages = [
        {"role": "system", "content": "You are a stock analyst."},
        {"role": "user", "content": "Analyze AAPL stock"}
    ]
    
    response = test_agent.call_openai_api(test_messages)
    print(f"✅ AI 응답 테스트: {response[:100]}...")
    
    # 응답 파싱 테스트
    parsed = test_agent.parse_ai_response(response)
    print(f"✅ 응답 파싱 테스트: {parsed.get('recommendation', 'N/A')}")
    
    # 신뢰도 계산 테스트
    confidence = test_agent.calculate_confidence_score(parsed)
    print(f"✅ 신뢰도 계산 테스트: {confidence}")
    
    print(f"\n💡 OpenAI API 키가 설정되면 실제 AI 분석이 가능합니다.")
    print(f"현재 모드: {'AI 사용 가능' if test_agent.ai_available else '시뮬레이션'}")
