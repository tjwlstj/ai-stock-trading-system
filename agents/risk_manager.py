"""
AI Stock Trading System - Risk Manager Agent
리스크 관리 에이전트 - 포트폴리오 리스크 평가 및 관리
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, PromptTemplates
from backend.database import DatabaseManager
from typing import Dict, List, Optional, Any, Tuple
import logging
import math

logger = logging.getLogger(__name__)

class RiskManager(BaseAgent):
    """리스크 관리 에이전트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        리스크 매니저 초기화
        
        Args:
            api_key: OpenAI API 키
        """
        super().__init__(
            agent_name="Risk Manager",
            agent_type="risk",
            api_key=api_key,
            model="gpt-4o-mini"
        )
        self.db_manager = DatabaseManager()
    
    def get_system_prompt(self) -> str:
        """리스크 매니저 시스템 프롬프트 반환"""
        return PromptTemplates.get_risk_manager_prompt()
    
    def analyze_stock(self, symbol: str, stock_data: Dict[str, Any], 
                     market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        주식에 대한 리스크 분석 수행
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            market_context: 시장 컨텍스트 (선택사항)
            
        Returns:
            리스크 분석 결과 딕셔너리
        """
        logger.info(f"[{self.agent_name}] {symbol} 리스크 분석 시작")
        
        try:
            # 기본 리스크 메트릭 계산
            risk_metrics = self.calculate_risk_metrics(symbol, stock_data)
            
            # 포지션 사이징 계산
            position_sizing = self.calculate_position_sizing(symbol, stock_data, risk_metrics)
            
            # 스톱로스 레벨 계산
            stop_loss_levels = self.calculate_stop_loss_levels(symbol, stock_data)
            
            # AI 기반 리스크 분석
            ai_risk_analysis = self._perform_ai_risk_analysis(symbol, stock_data, market_context)
            
            # 종합 리스크 평가
            comprehensive_assessment = self._create_comprehensive_assessment(
                symbol, risk_metrics, position_sizing, stop_loss_levels, ai_risk_analysis
            )
            
            # 메타데이터 추가
            comprehensive_assessment.update({
                'agent_name': self.agent_name,
                'agent_type': self.agent_type,
                'symbol': symbol,
                'analysis_timestamp': self._get_timestamp()
            })
            
            # 분석 결과 로깅
            self.log_risk_analysis(symbol, comprehensive_assessment)
            
            # 데이터베이스에 저장
            self._save_analysis_result(symbol, comprehensive_assessment)
            
            return comprehensive_assessment
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] {symbol} 리스크 분석 중 오류: {str(e)}")
            return self._create_error_result(symbol, str(e))
    
    def calculate_risk_metrics(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        기본 리스크 메트릭 계산
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            
        Returns:
            리스크 메트릭 딕셔너리
        """
        metrics = {
            'volatility': 0.0,
            'max_drawdown': 0.0,
            'beta': 1.0,
            'var_95': 0.0,  # 95% VaR
            'sharpe_ratio': 0.0
        }
        
        try:
            recent_prices = stock_data.get('recent_prices', [])
            if len(recent_prices) < 10:
                return metrics
            
            # 가격 데이터를 리스트로 변환
            prices = [float(p.get('close_price', 0)) for p in recent_prices]
            prices.reverse()  # 시간순으로 정렬
            
            # 수익률 계산
            returns = []
            for i in range(1, len(prices)):
                if prices[i-1] > 0:
                    ret = (prices[i] - prices[i-1]) / prices[i-1]
                    returns.append(ret)
            
            if len(returns) < 5:
                return metrics
            
            # 변동성 계산 (연환산)
            import statistics
            daily_volatility = statistics.stdev(returns) if len(returns) > 1 else 0
            metrics['volatility'] = daily_volatility * math.sqrt(252)  # 연환산
            
            # 최대 낙폭 계산
            peak = prices[0]
            max_dd = 0
            for price in prices:
                if price > peak:
                    peak = price
                drawdown = (peak - price) / peak
                max_dd = max(max_dd, drawdown)
            
            metrics['max_drawdown'] = max_dd
            
            # VaR 95% 계산 (간단한 히스토리컬 방법)
            if len(returns) >= 20:
                sorted_returns = sorted(returns)
                var_index = int(len(sorted_returns) * 0.05)
                metrics['var_95'] = abs(sorted_returns[var_index])
            
            # 샤프 비율 계산 (무위험 수익률 2% 가정)
            avg_return = statistics.mean(returns) if returns else 0
            risk_free_rate = 0.02 / 252  # 일일 무위험 수익률
            excess_return = avg_return - risk_free_rate
            
            if daily_volatility > 0:
                metrics['sharpe_ratio'] = (excess_return / daily_volatility) * math.sqrt(252)
            
        except Exception as e:
            logger.error(f"리스크 메트릭 계산 중 오류: {str(e)}")
        
        return metrics
    
    def calculate_position_sizing(self, symbol: str, stock_data: Dict[str, Any], 
                                risk_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        포지션 사이징 계산
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            risk_metrics: 리스크 메트릭
            
        Returns:
            포지션 사이징 정보
        """
        sizing = {
            'recommended_position_percent': 5.0,  # 기본 5%
            'max_position_percent': 10.0,
            'risk_adjusted_size': 5.0,
            'kelly_criterion': 0.0
        }
        
        try:
            volatility = risk_metrics.get('volatility', 0.2)
            max_drawdown = risk_metrics.get('max_drawdown', 0.1)
            
            # 변동성 기반 포지션 사이징
            if volatility > 0:
                # 높은 변동성일수록 작은 포지션
                vol_adjusted_size = min(10.0, 20.0 / (volatility * 100))
                sizing['risk_adjusted_size'] = max(1.0, vol_adjusted_size)
            
            # 최대 낙폭 기반 조정
            if max_drawdown > 0.2:  # 20% 이상 낙폭
                sizing['risk_adjusted_size'] *= 0.7
            elif max_drawdown > 0.15:  # 15% 이상 낙폭
                sizing['risk_adjusted_size'] *= 0.85
            
            # 최종 추천 포지션 크기
            sizing['recommended_position_percent'] = round(sizing['risk_adjusted_size'], 1)
            
            # 최대 포지션 제한
            sizing['max_position_percent'] = min(15.0, sizing['recommended_position_percent'] * 2)
            
        except Exception as e:
            logger.error(f"포지션 사이징 계산 중 오류: {str(e)}")
        
        return sizing
    
    def calculate_stop_loss_levels(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        스톱로스 레벨 계산
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            
        Returns:
            스톱로스 레벨 정보
        """
        stop_loss = {
            'conservative_stop': 0.0,  # 5% 손실
            'moderate_stop': 0.0,      # 8% 손실
            'aggressive_stop': 0.0,    # 12% 손실
            'technical_stop': 0.0,     # 기술적 지지선
            'recommended_stop': 0.0
        }
        
        try:
            recent_prices = stock_data.get('recent_prices', [])
            if not recent_prices:
                return stop_loss
            
            current_price = float(recent_prices[0].get('close_price', 0))
            if current_price <= 0:
                return stop_loss
            
            # 고정 퍼센트 스톱로스
            stop_loss['conservative_stop'] = round(current_price * 0.95, 2)
            stop_loss['moderate_stop'] = round(current_price * 0.92, 2)
            stop_loss['aggressive_stop'] = round(current_price * 0.88, 2)
            
            # 기술적 지지선 계산 (최근 저점)
            if len(recent_prices) >= 10:
                recent_lows = [float(p.get('low_price', p.get('close_price', 0))) 
                             for p in recent_prices[:10]]
                min_low = min(recent_lows)
                
                # 최근 저점의 95% 수준을 기술적 스톱로스로 설정
                stop_loss['technical_stop'] = round(min_low * 0.95, 2)
            else:
                stop_loss['technical_stop'] = stop_loss['moderate_stop']
            
            # 추천 스톱로스 (기술적 스톱과 중간 스톱 중 더 가까운 것)
            tech_distance = abs(current_price - stop_loss['technical_stop']) / current_price
            mod_distance = abs(current_price - stop_loss['moderate_stop']) / current_price
            
            if tech_distance < mod_distance and tech_distance > 0.03:  # 최소 3% 거리
                stop_loss['recommended_stop'] = stop_loss['technical_stop']
            else:
                stop_loss['recommended_stop'] = stop_loss['moderate_stop']
            
        except Exception as e:
            logger.error(f"스톱로스 레벨 계산 중 오류: {str(e)}")
        
        return stop_loss
    
    def _perform_ai_risk_analysis(self, symbol: str, stock_data: Dict[str, Any], 
                                market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        AI 기반 리스크 분석 수행
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            market_context: 시장 컨텍스트
            
        Returns:
            AI 리스크 분석 결과
        """
        try:
            # 주식 데이터 포맷팅
            formatted_data = self.format_stock_data_for_prompt(symbol, stock_data)
            
            # 리스크 분석 프롬프트 구성
            risk_prompt = f"""
Analyze the risk profile for {symbol} and provide risk management recommendations.

{formatted_data}

Please evaluate:
1. Overall risk level (LOW/MEDIUM/HIGH)
2. Key risk factors and vulnerabilities
3. Recommended position size as percentage of portfolio
4. Stop-loss recommendations
5. Risk mitigation strategies
6. Portfolio diversification suggestions

Consider market volatility, liquidity, sector risks, and company-specific factors.
"""
            
            if market_context:
                risk_prompt += f"""
Market Context:
- Market sentiment: {market_context.get('sentiment', 'NEUTRAL')}
- Sector performance: {market_context.get('sector_performance', 'N/A')}
- Economic conditions: {market_context.get('economic_indicators', 'N/A')}
"""
            
            # AI API 호출
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": risk_prompt}
            ]
            
            ai_response = self.call_openai_api(messages, temperature=0.5)
            
            # 응답 파싱
            return self.parse_ai_response(ai_response)
            
        except Exception as e:
            logger.error(f"AI 리스크 분석 중 오류: {str(e)}")
            return {
                'risk_assessment': 'MEDIUM',
                'risk_factors': ['Analysis error occurred'],
                'mitigation_strategies': ['Manual review required']
            }
    
    def _create_comprehensive_assessment(self, symbol: str, risk_metrics: Dict[str, Any],
                                       position_sizing: Dict[str, Any], 
                                       stop_loss_levels: Dict[str, Any],
                                       ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        종합 리스크 평가 생성
        
        Args:
            symbol: 주식 심볼
            risk_metrics: 리스크 메트릭
            position_sizing: 포지션 사이징
            stop_loss_levels: 스톱로스 레벨
            ai_analysis: AI 분석 결과
            
        Returns:
            종합 리스크 평가
        """
        # 전체 리스크 레벨 결정
        volatility = risk_metrics.get('volatility', 0.2)
        max_drawdown = risk_metrics.get('max_drawdown', 0.1)
        
        if volatility > 0.4 or max_drawdown > 0.25:
            overall_risk = 'HIGH'
        elif volatility > 0.25 or max_drawdown > 0.15:
            overall_risk = 'MEDIUM-HIGH'
        elif volatility > 0.15 or max_drawdown > 0.1:
            overall_risk = 'MEDIUM'
        else:
            overall_risk = 'LOW-MEDIUM'
        
        # AI 분석 결과와 조합
        ai_risk = ai_analysis.get('risk_assessment', 'MEDIUM')
        if ai_risk == 'HIGH' or overall_risk == 'HIGH':
            final_risk = 'HIGH'
        elif ai_risk == 'LOW' and overall_risk in ['LOW-MEDIUM', 'MEDIUM']:
            final_risk = 'MEDIUM'
        else:
            final_risk = overall_risk
        
        return {
            'overall_risk_assessment': final_risk,
            'risk_metrics': risk_metrics,
            'position_sizing': position_sizing,
            'stop_loss_levels': stop_loss_levels,
            'ai_risk_analysis': ai_analysis,
            'risk_score': self._calculate_risk_score(risk_metrics),
            'recommendations': self._generate_risk_recommendations(
                final_risk, position_sizing, stop_loss_levels
            ),
            'confidence': self._calculate_risk_confidence(risk_metrics, ai_analysis)
        }
    
    def _calculate_risk_score(self, risk_metrics: Dict[str, Any]) -> float:
        """
        리스크 점수 계산 (0-100, 높을수록 위험)
        
        Args:
            risk_metrics: 리스크 메트릭
            
        Returns:
            리스크 점수
        """
        try:
            volatility = risk_metrics.get('volatility', 0.2)
            max_drawdown = risk_metrics.get('max_drawdown', 0.1)
            var_95 = risk_metrics.get('var_95', 0.02)
            
            # 각 메트릭을 0-100 스케일로 변환
            vol_score = min(100, volatility * 250)  # 변동성 점수
            dd_score = min(100, max_drawdown * 400)  # 낙폭 점수
            var_score = min(100, var_95 * 2000)     # VaR 점수
            
            # 가중 평균으로 최종 점수 계산
            risk_score = (vol_score * 0.4 + dd_score * 0.4 + var_score * 0.2)
            
            return round(risk_score, 1)
            
        except Exception as e:
            logger.error(f"리스크 점수 계산 중 오류: {str(e)}")
            return 50.0  # 기본값
    
    def _generate_risk_recommendations(self, risk_level: str, 
                                     position_sizing: Dict[str, Any],
                                     stop_loss_levels: Dict[str, Any]) -> List[str]:
        """
        리스크 레벨에 따른 추천사항 생성
        
        Args:
            risk_level: 리스크 레벨
            position_sizing: 포지션 사이징 정보
            stop_loss_levels: 스톱로스 레벨 정보
            
        Returns:
            추천사항 리스트
        """
        recommendations = []
        
        # 포지션 사이징 추천
        recommended_size = position_sizing.get('recommended_position_percent', 5.0)
        recommendations.append(f"Recommended position size: {recommended_size}% of portfolio")
        
        # 스톱로스 추천
        recommended_stop = stop_loss_levels.get('recommended_stop', 0)
        if recommended_stop > 0:
            recommendations.append(f"Set stop-loss at ${recommended_stop:.2f}")
        
        # 리스크 레벨별 추천
        if risk_level == 'HIGH':
            recommendations.extend([
                "Consider reducing position size due to high volatility",
                "Use tight stop-losses to limit downside",
                "Monitor position closely for exit signals",
                "Consider hedging strategies if maintaining position"
            ])
        elif risk_level == 'MEDIUM-HIGH':
            recommendations.extend([
                "Use conservative position sizing",
                "Set clear exit criteria before entering",
                "Consider dollar-cost averaging for entry"
            ])
        elif risk_level in ['MEDIUM', 'LOW-MEDIUM']:
            recommendations.extend([
                "Standard position sizing acceptable",
                "Use trailing stops to protect profits",
                "Regular portfolio rebalancing recommended"
            ])
        
        return recommendations
    
    def _calculate_risk_confidence(self, risk_metrics: Dict[str, Any], 
                                 ai_analysis: Dict[str, Any]) -> float:
        """
        리스크 분석 신뢰도 계산
        
        Args:
            risk_metrics: 리스크 메트릭
            ai_analysis: AI 분석 결과
            
        Returns:
            신뢰도 점수 (0.0 ~ 1.0)
        """
        base_confidence = 0.7
        
        # 데이터 품질에 따른 조정
        if risk_metrics.get('volatility', 0) > 0:
            base_confidence += 0.1
        
        if risk_metrics.get('max_drawdown', 0) > 0:
            base_confidence += 0.1
        
        # AI 분석 품질에 따른 조정
        ai_confidence = ai_analysis.get('confidence', 0.5)
        if isinstance(ai_confidence, (int, float)):
            base_confidence = (base_confidence + ai_confidence) / 2
        
        return round(min(1.0, base_confidence), 2)
    
    def log_risk_analysis(self, symbol: str, assessment: Dict[str, Any]):
        """리스크 분석 결과 로깅"""
        logger.info(f"[{self.agent_name}] {symbol} 리스크 분석 완료")
        logger.info(f"  전체 리스크: {assessment.get('overall_risk_assessment', 'N/A')}")
        logger.info(f"  리스크 점수: {assessment.get('risk_score', 0)}")
        logger.info(f"  추천 포지션: {assessment.get('position_sizing', {}).get('recommended_position_percent', 0)}%")
    
    def _save_analysis_result(self, symbol: str, analysis_result: Dict[str, Any]):
        """분석 결과를 데이터베이스에 저장"""
        try:
            self.db_manager.execute_update(
                """INSERT INTO analysis_results 
                   (symbol, agent_type, analysis_type, result_data, confidence_score)
                   VALUES (?, ?, ?, ?, ?)""",
                (symbol, self.agent_type, 'risk_analysis', 
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
            'overall_risk_assessment': 'HIGH',  # 오류 시 높은 리스크로 설정
            'risk_score': 80.0,
            'error': True,
            'error_message': error_msg,
            'analysis_timestamp': self._get_timestamp(),
            'recommendations': ['Manual review required due to analysis error']
        }
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()

# 테스트 및 예제 실행
if __name__ == "__main__":
    print("=== AI Stock Trading System - Risk Manager ===")
    
    # 리스크 매니저 생성
    risk_manager = RiskManager()
    
    # 테스트 주식 데이터 (변동성이 큰 데이터)
    test_stock_data = {
        'recent_prices': [
            {'date': '2025-09-25', 'close_price': 250.00, 'low_price': 245.00, 'volume': 60000000},
            {'date': '2025-09-24', 'close_price': 245.50, 'low_price': 240.00, 'volume': 55000000},
            {'date': '2025-09-23', 'close_price': 255.80, 'low_price': 250.00, 'volume': 45000000},
            {'date': '2025-09-22', 'close_price': 248.30, 'low_price': 245.00, 'volume': 70000000},
            {'date': '2025-09-21', 'close_price': 260.15, 'low_price': 255.00, 'volume': 40000000},
            {'date': '2025-09-20', 'close_price': 252.75, 'low_price': 248.00, 'volume': 50000000},
            {'date': '2025-09-19', 'close_price': 258.90, 'low_price': 252.00, 'volume': 35000000},
            {'date': '2025-09-18', 'close_price': 245.60, 'low_price': 240.00, 'volume': 80000000},
            {'date': '2025-09-17', 'close_price': 265.20, 'low_price': 260.00, 'volume': 30000000},
            {'date': '2025-09-16', 'close_price': 255.40, 'low_price': 250.00, 'volume': 45000000}
        ]
    }
    
    # 시장 컨텍스트
    market_context = {
        'sentiment': 'VOLATILE',
        'sector_performance': 'MIXED',
        'economic_indicators': 'UNCERTAIN'
    }
    
    # AAPL 리스크 분석 수행
    print("🔍 AAPL 리스크 분석 수행 중...")
    risk_assessment = risk_manager.analyze_stock('AAPL', test_stock_data, market_context)
    
    # 결과 출력
    print(f"\n📊 리스크 분석 결과:")
    print(f"  전체 리스크 레벨: {risk_assessment.get('overall_risk_assessment', 'N/A')}")
    print(f"  리스크 점수: {risk_assessment.get('risk_score', 0)}/100")
    print(f"  신뢰도: {risk_assessment.get('confidence', 0):.2f}")
    
    # 리스크 메트릭
    risk_metrics = risk_assessment.get('risk_metrics', {})
    print(f"\n📈 리스크 메트릭:")
    print(f"  변동성: {risk_metrics.get('volatility', 0):.1%}")
    print(f"  최대 낙폭: {risk_metrics.get('max_drawdown', 0):.1%}")
    print(f"  VaR 95%: {risk_metrics.get('var_95', 0):.1%}")
    
    # 포지션 사이징
    position_sizing = risk_assessment.get('position_sizing', {})
    print(f"\n💰 포지션 사이징:")
    print(f"  추천 포지션: {position_sizing.get('recommended_position_percent', 0)}%")
    print(f"  최대 포지션: {position_sizing.get('max_position_percent', 0)}%")
    
    # 스톱로스 레벨
    stop_loss = risk_assessment.get('stop_loss_levels', {})
    print(f"\n🛑 스톱로스 레벨:")
    print(f"  추천 스톱로스: ${stop_loss.get('recommended_stop', 0):.2f}")
    print(f"  보수적 스톱로스: ${stop_loss.get('conservative_stop', 0):.2f}")
    print(f"  기술적 스톱로스: ${stop_loss.get('technical_stop', 0):.2f}")
    
    # 추천사항
    recommendations = risk_assessment.get('recommendations', [])
    print(f"\n💡 추천사항:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n✅ 리스크 매니저 테스트 완료")
