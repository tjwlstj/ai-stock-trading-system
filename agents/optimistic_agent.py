"""
AI Stock Trading System - Optimistic Analyst Agent
낙관적 분석가 에이전트 - 성장 가능성과 긍정적 요소에 집중
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, PromptTemplates
from backend.database import DatabaseManager
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class OptimisticAnalyst(BaseAgent):
    """낙관적 분석가 에이전트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        낙관적 분석가 초기화
        
        Args:
            api_key: OpenAI API 키
        """
        super().__init__(
            agent_name="Optimistic Analyst",
            agent_type="optimistic",
            api_key=api_key,
            model="gpt-4o-mini"
        )
        self.db_manager = DatabaseManager()
    
    def get_system_prompt(self) -> str:
        """낙관적 분석가 시스템 프롬프트 반환"""
        return PromptTemplates.get_optimistic_analyst_prompt()
    
    def analyze_stock(self, symbol: str, stock_data: Dict[str, Any], 
                     market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        주식에 대한 낙관적 분석 수행
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            market_context: 시장 컨텍스트 (선택사항)
            
        Returns:
            분석 결과 딕셔너리
        """
        logger.info(f"[{self.agent_name}] {symbol} 낙관적 분석 시작")
        
        try:
            # 주식 데이터 포맷팅
            formatted_data = self.format_stock_data_for_prompt(symbol, stock_data)
            
            # 낙관적 분석 프롬프트 구성
            analysis_prompt = self._build_analysis_prompt(symbol, formatted_data, market_context)
            
            # AI API 호출
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": analysis_prompt}
            ]
            
            ai_response = self.call_openai_api(messages, temperature=0.7)
            
            # 응답 파싱
            analysis_result = self.parse_ai_response(ai_response)
            
            # 낙관적 관점 강화
            analysis_result = self._enhance_optimistic_perspective(analysis_result, stock_data)
            
            # 신뢰도 계산
            analysis_result['confidence'] = self.calculate_confidence_score(analysis_result)
            
            # 메타데이터 추가
            analysis_result.update({
                'agent_name': self.agent_name,
                'agent_type': self.agent_type,
                'symbol': symbol,
                'analysis_timestamp': self._get_timestamp(),
                'market_sentiment': 'BULLISH'
            })
            
            # 분석 결과 로깅
            self.log_analysis(symbol, analysis_result)
            
            # 데이터베이스에 저장
            self._save_analysis_result(symbol, analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] {symbol} 분석 중 오류: {str(e)}")
            return self._create_error_result(symbol, str(e))
    
    def _build_analysis_prompt(self, symbol: str, stock_data: str, 
                             market_context: Dict[str, Any] = None) -> str:
        """
        낙관적 분석을 위한 프롬프트 구성
        
        Args:
            symbol: 주식 심볼
            stock_data: 포맷팅된 주식 데이터
            market_context: 시장 컨텍스트
            
        Returns:
            분석 프롬프트
        """
        prompt = f"""
Please analyze {symbol} from an optimistic, growth-focused perspective.

{stock_data}

Focus on these positive aspects:
1. Growth potential and market opportunities
2. Competitive advantages and market position
3. Innovation and technological leadership
4. Strong financial fundamentals and cash flow
5. Positive market trends and momentum
6. Expansion opportunities and new markets
7. Management quality and strategic vision

"""
        
        if market_context:
            prompt += f"""
Market Context:
- Overall market sentiment: {market_context.get('sentiment', 'NEUTRAL')}
- Sector performance: {market_context.get('sector_performance', 'N/A')}
- Economic indicators: {market_context.get('economic_indicators', 'N/A')}

"""
        
        prompt += """
Provide a comprehensive bullish analysis focusing on:
- Why this stock has strong upside potential
- Key growth catalysts and positive developments
- Technical indicators showing strength
- Long-term investment thesis
- Specific price targets and timeline

Remember to maintain optimism while being realistic about the analysis.
"""
        
        return prompt
    
    def _enhance_optimistic_perspective(self, analysis_result: Dict[str, Any], 
                                      stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        낙관적 관점을 강화하여 분석 결과 개선
        
        Args:
            analysis_result: 기본 분석 결과
            stock_data: 주식 데이터
            
        Returns:
            강화된 분석 결과
        """
        # 기본 추천이 HOLD인 경우 BUY로 상향 조정 고려
        if analysis_result.get('recommendation') == 'HOLD':
            recent_prices = stock_data.get('recent_prices', [])
            if recent_prices and len(recent_prices) >= 2:
                # 최근 상승 추세인 경우 BUY로 조정
                current_price = recent_prices[0].get('close_price', 0)
                prev_price = recent_prices[1].get('close_price', 0)
                
                if current_price > prev_price * 1.02:  # 2% 이상 상승
                    analysis_result['recommendation'] = 'BUY'
                    analysis_result['confidence'] = min(1.0, analysis_result.get('confidence', 0.5) + 0.1)
                    
                    reasoning = analysis_result.get('reasoning', '')
                    analysis_result['reasoning'] = f"Recent upward momentum supports bullish outlook. {reasoning}"
        
        # 목표 가격을 현재 가격보다 높게 설정
        recent_prices = stock_data.get('recent_prices', [])
        if recent_prices:
            current_price = recent_prices[0].get('close_price', 0)
            target_price = analysis_result.get('target_price', 0)
            
            if target_price <= current_price:
                # 낙관적 목표가 설정 (5-15% 상승)
                optimistic_target = current_price * (1.05 + (analysis_result.get('confidence', 0.5) * 0.1))
                analysis_result['target_price'] = round(optimistic_target, 2)
        
        # 긍정적 키워드 추가
        positive_keywords = [
            "growth potential", "market leadership", "innovation", "strong fundamentals",
            "competitive advantage", "expansion opportunity", "bullish momentum"
        ]
        
        reasoning = analysis_result.get('reasoning', '')
        if not any(keyword in reasoning.lower() for keyword in positive_keywords):
            analysis_result['reasoning'] = f"Strong growth potential identified. {reasoning}"
        
        return analysis_result
    
    def get_bullish_signals(self, symbol: str) -> List[str]:
        """
        특정 종목의 강세 신호 식별
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            강세 신호 리스트
        """
        signals = []
        
        try:
            # 최근 가격 데이터 조회
            recent_data = self.db_manager.get_stock_price_data(symbol)
            
            if not recent_data.empty and len(recent_data) >= 5:
                # 상승 추세 확인
                recent_closes = recent_data['close_price'].tail(5)
                if recent_closes.iloc[-1] > recent_closes.iloc[0]:
                    signals.append("Upward price trend over last 5 days")
                
                # 거래량 증가 확인
                recent_volumes = recent_data['volume'].tail(5)
                avg_volume = recent_volumes.mean()
                latest_volume = recent_volumes.iloc[-1]
                
                if latest_volume > avg_volume * 1.2:
                    signals.append("Above-average trading volume indicating interest")
                
                # 기술적 지표 (간단한 이동평균)
                if len(recent_data) >= 20:
                    ma_20 = recent_data['close_price'].tail(20).mean()
                    current_price = recent_data['close_price'].iloc[-1]
                    
                    if current_price > ma_20:
                        signals.append("Price above 20-day moving average")
        
        except Exception as e:
            logger.error(f"강세 신호 분석 중 오류: {str(e)}")
        
        return signals
    
    def _save_analysis_result(self, symbol: str, analysis_result: Dict[str, Any]):
        """분석 결과를 데이터베이스에 저장"""
        try:
            self.db_manager.execute_update(
                """INSERT INTO analysis_results 
                   (symbol, agent_type, analysis_type, result_data, confidence_score)
                   VALUES (?, ?, ?, ?, ?)""",
                (symbol, self.agent_type, 'stock_analysis', 
                 str(analysis_result), analysis_result.get('confidence', 0.5))
            )
        except Exception as e:
            logger.error(f"분석 결과 저장 실패: {str(e)}")
    
    def _create_error_result(self, symbol: str, error_msg: str) -> Dict[str, Any]:
        """오류 발생 시 기본 결과 생성"""
        return {
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'symbol': symbol,
            'recommendation': 'HOLD',
            'confidence': 0.3,
            'reasoning': f'Analysis failed due to error: {error_msg}',
            'target_price': 0.0,
            'risk_level': 'UNKNOWN',
            'error': True,
            'analysis_timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()

# 테스트 및 예제 실행
if __name__ == "__main__":
    print("=== AI Stock Trading System - Optimistic Analyst ===")
    
    # 낙관적 분석가 생성
    analyst = OptimisticAnalyst()
    
    # 테스트 주식 데이터
    test_stock_data = {
        'recent_prices': [
            {'date': '2025-09-25', 'close_price': 256.87, 'volume': 50836929},
            {'date': '2025-09-24', 'close_price': 252.31, 'volume': 42303700},
            {'date': '2025-09-23', 'close_price': 254.43, 'volume': 60275200},
            {'date': '2025-09-22', 'close_price': 256.08, 'volume': 105517400},
            {'date': '2025-09-21', 'close_price': 250.15, 'volume': 45123800}
        ]
    }
    
    # 시장 컨텍스트
    market_context = {
        'sentiment': 'POSITIVE',
        'sector_performance': 'OUTPERFORMING',
        'economic_indicators': 'STABLE'
    }
    
    # AAPL 분석 수행
    print("🔍 AAPL 낙관적 분석 수행 중...")
    analysis_result = analyst.analyze_stock('AAPL', test_stock_data, market_context)
    
    # 결과 출력
    print(f"\n📊 분석 결과:")
    print(f"  추천: {analysis_result.get('recommendation', 'N/A')}")
    print(f"  신뢰도: {analysis_result.get('confidence', 0):.2f}")
    print(f"  목표가: ${analysis_result.get('target_price', 0):.2f}")
    print(f"  리스크: {analysis_result.get('risk_level', 'N/A')}")
    print(f"  근거: {analysis_result.get('reasoning', 'N/A')[:150]}...")
    
    # 강세 신호 분석
    print(f"\n📈 강세 신호 분석:")
    bullish_signals = analyst.get_bullish_signals('AAPL')
    if bullish_signals:
        for i, signal in enumerate(bullish_signals, 1):
            print(f"  {i}. {signal}")
    else:
        print("  현재 식별된 강세 신호가 없습니다.")
    
    print(f"\n✅ 낙관적 분석가 테스트 완료")
