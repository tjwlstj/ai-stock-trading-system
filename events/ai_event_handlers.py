"""
AI 에이전트 이벤트 핸들러
실시간 이벤트에 반응하는 AI 에이전트들을 구현합니다.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .event_system import EventHandler, MarketEvent, EventType, EventPriority
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.ai_provider import AnalysisRequest
from agents.ai_provider_factory import create_provider_by_name

logger = logging.getLogger(__name__)

class AIAnalysisHandler(EventHandler):
    """AI 분석 이벤트 핸들러"""
    
    def __init__(self, agent_name: str, model_name: str = "gpt-4.1-mini"):
        super().__init__(f"ai_analysis_{agent_name}")
        self.agent_name = agent_name
        self.model_name = model_name
        
        # AI Provider 초기화
        try:
            self.ai_provider = create_provider_by_name(model_name)
            logger.info(f"AI Analysis Handler '{agent_name}' initialized with {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize AI provider: {e}")
            self.ai_provider = None
        
        # 분석 캐시 (중복 분석 방지)
        self.analysis_cache = {}
        self.cache_ttl = 300  # 5분
    
    async def handle_event(self, event: MarketEvent) -> Optional[MarketEvent]:
        """이벤트 기반 AI 분석 수행"""
        if not self.ai_provider:
            logger.error("AI provider not available")
            return None
        
        try:
            # 캐시 확인
            cache_key = f"{event.symbol}_{event.event_type.value}_{int(event.timestamp/60)}"
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.cache_ttl:
                    logger.debug(f"Using cached analysis for {event.symbol}")
                    return None
            
            # AI 분석 수행
            analysis_prompt = self._build_analysis_prompt(event)
            
            request = AnalysisRequest(
                prompt=analysis_prompt,
                stock_data=self._extract_stock_data(event),
                temperature=0.7,
                max_tokens=800
            )
            
            start_time = time.time()
            response = self.ai_provider.generate_analysis(request)
            processing_time = time.time() - start_time
            
            # 분석 결과 캐싱
            self.analysis_cache[cache_key] = {
                'result': response,
                'timestamp': time.time()
            }
            
            # 분석 완료 이벤트 생성
            analysis_event = MarketEvent(
                event_id=f"analysis_{event.event_id}",
                event_type=EventType.AI_ANALYSIS_COMPLETE,
                symbol=event.symbol,
                timestamp=time.time(),
                data={
                    "original_event_id": event.event_id,
                    "agent_name": self.agent_name,
                    "analysis": response.content,
                    "model_used": response.model_used,
                    "processing_time": processing_time,
                    "cost": response.cost_estimate,
                    "confidence": response.confidence_score,
                    "recommendation": self._extract_recommendation(response.content),
                    "trigger_event_type": event.event_type.value
                },
                priority=EventPriority.MEDIUM,
                source=f"ai_agent_{self.agent_name}"
            )
            
            logger.info(f"AI analysis completed for {event.symbol} by {self.agent_name}")
            return analysis_event
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None
    
    def _build_analysis_prompt(self, event: MarketEvent) -> str:
        """이벤트 기반 분석 프롬프트 구성"""
        base_prompt = f"""
You are a {self.agent_name} analyzing a real-time market event for {event.symbol}.

Event Details:
- Type: {event.event_type.value}
- Priority: {event.priority.value}
- Timestamp: {datetime.fromtimestamp(event.timestamp).isoformat()}
- Data: {event.data}

Please provide a focused analysis based on this specific event:
1. Event Impact Assessment
2. Short-term Price Prediction
3. Trading Recommendation (BUY/HOLD/SELL)
4. Confidence Level (0-100%)
5. Key Risk Factors

Keep the analysis concise but actionable.
"""
        return base_prompt
    
    def _extract_stock_data(self, event: MarketEvent) -> Dict[str, Any]:
        """이벤트에서 주식 데이터 추출"""
        stock_data = {
            "symbol": event.symbol,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp
        }
        
        # 이벤트 타입별 데이터 추출
        if event.event_type == EventType.PRICE_CHANGE:
            stock_data.update({
                "current_price": event.data.get("new_price"),
                "previous_price": event.data.get("old_price"),
                "change_percent": event.data.get("change_percent"),
                "volume": event.data.get("volume")
            })
        elif event.event_type == EventType.VOLUME_SPIKE:
            stock_data.update({
                "current_volume": event.data.get("current_volume"),
                "average_volume": event.data.get("average_volume"),
                "spike_ratio": event.data.get("spike_ratio")
            })
        elif event.event_type == EventType.NEWS_ALERT:
            stock_data.update({
                "news_headline": event.data.get("headline"),
                "sentiment": event.data.get("sentiment"),
                "impact_score": event.data.get("impact_score")
            })
        
        return stock_data
    
    def _extract_recommendation(self, analysis: str) -> str:
        """분석에서 추천 의견 추출"""
        analysis_lower = analysis.lower()
        
        if "strong buy" in analysis_lower:
            return "STRONG_BUY"
        elif "buy" in analysis_lower:
            return "BUY"
        elif "strong sell" in analysis_lower:
            return "STRONG_SELL"
        elif "sell" in analysis_lower:
            return "SELL"
        else:
            return "HOLD"

class OptimisticAnalysisHandler(AIAnalysisHandler):
    """낙관적 분석가 이벤트 핸들러"""
    
    def __init__(self, model_name: str = "gpt-4.1-mini"):
        super().__init__("optimistic_analyst", model_name)
    
    def _build_analysis_prompt(self, event: MarketEvent) -> str:
        """낙관적 관점의 분석 프롬프트"""
        return f"""
You are an OPTIMISTIC stock analyst focusing on growth opportunities and positive market signals.

Event for {event.symbol}:
- Type: {event.event_type.value}
- Data: {event.data}

As an optimistic analyst, focus on:
1. Growth potential and positive catalysts
2. Market opportunities this event might create
3. Bullish technical indicators
4. Positive sentiment factors
5. Upside price targets

Provide a BUY-oriented analysis with confidence level.
Be optimistic but realistic in your assessment.
"""

class PessimisticAnalysisHandler(AIAnalysisHandler):
    """비관적 분석가 이벤트 핸들러"""
    
    def __init__(self, model_name: str = "gpt-4.1-nano"):
        super().__init__("pessimistic_analyst", model_name)
    
    def _build_analysis_prompt(self, event: MarketEvent) -> str:
        """비관적 관점의 분석 프롬프트"""
        return f"""
You are a PESSIMISTIC stock analyst focusing on risks and potential downsides.

Event for {event.symbol}:
- Type: {event.event_type.value}
- Data: {event.data}

As a pessimistic analyst, focus on:
1. Risk factors and potential threats
2. Market vulnerabilities this event exposes
3. Bearish technical indicators
4. Negative sentiment factors
5. Downside price targets

Provide a risk-focused analysis with SELL/HOLD bias.
Be cautious and highlight potential problems.
"""

class RiskManagerHandler(AIAnalysisHandler):
    """리스크 매니저 이벤트 핸들러"""
    
    def __init__(self, model_name: str = "gpt-4.1-mini"):
        super().__init__("risk_manager", model_name)
    
    def _build_analysis_prompt(self, event: MarketEvent) -> str:
        """리스크 관리 관점의 분석 프롬프트"""
        return f"""
You are a RISK MANAGER analyzing portfolio implications of market events.

Event for {event.symbol}:
- Type: {event.event_type.value}
- Data: {event.data}

As a risk manager, provide:
1. Risk Level Assessment (LOW/MEDIUM/HIGH/CRITICAL)
2. Portfolio Impact Analysis
3. Position Sizing Recommendations
4. Stop-loss and Take-profit Levels
5. Hedging Strategies (if needed)

Focus on capital preservation and risk-adjusted returns.
Provide specific risk management actions.
"""

class TradeSignalGenerator(EventHandler):
    """거래 신호 생성기"""
    
    def __init__(self):
        super().__init__("trade_signal_generator")
        self.analysis_buffer = {}  # 에이전트별 분석 결과 버퍼
        self.signal_threshold = 2  # 최소 2개 에이전트 분석 필요
    
    async def handle_event(self, event: MarketEvent) -> Optional[MarketEvent]:
        """AI 분석 결과를 종합하여 거래 신호 생성"""
        if event.event_type != EventType.AI_ANALYSIS_COMPLETE:
            return None
        
        symbol = event.symbol
        agent_name = event.data.get("agent_name")
        
        # 분석 결과 버퍼에 저장
        if symbol not in self.analysis_buffer:
            self.analysis_buffer[symbol] = {}
        
        self.analysis_buffer[symbol][agent_name] = {
            "recommendation": event.data.get("recommendation"),
            "confidence": event.data.get("confidence", 0.5),
            "analysis": event.data.get("analysis"),
            "timestamp": event.timestamp
        }
        
        # 충분한 분석이 모였는지 확인
        analyses = self.analysis_buffer[symbol]
        if len(analyses) < self.signal_threshold:
            return None
        
        # 거래 신호 생성
        signal = self._generate_trade_signal(symbol, analyses)
        
        if signal:
            trade_event = MarketEvent(
                event_id=f"trade_signal_{symbol}_{int(time.time())}",
                event_type=EventType.TRADE_SIGNAL,
                symbol=symbol,
                timestamp=time.time(),
                data=signal,
                priority=EventPriority.HIGH,
                source="trade_signal_generator"
            )
            
            # 버퍼 정리 (오래된 분석 제거)
            self._cleanup_buffer(symbol)
            
            logger.info(f"Trade signal generated for {symbol}: {signal['action']}")
            return trade_event
        
        return None
    
    def _generate_trade_signal(self, symbol: str, analyses: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
        """분석 결과를 종합하여 거래 신호 생성"""
        recommendations = []
        confidences = []
        
        for agent_name, analysis in analyses.items():
            rec = analysis.get("recommendation", "HOLD")
            conf = analysis.get("confidence", 0.5)
            
            # 추천을 점수로 변환
            score_map = {
                "STRONG_BUY": 2,
                "BUY": 1,
                "HOLD": 0,
                "SELL": -1,
                "STRONG_SELL": -2
            }
            
            score = score_map.get(rec, 0)
            weighted_score = score * conf
            
            recommendations.append(weighted_score)
            confidences.append(conf)
        
        # 가중 평균 계산
        if not recommendations:
            return None
        
        avg_score = sum(recommendations) / len(recommendations)
        avg_confidence = sum(confidences) / len(confidences)
        
        # 거래 신호 결정
        if avg_score > 0.5:
            action = "BUY"
        elif avg_score < -0.5:
            action = "SELL"
        else:
            action = "HOLD"
        
        # 신호 강도 계산
        strength = min(abs(avg_score), 1.0)
        
        return {
            "action": action,
            "strength": strength,
            "confidence": avg_confidence,
            "consensus_score": avg_score,
            "agent_count": len(analyses),
            "agent_recommendations": {
                agent: analysis["recommendation"] 
                for agent, analysis in analyses.items()
            }
        }
    
    def _cleanup_buffer(self, symbol: str):
        """오래된 분석 결과 정리"""
        current_time = time.time()
        ttl = 300  # 5분
        
        if symbol in self.analysis_buffer:
            self.analysis_buffer[symbol] = {
                agent: analysis
                for agent, analysis in self.analysis_buffer[symbol].items()
                if current_time - analysis["timestamp"] < ttl
            }
            
            # 빈 버퍼 제거
            if not self.analysis_buffer[symbol]:
                del self.analysis_buffer[symbol]

# 편의 함수들
def setup_ai_event_handlers(event_bus) -> List[EventHandler]:
    """AI 이벤트 핸들러들을 설정하고 등록"""
    handlers = []
    
    # AI 분석 핸들러들
    optimistic_handler = OptimisticAnalysisHandler()
    pessimistic_handler = PessimisticAnalysisHandler()
    risk_handler = RiskManagerHandler()
    
    # 거래 신호 생성기
    signal_generator = TradeSignalGenerator()
    
    handlers.extend([optimistic_handler, pessimistic_handler, risk_handler, signal_generator])
    
    # 이벤트 버스에 등록
    market_events = [EventType.PRICE_CHANGE, EventType.VOLUME_SPIKE, EventType.NEWS_ALERT]
    
    event_bus.register_handler(optimistic_handler, market_events)
    event_bus.register_handler(pessimistic_handler, market_events)
    event_bus.register_handler(risk_handler, market_events)
    event_bus.register_handler(signal_generator, [EventType.AI_ANALYSIS_COMPLETE])
    
    logger.info("AI event handlers setup completed")
    return handlers
