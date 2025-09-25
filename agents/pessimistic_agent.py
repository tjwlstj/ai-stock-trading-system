"""
AI Stock Trading System - Pessimistic Analyst Agent
비관적 분석가 에이전트 - 리스크와 하락 요인에 집중
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, PromptTemplates
from backend.database import DatabaseManager
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class PessimisticAnalyst(BaseAgent):
    """비관적 분석가 에이전트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        비관적 분석가 초기화
        
        Args:
            api_key: OpenAI API 키
        """
        super().__init__(
            agent_name="Pessimistic Analyst",
            agent_type="pessimistic",
            api_key=api_key,
            model="gpt-4o-mini"
        )
        self.db_manager = DatabaseManager()
    
    def get_system_prompt(self) -> str:
        """비관적 분석가 시스템 프롬프트 반환"""
        return PromptTemplates.get_pessimistic_analyst_prompt()
    
    def analyze_stock(self, symbol: str, stock_data: Dict[str, Any], 
                     market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        주식에 대한 비관적 분석 수행
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            market_context: 시장 컨텍스트 (선택사항)
            
        Returns:
            분석 결과 딕셔너리
        """
        logger.info(f"[{self.agent_name}] {symbol} 비관적 분석 시작")
        
        try:
            # 주식 데이터 포맷팅
            formatted_data = self.format_stock_data_for_prompt(symbol, stock_data)
            
            # 비관적 분석 프롬프트 구성
            analysis_prompt = self._build_analysis_prompt(symbol, formatted_data, market_context)
            
            # AI API 호출
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": analysis_prompt}
            ]
            
            ai_response = self.call_openai_api(messages, temperature=0.7)
            
            # 응답 파싱
            analysis_result = self.parse_ai_response(ai_response)
            
            # 비관적 관점 강화
            analysis_result = self._enhance_pessimistic_perspective(analysis_result, stock_data)
            
            # 신뢰도 계산
            analysis_result['confidence'] = self.calculate_confidence_score(analysis_result)
            
            # 메타데이터 추가
            analysis_result.update({
                'agent_name': self.agent_name,
                'agent_type': self.agent_type,
                'symbol': symbol,
                'analysis_timestamp': self._get_timestamp(),
                'market_sentiment': 'BEARISH'
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
        비관적 분석을 위한 프롬프트 구성
        
        Args:
            symbol: 주식 심볼
            stock_data: 포맷팅된 주식 데이터
            market_context: 시장 컨텍스트
            
        Returns:
            분석 프롬프트
        """
        prompt = f"""
Please analyze {symbol} from a pessimistic, risk-focused perspective.

{stock_data}

Focus on these risk factors and challenges:
1. Market risks and potential downside scenarios
2. Competitive threats and market share erosion
3. Valuation concerns and overpricing risks
4. Economic headwinds and sector challenges
5. Technical weakness and bearish indicators
6. Regulatory risks and compliance issues
7. Management concerns and strategic missteps
8. Financial vulnerabilities and cash flow issues

"""
        
        if market_context:
            prompt += f"""
Market Context:
- Overall market sentiment: {market_context.get('sentiment', 'NEUTRAL')}
- Sector performance: {market_context.get('sector_performance', 'N/A')}
- Economic indicators: {market_context.get('economic_indicators', 'N/A')}

"""
        
        prompt += """
Provide a comprehensive bearish analysis focusing on:
- Why this stock faces significant downside risks
- Key risk factors and negative developments
- Technical indicators showing weakness
- Potential price decline scenarios
- Specific downside price targets and timeline
- Risk mitigation strategies for investors

Remember to be thorough in identifying risks while maintaining analytical objectivity.
"""
        
        return prompt
    
    def _enhance_pessimistic_perspective(self, analysis_result: Dict[str, Any], 
                                       stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        비관적 관점을 강화하여 분석 결과 개선
        
        Args:
            analysis_result: 기본 분석 결과
            stock_data: 주식 데이터
            
        Returns:
            강화된 분석 결과
        """
        # 기본 추천이 BUY인 경우 HOLD로 하향 조정 고려
        if analysis_result.get('recommendation') == 'BUY':
            recent_prices = stock_data.get('recent_prices', [])
            if recent_prices and len(recent_prices) >= 2:
                # 최근 하락 추세인 경우 HOLD 또는 SELL로 조정
                current_price = recent_prices[0].get('close_price', 0)
                prev_price = recent_prices[1].get('close_price', 0)
                
                if current_price < prev_price * 0.98:  # 2% 이상 하락
                    analysis_result['recommendation'] = 'SELL' if current_price < prev_price * 0.95 else 'HOLD'
                    analysis_result['confidence'] = min(1.0, analysis_result.get('confidence', 0.5) + 0.1)
                    
                    reasoning = analysis_result.get('reasoning', '')
                    analysis_result['reasoning'] = f"Recent downward momentum raises concerns. {reasoning}"
        
        # 목표 가격을 현재 가격보다 낮게 설정
        recent_prices = stock_data.get('recent_prices', [])
        if recent_prices:
            current_price = recent_prices[0].get('close_price', 0)
            target_price = analysis_result.get('target_price', 0)
            
            if target_price >= current_price:
                # 비관적 목표가 설정 (5-15% 하락)
                pessimistic_target = current_price * (0.95 - (analysis_result.get('confidence', 0.5) * 0.1))
                analysis_result['target_price'] = round(pessimistic_target, 2)
        
        # 리스크 레벨 상향 조정
        current_risk = analysis_result.get('risk_level', 'MEDIUM')
        if current_risk == 'LOW':
            analysis_result['risk_level'] = 'MEDIUM'
        elif current_risk == 'MEDIUM':
            analysis_result['risk_level'] = 'HIGH'
        
        # 부정적 키워드 추가
        negative_keywords = [
            "downside risk", "market volatility", "competitive pressure", "valuation concern",
            "bearish signal", "potential decline", "risk factor"
        ]
        
        reasoning = analysis_result.get('reasoning', '')
        if not any(keyword in reasoning.lower() for keyword in negative_keywords):
            analysis_result['reasoning'] = f"Significant downside risks identified. {reasoning}"
        
        return analysis_result
    
    def get_bearish_signals(self, symbol: str) -> List[str]:
        """
        특정 종목의 약세 신호 식별
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            약세 신호 리스트
        """
        signals = []
        
        try:
            # 최근 가격 데이터 조회
            recent_data = self.db_manager.get_stock_price_data(symbol)
            
            if not recent_data.empty and len(recent_data) >= 5:
                # 하락 추세 확인
                recent_closes = recent_data['close_price'].tail(5)
                if recent_closes.iloc[-1] < recent_closes.iloc[0]:
                    decline_pct = ((recent_closes.iloc[0] - recent_closes.iloc[-1]) / recent_closes.iloc[0]) * 100
                    signals.append(f"Downward price trend: {decline_pct:.1f}% decline over last 5 days")
                
                # 거래량 감소 확인
                recent_volumes = recent_data['volume'].tail(5)
                avg_volume = recent_volumes.mean()
                latest_volume = recent_volumes.iloc[-1]
                
                if latest_volume < avg_volume * 0.8:
                    signals.append("Below-average trading volume indicating weak interest")
                
                # 기술적 지표 (간단한 이동평균)
                if len(recent_data) >= 20:
                    ma_20 = recent_data['close_price'].tail(20).mean()
                    current_price = recent_data['close_price'].iloc[-1]
                    
                    if current_price < ma_20:
                        signals.append("Price below 20-day moving average")
                
                # 변동성 증가 확인
                if len(recent_data) >= 10:
                    recent_returns = recent_data['close_price'].pct_change().tail(10)
                    volatility = recent_returns.std()
                    
                    if volatility > 0.03:  # 3% 이상의 일일 변동성
                        signals.append("High volatility indicating market uncertainty")
        
        except Exception as e:
            logger.error(f"약세 신호 분석 중 오류: {str(e)}")
        
        return signals
    
    def assess_market_risks(self, symbol: str, market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        시장 리스크 평가
        
        Args:
            symbol: 주식 심볼
            market_context: 시장 컨텍스트
            
        Returns:
            리스크 평가 결과
        """
        risks = {
            'overall_risk_level': 'MEDIUM',
            'risk_factors': [],
            'mitigation_strategies': []
        }
        
        try:
            # 약세 신호 기반 리스크 평가
            bearish_signals = self.get_bearish_signals(symbol)
            
            if len(bearish_signals) >= 3:
                risks['overall_risk_level'] = 'HIGH'
                risks['risk_factors'].extend(bearish_signals)
            elif len(bearish_signals) >= 1:
                risks['overall_risk_level'] = 'MEDIUM-HIGH'
                risks['risk_factors'].extend(bearish_signals)
            
            # 시장 컨텍스트 기반 리스크
            if market_context:
                sentiment = market_context.get('sentiment', 'NEUTRAL')
                if sentiment in ['NEGATIVE', 'BEARISH']:
                    risks['risk_factors'].append("Negative overall market sentiment")
                    risks['overall_risk_level'] = 'HIGH'
                
                sector_performance = market_context.get('sector_performance', 'NEUTRAL')
                if sector_performance == 'UNDERPERFORMING':
                    risks['risk_factors'].append("Sector underperformance")
            
            # 리스크 완화 전략
            risks['mitigation_strategies'] = [
                "Consider position sizing to limit exposure",
                "Set stop-loss orders to protect capital",
                "Monitor key support levels closely",
                "Diversify across sectors and asset classes",
                "Consider hedging strategies if holding long positions"
            ]
            
        except Exception as e:
            logger.error(f"시장 리스크 평가 중 오류: {str(e)}")
            risks['error'] = str(e)
        
        return risks
    
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
            'risk_level': 'HIGH',  # 오류 시 높은 리스크로 설정
            'error': True,
            'analysis_timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()

# 테스트 및 예제 실행
if __name__ == "__main__":
    print("=== AI Stock Trading System - Pessimistic Analyst ===")
    
    # 비관적 분석가 생성
    analyst = PessimisticAnalyst()
    
    # 테스트 주식 데이터 (하락 추세)
    test_stock_data = {
        'recent_prices': [
            {'date': '2025-09-25', 'close_price': 245.50, 'volume': 35000000},  # 하락
            {'date': '2025-09-24', 'close_price': 248.75, 'volume': 28000000},  # 거래량 감소
            {'date': '2025-09-23', 'close_price': 252.10, 'volume': 32000000},
            {'date': '2025-09-22', 'close_price': 255.80, 'volume': 45000000},
            {'date': '2025-09-21', 'close_price': 258.30, 'volume': 50000000}
        ]
    }
    
    # 시장 컨텍스트 (부정적)
    market_context = {
        'sentiment': 'NEGATIVE',
        'sector_performance': 'UNDERPERFORMING',
        'economic_indicators': 'DECLINING'
    }
    
    # AAPL 분석 수행
    print("🔍 AAPL 비관적 분석 수행 중...")
    analysis_result = analyst.analyze_stock('AAPL', test_stock_data, market_context)
    
    # 결과 출력
    print(f"\n📊 분석 결과:")
    print(f"  추천: {analysis_result.get('recommendation', 'N/A')}")
    print(f"  신뢰도: {analysis_result.get('confidence', 0):.2f}")
    print(f"  목표가: ${analysis_result.get('target_price', 0):.2f}")
    print(f"  리스크: {analysis_result.get('risk_level', 'N/A')}")
    print(f"  근거: {analysis_result.get('reasoning', 'N/A')[:150]}...")
    
    # 약세 신호 분석
    print(f"\n📉 약세 신호 분석:")
    bearish_signals = analyst.get_bearish_signals('AAPL')
    if bearish_signals:
        for i, signal in enumerate(bearish_signals, 1):
            print(f"  {i}. {signal}")
    else:
        print("  현재 식별된 약세 신호가 없습니다.")
    
    # 시장 리스크 평가
    print(f"\n⚠️ 시장 리스크 평가:")
    risk_assessment = analyst.assess_market_risks('AAPL', market_context)
    print(f"  전체 리스크 레벨: {risk_assessment.get('overall_risk_level', 'N/A')}")
    print(f"  주요 리스크 요인: {len(risk_assessment.get('risk_factors', []))}개")
    
    print(f"\n✅ 비관적 분석가 테스트 완료")
