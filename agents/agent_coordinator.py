"""
AI Stock Trading System - Agent Coordinator
다중 AI 에이전트 조정자 - 여러 에이전트의 분석을 통합하고 최종 결정 도출
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.optimistic_agent import OptimisticAnalyst
from agents.pessimistic_agent import PessimisticAnalyst
from agents.risk_manager import RiskManager
from backend.database import DatabaseManager
from backend.data_collector import StockDataCollector
from backend.cloud_storage import CloudStorageManager
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """다중 AI 에이전트 조정자"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        에이전트 조정자 초기화
        
        Args:
            api_key: OpenAI API 키
        """
        self.api_key = api_key
        
        # AI 에이전트들 초기화
        self.optimistic_agent = OptimisticAnalyst(api_key)
        self.pessimistic_agent = PessimisticAnalyst(api_key)
        self.risk_manager = RiskManager(api_key)
        
        # 데이터 관리자들 초기화
        self.db_manager = DatabaseManager()
        self.data_collector = StockDataCollector()
        self.cloud_storage = CloudStorageManager()
        
        logger.info("다중 AI 에이전트 조정자 초기화 완료")
    
    def analyze_stock_comprehensive(self, symbol: str, 
                                  collect_fresh_data: bool = True) -> Dict[str, Any]:
        """
        종합적인 주식 분석 수행 (모든 에이전트 활용)
        
        Args:
            symbol: 주식 심볼
            collect_fresh_data: 새로운 데이터 수집 여부
            
        Returns:
            종합 분석 결과
        """
        logger.info(f"[AgentCoordinator] {symbol} 종합 분석 시작")
        
        try:
            # 1. 데이터 수집 및 준비
            stock_data = self._prepare_stock_data(symbol, collect_fresh_data)
            market_context = self._get_market_context()
            
            # 2. 각 에이전트별 분석 수행
            analyses = self._perform_multi_agent_analysis(symbol, stock_data, market_context)
            
            # 3. 분석 결과 통합
            integrated_analysis = self._integrate_analyses(symbol, analyses, stock_data)
            
            # 4. 최종 투자 결정 도출
            final_decision = self._make_final_decision(integrated_analysis)
            
            # 5. 결과 저장 및 백업
            self._save_comprehensive_result(symbol, final_decision)
            
            logger.info(f"[AgentCoordinator] {symbol} 종합 분석 완료")
            return final_decision
            
        except Exception as e:
            logger.error(f"[AgentCoordinator] {symbol} 종합 분석 중 오류: {str(e)}")
            return self._create_error_result(symbol, str(e))
    
    def _prepare_stock_data(self, symbol: str, collect_fresh: bool) -> Dict[str, Any]:
        """
        주식 데이터 준비
        
        Args:
            symbol: 주식 심볼
            collect_fresh: 새로운 데이터 수집 여부
            
        Returns:
            준비된 주식 데이터
        """
        try:
            # 새로운 데이터 수집
            if collect_fresh:
                logger.info(f"새로운 데이터 수집 중: {symbol}")
                self.data_collector.collect_stock_data(symbol, period="3mo")
            
            # 데이터베이스에서 최근 데이터 조회
            recent_prices = self.db_manager.get_latest_data(symbol, days=30)
            
            # 데이터 포맷팅
            stock_data = {
                'symbol': symbol,
                'recent_prices': recent_prices,
                'data_points': len(recent_prices),
                'last_updated': datetime.now().isoformat()
            }
            
            # 기본 통계 계산
            if recent_prices:
                prices = [float(p['close_price']) for p in recent_prices]
                stock_data.update({
                    'current_price': prices[0] if prices else 0,
                    'price_change_1d': ((prices[0] - prices[1]) / prices[1] * 100) if len(prices) > 1 else 0,
                    'price_change_7d': ((prices[0] - prices[6]) / prices[6] * 100) if len(prices) > 6 else 0,
                    'avg_volume': sum(p['volume'] for p in recent_prices[:10]) / min(10, len(recent_prices))
                })
            
            return stock_data
            
        except Exception as e:
            logger.error(f"데이터 준비 중 오류: {str(e)}")
            return {'symbol': symbol, 'recent_prices': [], 'error': str(e)}
    
    def _get_market_context(self) -> Dict[str, Any]:
        """
        시장 컨텍스트 정보 수집
        
        Returns:
            시장 컨텍스트 딕셔너리
        """
        # 간단한 시장 컨텍스트 (실제로는 더 복잡한 데이터 수집 가능)
        return {
            'sentiment': 'NEUTRAL',
            'sector_performance': 'MIXED',
            'economic_indicators': 'STABLE',
            'market_volatility': 'MEDIUM',
            'timestamp': datetime.now().isoformat()
        }
    
    def _perform_multi_agent_analysis(self, symbol: str, stock_data: Dict[str, Any], 
                                    market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        다중 에이전트 분석 수행
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 데이터
            market_context: 시장 컨텍스트
            
        Returns:
            각 에이전트별 분석 결과
        """
        analyses = {}
        
        try:
            # 낙관적 분석가
            logger.info(f"낙관적 분석 수행 중: {symbol}")
            analyses['optimistic'] = self.optimistic_agent.analyze_stock(
                symbol, stock_data, market_context
            )
            
            # 비관적 분석가
            logger.info(f"비관적 분석 수행 중: {symbol}")
            analyses['pessimistic'] = self.pessimistic_agent.analyze_stock(
                symbol, stock_data, market_context
            )
            
            # 리스크 매니저
            logger.info(f"리스크 분석 수행 중: {symbol}")
            analyses['risk'] = self.risk_manager.analyze_stock(
                symbol, stock_data, market_context
            )
            
        except Exception as e:
            logger.error(f"다중 에이전트 분석 중 오류: {str(e)}")
            analyses['error'] = str(e)
        
        return analyses
    
    def _integrate_analyses(self, symbol: str, analyses: Dict[str, Any], 
                          stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        각 에이전트의 분석 결과를 통합
        
        Args:
            symbol: 주식 심볼
            analyses: 에이전트별 분석 결과
            stock_data: 주식 데이터
            
        Returns:
            통합된 분석 결과
        """
        integration = {
            'symbol': symbol,
            'individual_analyses': analyses,
            'consensus': {},
            'conflicts': [],
            'confidence_weighted_result': {}
        }
        
        try:
            # 추천 의견 수집
            recommendations = []
            confidences = []
            target_prices = []
            
            for agent_type, analysis in analyses.items():
                if agent_type != 'error' and isinstance(analysis, dict):
                    rec = analysis.get('recommendation', 'HOLD')
                    conf = analysis.get('confidence', 0.5)
                    target = analysis.get('target_price', 0)
                    
                    recommendations.append(rec)
                    confidences.append(conf)
                    if target > 0:
                        target_prices.append(target)
            
            # 합의 도출
            integration['consensus'] = self._calculate_consensus(
                recommendations, confidences, target_prices
            )
            
            # 의견 충돌 식별
            integration['conflicts'] = self._identify_conflicts(analyses)
            
            # 신뢰도 가중 결과
            integration['confidence_weighted_result'] = self._calculate_weighted_result(
                analyses, confidences
            )
            
            # 리스크 조정된 최종 추천
            integration['risk_adjusted_recommendation'] = self._apply_risk_adjustment(
                integration['consensus'], analyses.get('risk', {})
            )
            
        except Exception as e:
            logger.error(f"분석 통합 중 오류: {str(e)}")
            integration['error'] = str(e)
        
        return integration
    
    def _calculate_consensus(self, recommendations: List[str], 
                           confidences: List[float], 
                           target_prices: List[float]) -> Dict[str, Any]:
        """
        에이전트들의 합의 계산
        
        Args:
            recommendations: 추천 리스트
            confidences: 신뢰도 리스트
            target_prices: 목표가 리스트
            
        Returns:
            합의 결과
        """
        consensus = {
            'recommendation': 'HOLD',
            'confidence': 0.5,
            'target_price': 0.0,
            'agreement_level': 0.0
        }
        
        if not recommendations:
            return consensus
        
        # 가중 투표 방식으로 추천 결정
        buy_weight = sum(conf for rec, conf in zip(recommendations, confidences) if rec == 'BUY')
        sell_weight = sum(conf for rec, conf in zip(recommendations, confidences) if rec == 'SELL')
        hold_weight = sum(conf for rec, conf in zip(recommendations, confidences) if rec == 'HOLD')
        
        total_weight = buy_weight + sell_weight + hold_weight
        
        if total_weight > 0:
            if buy_weight > sell_weight and buy_weight > hold_weight:
                consensus['recommendation'] = 'BUY'
                consensus['confidence'] = buy_weight / total_weight
            elif sell_weight > buy_weight and sell_weight > hold_weight:
                consensus['recommendation'] = 'SELL'
                consensus['confidence'] = sell_weight / total_weight
            else:
                consensus['recommendation'] = 'HOLD'
                consensus['confidence'] = hold_weight / total_weight
        
        # 목표가 평균
        if target_prices:
            consensus['target_price'] = sum(target_prices) / len(target_prices)
        
        # 합의 수준 계산 (같은 추천의 비율)
        most_common_rec = consensus['recommendation']
        agreement_count = sum(1 for rec in recommendations if rec == most_common_rec)
        consensus['agreement_level'] = agreement_count / len(recommendations)
        
        return consensus
    
    def _identify_conflicts(self, analyses: Dict[str, Any]) -> List[str]:
        """
        에이전트 간 의견 충돌 식별
        
        Args:
            analyses: 에이전트별 분석 결과
            
        Returns:
            충돌 사항 리스트
        """
        conflicts = []
        
        try:
            recommendations = []
            for agent_type, analysis in analyses.items():
                if agent_type != 'error' and isinstance(analysis, dict):
                    rec = analysis.get('recommendation', 'HOLD')
                    recommendations.append((agent_type, rec))
            
            # BUY vs SELL 충돌
            buy_agents = [agent for agent, rec in recommendations if rec == 'BUY']
            sell_agents = [agent for agent, rec in recommendations if rec == 'SELL']
            
            if buy_agents and sell_agents:
                conflicts.append(f"Strong disagreement: {', '.join(buy_agents)} recommend BUY while {', '.join(sell_agents)} recommend SELL")
            
            # 리스크 레벨 충돌
            risk_analysis = analyses.get('risk', {})
            risk_level = risk_analysis.get('overall_risk_assessment', 'MEDIUM')
            
            if risk_level == 'HIGH' and buy_agents:
                conflicts.append(f"Risk conflict: High risk identified but {', '.join(buy_agents)} still recommend BUY")
            
        except Exception as e:
            logger.error(f"충돌 식별 중 오류: {str(e)}")
        
        return conflicts
    
    def _calculate_weighted_result(self, analyses: Dict[str, Any], 
                                 confidences: List[float]) -> Dict[str, Any]:
        """
        신뢰도 가중 결과 계산
        
        Args:
            analyses: 에이전트별 분석 결과
            confidences: 신뢰도 리스트
            
        Returns:
            가중 결과
        """
        weighted_result = {
            'final_recommendation': 'HOLD',
            'weighted_confidence': 0.5,
            'key_factors': []
        }
        
        try:
            # 각 에이전트의 가중치 계산
            total_confidence = sum(confidences) if confidences else 1.0
            
            buy_score = 0
            sell_score = 0
            hold_score = 0
            
            for agent_type, analysis in analyses.items():
                if agent_type != 'error' and isinstance(analysis, dict):
                    rec = analysis.get('recommendation', 'HOLD')
                    conf = analysis.get('confidence', 0.5)
                    weight = conf / total_confidence if total_confidence > 0 else 0.33
                    
                    if rec == 'BUY':
                        buy_score += weight
                    elif rec == 'SELL':
                        sell_score += weight
                    else:
                        hold_score += weight
            
            # 최고 점수의 추천 선택
            max_score = max(buy_score, sell_score, hold_score)
            
            if max_score == buy_score:
                weighted_result['final_recommendation'] = 'BUY'
                weighted_result['weighted_confidence'] = buy_score
            elif max_score == sell_score:
                weighted_result['final_recommendation'] = 'SELL'
                weighted_result['weighted_confidence'] = sell_score
            else:
                weighted_result['final_recommendation'] = 'HOLD'
                weighted_result['weighted_confidence'] = hold_score
            
            # 주요 요인 추출
            weighted_result['key_factors'] = self._extract_key_factors(analyses)
            
        except Exception as e:
            logger.error(f"가중 결과 계산 중 오류: {str(e)}")
        
        return weighted_result
    
    def _extract_key_factors(self, analyses: Dict[str, Any]) -> List[str]:
        """
        주요 결정 요인 추출
        
        Args:
            analyses: 에이전트별 분석 결과
            
        Returns:
            주요 요인 리스트
        """
        factors = []
        
        try:
            for agent_type, analysis in analyses.items():
                if agent_type != 'error' and isinstance(analysis, dict):
                    reasoning = analysis.get('reasoning', '')
                    if reasoning:
                        # 첫 번째 문장을 주요 요인으로 추출
                        first_sentence = reasoning.split('.')[0]
                        if len(first_sentence) > 10:
                            factors.append(f"[{agent_type.title()}] {first_sentence}")
        
        except Exception as e:
            logger.error(f"주요 요인 추출 중 오류: {str(e)}")
        
        return factors[:5]  # 최대 5개 요인
    
    def _apply_risk_adjustment(self, consensus: Dict[str, Any], 
                             risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        리스크를 고려한 최종 추천 조정
        
        Args:
            consensus: 합의 결과
            risk_analysis: 리스크 분석 결과
            
        Returns:
            리스크 조정된 추천
        """
        adjusted = consensus.copy()
        
        try:
            risk_level = risk_analysis.get('overall_risk_assessment', 'MEDIUM')
            risk_score = risk_analysis.get('risk_score', 50)
            
            # 높은 리스크 시 추천 하향 조정
            if risk_level == 'HIGH' or risk_score > 70:
                if adjusted['recommendation'] == 'BUY':
                    adjusted['recommendation'] = 'HOLD'
                    adjusted['confidence'] *= 0.8
                    adjusted['risk_adjustment'] = 'Downgraded from BUY to HOLD due to high risk'
                elif adjusted['recommendation'] == 'HOLD' and risk_score > 80:
                    adjusted['recommendation'] = 'SELL'
                    adjusted['confidence'] *= 0.9
                    adjusted['risk_adjustment'] = 'Downgraded from HOLD to SELL due to very high risk'
            
            # 포지션 사이징 정보 추가
            position_sizing = risk_analysis.get('position_sizing', {})
            adjusted['recommended_position_size'] = position_sizing.get('recommended_position_percent', 5.0)
            
            # 스톱로스 정보 추가
            stop_loss = risk_analysis.get('stop_loss_levels', {})
            adjusted['recommended_stop_loss'] = stop_loss.get('recommended_stop', 0)
            
        except Exception as e:
            logger.error(f"리스크 조정 중 오류: {str(e)}")
        
        return adjusted
    
    def _make_final_decision(self, integrated_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        최종 투자 결정 생성
        
        Args:
            integrated_analysis: 통합된 분석 결과
            
        Returns:
            최종 결정
        """
        final_decision = {
            'symbol': integrated_analysis.get('symbol', ''),
            'final_recommendation': 'HOLD',
            'confidence': 0.5,
            'target_price': 0.0,
            'position_size': 5.0,
            'stop_loss': 0.0,
            'reasoning': '',
            'risk_level': 'MEDIUM',
            'agent_consensus': {},
            'conflicts': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 리스크 조정된 추천 사용
            risk_adjusted = integrated_analysis.get('risk_adjusted_recommendation', {})
            
            final_decision.update({
                'final_recommendation': risk_adjusted.get('recommendation', 'HOLD'),
                'confidence': risk_adjusted.get('confidence', 0.5),
                'target_price': risk_adjusted.get('target_price', 0.0),
                'position_size': risk_adjusted.get('recommended_position_size', 5.0),
                'stop_loss': risk_adjusted.get('recommended_stop_loss', 0.0)
            })
            
            # 종합 근거 작성
            consensus = integrated_analysis.get('consensus', {})
            conflicts = integrated_analysis.get('conflicts', [])
            key_factors = integrated_analysis.get('confidence_weighted_result', {}).get('key_factors', [])
            
            reasoning_parts = []
            reasoning_parts.append(f"Multi-agent analysis consensus: {consensus.get('recommendation', 'HOLD')}")
            reasoning_parts.append(f"Agreement level: {consensus.get('agreement_level', 0):.1%}")
            
            if key_factors:
                reasoning_parts.append("Key factors: " + "; ".join(key_factors[:3]))
            
            if conflicts:
                reasoning_parts.append(f"Conflicts identified: {len(conflicts)} disagreements")
            
            final_decision['reasoning'] = ". ".join(reasoning_parts)
            
            # 추가 메타데이터
            final_decision.update({
                'agent_consensus': consensus,
                'conflicts': conflicts,
                'analysis_summary': integrated_analysis
            })
            
        except Exception as e:
            logger.error(f"최종 결정 생성 중 오류: {str(e)}")
            final_decision['error'] = str(e)
        
        return final_decision
    
    def _save_comprehensive_result(self, symbol: str, final_decision: Dict[str, Any]):
        """
        종합 분석 결과 저장
        
        Args:
            symbol: 주식 심볼
            final_decision: 최종 결정
        """
        try:
            # 데이터베이스에 저장
            self.db_manager.execute_update(
                """INSERT INTO analysis_results 
                   (symbol, agent_type, analysis_type, result_data, confidence_score)
                   VALUES (?, ?, ?, ?, ?)""",
                (symbol, 'coordinator', 'comprehensive_analysis', 
                 json.dumps(final_decision), final_decision.get('confidence', 0.5))
            )
            
            # 클라우드 스토리지에 백업
            self.cloud_storage.upload_analysis_results(
                final_decision, symbol, 'comprehensive_analysis'
            )
            
            logger.info(f"종합 분석 결과 저장 완료: {symbol}")
            
        except Exception as e:
            logger.error(f"결과 저장 중 오류: {str(e)}")
    
    def _create_error_result(self, symbol: str, error_msg: str) -> Dict[str, Any]:
        """오류 발생 시 기본 결과 생성"""
        return {
            'symbol': symbol,
            'final_recommendation': 'HOLD',
            'confidence': 0.3,
            'error': True,
            'error_message': error_msg,
            'reasoning': f'Analysis failed: {error_msg}',
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_portfolio(self, symbols: List[str]) -> Dict[str, Any]:
        """
        포트폴리오 전체 분석
        
        Args:
            symbols: 주식 심볼 리스트
            
        Returns:
            포트폴리오 분석 결과
        """
        logger.info(f"포트폴리오 분석 시작: {len(symbols)}개 종목")
        
        portfolio_results = {}
        
        for symbol in symbols:
            try:
                result = self.analyze_stock_comprehensive(symbol, collect_fresh_data=True)
                portfolio_results[symbol] = result
            except Exception as e:
                logger.error(f"포트폴리오 분석 중 {symbol} 오류: {str(e)}")
                portfolio_results[symbol] = self._create_error_result(symbol, str(e))
        
        # 포트폴리오 요약 생성
        portfolio_summary = self._create_portfolio_summary(portfolio_results)
        
        return {
            'individual_analyses': portfolio_results,
            'portfolio_summary': portfolio_summary,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _create_portfolio_summary(self, portfolio_results: Dict[str, Any]) -> Dict[str, Any]:
        """포트폴리오 요약 생성"""
        summary = {
            'total_stocks': len(portfolio_results),
            'buy_recommendations': 0,
            'sell_recommendations': 0,
            'hold_recommendations': 0,
            'avg_confidence': 0.0,
            'high_risk_stocks': [],
            'top_opportunities': []
        }
        
        confidences = []
        
        for symbol, result in portfolio_results.items():
            if not result.get('error', False):
                rec = result.get('final_recommendation', 'HOLD')
                conf = result.get('confidence', 0.5)
                
                if rec == 'BUY':
                    summary['buy_recommendations'] += 1
                elif rec == 'SELL':
                    summary['sell_recommendations'] += 1
                else:
                    summary['hold_recommendations'] += 1
                
                confidences.append(conf)
                
                # 고위험 종목 식별
                risk_level = result.get('risk_level', 'MEDIUM')
                if risk_level == 'HIGH':
                    summary['high_risk_stocks'].append(symbol)
                
                # 기회 종목 식별 (BUY + 높은 신뢰도)
                if rec == 'BUY' and conf > 0.7:
                    summary['top_opportunities'].append({
                        'symbol': symbol,
                        'confidence': conf,
                        'target_price': result.get('target_price', 0)
                    })
        
        if confidences:
            summary['avg_confidence'] = sum(confidences) / len(confidences)
        
        # 기회 종목 정렬 (신뢰도 순)
        summary['top_opportunities'].sort(key=lambda x: x['confidence'], reverse=True)
        
        return summary

# 테스트 및 예제 실행
if __name__ == "__main__":
    print("=== AI Stock Trading System - Agent Coordinator ===")
    
    # 에이전트 조정자 생성
    coordinator = AgentCoordinator()
    
    # 단일 종목 종합 분석
    print("🔍 AAPL 종합 분석 수행 중...")
    comprehensive_result = coordinator.analyze_stock_comprehensive('AAPL', collect_fresh_data=False)
    
    # 결과 출력
    print(f"\n📊 종합 분석 결과:")
    print(f"  최종 추천: {comprehensive_result.get('final_recommendation', 'N/A')}")
    print(f"  신뢰도: {comprehensive_result.get('confidence', 0):.2f}")
    print(f"  목표가: ${comprehensive_result.get('target_price', 0):.2f}")
    print(f"  포지션 크기: {comprehensive_result.get('position_size', 0)}%")
    print(f"  스톱로스: ${comprehensive_result.get('stop_loss', 0):.2f}")
    print(f"  근거: {comprehensive_result.get('reasoning', 'N/A')[:150]}...")
    
    # 에이전트 합의 정보
    consensus = comprehensive_result.get('agent_consensus', {})
    print(f"\n🤝 에이전트 합의:")
    print(f"  합의 추천: {consensus.get('recommendation', 'N/A')}")
    print(f"  합의 수준: {consensus.get('agreement_level', 0):.1%}")
    
    # 충돌 정보
    conflicts = comprehensive_result.get('conflicts', [])
    if conflicts:
        print(f"\n⚠️ 의견 충돌:")
        for i, conflict in enumerate(conflicts[:3], 1):
            print(f"  {i}. {conflict}")
    else:
        print(f"\n✅ 에이전트 간 의견 충돌 없음")
    
    # 포트폴리오 분석 (간단한 예제)
    print(f"\n📈 포트폴리오 분석 예제:")
    test_portfolio = ['AAPL', 'GOOGL']
    portfolio_result = coordinator.analyze_portfolio(test_portfolio)
    
    portfolio_summary = portfolio_result.get('portfolio_summary', {})
    print(f"  총 종목: {portfolio_summary.get('total_stocks', 0)}개")
    print(f"  BUY 추천: {portfolio_summary.get('buy_recommendations', 0)}개")
    print(f"  HOLD 추천: {portfolio_summary.get('hold_recommendations', 0)}개")
    print(f"  SELL 추천: {portfolio_summary.get('sell_recommendations', 0)}개")
    print(f"  평균 신뢰도: {portfolio_summary.get('avg_confidence', 0):.2f}")
    
    print(f"\n✅ 다중 AI 에이전트 조정자 테스트 완료")
