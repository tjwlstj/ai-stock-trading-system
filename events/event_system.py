"""
실시간 이벤트 기반 아키텍처
주식 시장의 실시간 이벤트를 처리하고 AI 에이전트들에게 전달하는 시스템
"""

import asyncio
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import threading
from queue import Queue, Empty
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """이벤트 타입 정의"""
    PRICE_CHANGE = "price_change"
    VOLUME_SPIKE = "volume_spike"
    NEWS_ALERT = "news_alert"
    EARNINGS_ANNOUNCEMENT = "earnings_announcement"
    MARKET_OPEN = "market_open"
    MARKET_CLOSE = "market_close"
    TECHNICAL_INDICATOR = "technical_indicator"
    AI_ANALYSIS_COMPLETE = "ai_analysis_complete"
    TRADE_SIGNAL = "trade_signal"
    RISK_ALERT = "risk_alert"

class EventPriority(Enum):
    """이벤트 우선순위"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MarketEvent:
    """시장 이벤트 데이터 구조"""
    event_id: str
    event_type: EventType
    symbol: str
    timestamp: float
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.MEDIUM
    source: str = "unknown"
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['priority'] = self.priority.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketEvent':
        """딕셔너리에서 생성"""
        data['event_type'] = EventType(data['event_type'])
        data['priority'] = EventPriority(data['priority'])
        return cls(**data)

class EventHandler(ABC):
    """이벤트 핸들러 추상 클래스"""
    
    def __init__(self, handler_id: str):
        self.handler_id = handler_id
        self.supported_events: Set[EventType] = set()
    
    @abstractmethod
    async def handle_event(self, event: MarketEvent) -> Optional[MarketEvent]:
        """
        이벤트 처리
        
        Args:
            event: 처리할 이벤트
            
        Returns:
            Optional[MarketEvent]: 새로 생성된 이벤트 (있는 경우)
        """
        pass
    
    def can_handle(self, event_type: EventType) -> bool:
        """이벤트 타입 처리 가능 여부 확인"""
        return event_type in self.supported_events

class EventBus:
    """이벤트 버스 - 이벤트 발행/구독 시스템"""
    
    def __init__(self):
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self.event_queue = asyncio.Queue()
        self.running = False
        self.metrics = {
            "events_processed": 0,
            "events_failed": 0,
            "handlers_registered": 0,
            "average_processing_time": 0.0
        }
    
    def register_handler(self, handler: EventHandler, event_types: List[EventType]):
        """이벤트 핸들러 등록"""
        for event_type in event_types:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)
            handler.supported_events.add(event_type)
        
        self.metrics["handlers_registered"] += 1
        logger.info(f"Handler {handler.handler_id} registered for {len(event_types)} event types")
    
    async def publish_event(self, event: MarketEvent):
        """이벤트 발행"""
        await self.event_queue.put(event)
        logger.debug(f"Event published: {event.event_type.value} for {event.symbol}")
    
    async def start_processing(self):
        """이벤트 처리 시작"""
        self.running = True
        logger.info("Event bus started processing")
        
        while self.running:
            try:
                # 이벤트 대기 (타임아웃 설정)
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._process_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                self.metrics["events_failed"] += 1
    
    async def _process_event(self, event: MarketEvent):
        """개별 이벤트 처리"""
        start_time = time.time()
        
        try:
            # 해당 이벤트 타입의 핸들러들 찾기
            handlers = self.handlers.get(event.event_type, [])
            
            if not handlers:
                logger.warning(f"No handlers found for event type: {event.event_type.value}")
                return
            
            # 우선순위별로 핸들러 실행
            tasks = []
            for handler in handlers:
                if handler.can_handle(event.event_type):
                    task = asyncio.create_task(handler.handle_event(event))
                    tasks.append(task)
            
            # 모든 핸들러 병렬 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 처리 및 새 이벤트 발행
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Handler error: {result}")
                    self.metrics["events_failed"] += 1
                elif isinstance(result, MarketEvent):
                    # 핸들러가 새 이벤트를 생성한 경우
                    await self.publish_event(result)
            
            # 이벤트 처리 완료 표시
            event.processed = True
            self.metrics["events_processed"] += 1
            
            # 평균 처리 시간 업데이트
            processing_time = time.time() - start_time
            total_time = (self.metrics["average_processing_time"] * 
                         (self.metrics["events_processed"] - 1) + processing_time)
            self.metrics["average_processing_time"] = total_time / self.metrics["events_processed"]
            
            logger.debug(f"Event processed in {processing_time:.3f}s: {event.event_type.value}")
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            self.metrics["events_failed"] += 1
    
    def stop_processing(self):
        """이벤트 처리 중지"""
        self.running = False
        logger.info("Event bus stopped processing")
    
    def get_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 반환"""
        return {
            **self.metrics,
            "queue_size": self.event_queue.qsize(),
            "handlers_count": sum(len(handlers) for handlers in self.handlers.values()),
            "success_rate": (self.metrics["events_processed"] / 
                           max(self.metrics["events_processed"] + self.metrics["events_failed"], 1))
        }

class RealTimeDataStream:
    """실시간 데이터 스트림 시뮬레이터"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.running = False
        self.symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        self.last_prices = {symbol: 100.0 for symbol in self.symbols}
    
    async def start_streaming(self):
        """데이터 스트리밍 시작"""
        self.running = True
        logger.info("Real-time data streaming started")
        
        while self.running:
            try:
                # 랜덤 심볼 선택
                import random
                symbol = random.choice(self.symbols)
                
                # 가격 변동 시뮬레이션
                current_price = self.last_prices[symbol]
                price_change = random.uniform(-0.05, 0.05)  # ±5% 변동
                new_price = current_price * (1 + price_change)
                self.last_prices[symbol] = new_price
                
                # 가격 변동 이벤트 생성
                if abs(price_change) > 0.02:  # 2% 이상 변동 시 이벤트 발행
                    event = MarketEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=EventType.PRICE_CHANGE,
                        symbol=symbol,
                        timestamp=time.time(),
                        data={
                            "old_price": current_price,
                            "new_price": new_price,
                            "change_percent": price_change * 100,
                            "volume": random.randint(1000000, 10000000)
                        },
                        priority=EventPriority.HIGH if abs(price_change) > 0.03 else EventPriority.MEDIUM
                    )
                    
                    await self.event_bus.publish_event(event)
                
                # 볼륨 급증 이벤트 (가끔)
                if random.random() < 0.1:  # 10% 확률
                    volume_event = MarketEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=EventType.VOLUME_SPIKE,
                        symbol=symbol,
                        timestamp=time.time(),
                        data={
                            "current_volume": random.randint(50000000, 100000000),
                            "average_volume": random.randint(10000000, 30000000),
                            "spike_ratio": random.uniform(2.0, 5.0)
                        },
                        priority=EventPriority.HIGH
                    )
                    
                    await self.event_bus.publish_event(volume_event)
                
                # 뉴스 이벤트 (드물게)
                if random.random() < 0.05:  # 5% 확률
                    news_event = MarketEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=EventType.NEWS_ALERT,
                        symbol=symbol,
                        timestamp=time.time(),
                        data={
                            "headline": f"{symbol} reports strong quarterly results",
                            "sentiment": random.choice(["positive", "negative", "neutral"]),
                            "impact_score": random.uniform(0.1, 1.0)
                        },
                        priority=EventPriority.MEDIUM
                    )
                    
                    await self.event_bus.publish_event(news_event)
                
                # 스트리밍 간격 (실제로는 더 빠를 수 있음)
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                logger.error(f"Error in data streaming: {e}")
                await asyncio.sleep(1.0)
    
    def stop_streaming(self):
        """데이터 스트리밍 중지"""
        self.running = False
        logger.info("Real-time data streaming stopped")

class EventLogger(EventHandler):
    """이벤트 로깅 핸들러"""
    
    def __init__(self):
        super().__init__("event_logger")
        self.event_log = []
    
    async def handle_event(self, event: MarketEvent) -> Optional[MarketEvent]:
        """이벤트 로깅"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(event.timestamp).isoformat(),
            "event_type": event.event_type.value,
            "symbol": event.symbol,
            "priority": event.priority.value,
            "data": event.data
        }
        
        self.event_log.append(log_entry)
        
        # 로그 크기 제한 (최근 1000개만 유지)
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-1000:]
        
        logger.info(f"Event logged: {event.event_type.value} - {event.symbol}")
        return None
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 이벤트 반환"""
        return self.event_log[-limit:]

# 편의 함수들
def create_price_change_event(symbol: str, old_price: float, new_price: float) -> MarketEvent:
    """가격 변동 이벤트 생성"""
    change_percent = ((new_price - old_price) / old_price) * 100
    
    return MarketEvent(
        event_id=str(uuid.uuid4()),
        event_type=EventType.PRICE_CHANGE,
        symbol=symbol,
        timestamp=time.time(),
        data={
            "old_price": old_price,
            "new_price": new_price,
            "change_percent": change_percent
        },
        priority=EventPriority.HIGH if abs(change_percent) > 3.0 else EventPriority.MEDIUM
    )

def create_news_event(symbol: str, headline: str, sentiment: str = "neutral") -> MarketEvent:
    """뉴스 이벤트 생성"""
    return MarketEvent(
        event_id=str(uuid.uuid4()),
        event_type=EventType.NEWS_ALERT,
        symbol=symbol,
        timestamp=time.time(),
        data={
            "headline": headline,
            "sentiment": sentiment,
            "impact_score": 0.5
        },
        priority=EventPriority.MEDIUM
    )
