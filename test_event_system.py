#!/usr/bin/env python3
"""
실시간 이벤트 시스템 테스트 스크립트
이벤트 기반 아키텍처와 AI 에이전트 통합을 테스트합니다.
"""

import asyncio
import sys
import os
import time
import logging

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from events.event_system import (
    EventBus, RealTimeDataStream, EventLogger, MarketEvent, 
    EventType, EventPriority, create_price_change_event, create_news_event
)
from events.ai_event_handlers import setup_ai_event_handlers

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestEventHandler:
    """테스트용 이벤트 핸들러"""
    
    def __init__(self):
        self.received_events = []
        self.trade_signals = []
    
    async def handle_event(self, event: MarketEvent):
        """이벤트 수신 처리"""
        self.received_events.append(event)
        
        if event.event_type == EventType.TRADE_SIGNAL:
            self.trade_signals.append(event)
            logger.info(f"🚨 TRADE SIGNAL: {event.symbol} - {event.data['action']} "
                       f"(Strength: {event.data['strength']:.2f}, "
                       f"Confidence: {event.data['confidence']:.2f})")

async def test_basic_event_system():
    """기본 이벤트 시스템 테스트"""
    print("🧪 Testing Basic Event System...")
    
    # 이벤트 버스 생성
    event_bus = EventBus()
    
    # 이벤트 로거 등록
    event_logger = EventLogger()
    event_bus.register_handler(event_logger, list(EventType))
    
    # 이벤트 처리 시작
    processing_task = asyncio.create_task(event_bus.start_processing())
    
    try:
        # 테스트 이벤트 발행
        test_events = [
            create_price_change_event("AAPL", 150.0, 155.0),
            create_news_event("GOOGL", "Google announces new AI breakthrough", "positive"),
            MarketEvent(
                event_id="test_volume",
                event_type=EventType.VOLUME_SPIKE,
                symbol="MSFT",
                timestamp=time.time(),
                data={"current_volume": 50000000, "average_volume": 20000000, "spike_ratio": 2.5},
                priority=EventPriority.HIGH
            )
        ]
        
        for event in test_events:
            await event_bus.publish_event(event)
            await asyncio.sleep(0.1)
        
        # 처리 대기
        await asyncio.sleep(2)
        
        # 결과 확인
        metrics = event_bus.get_metrics()
        recent_events = event_logger.get_recent_events(5)
        
        print(f"✅ Events processed: {metrics['events_processed']}")
        print(f"📊 Success rate: {metrics['success_rate']:.2%}")
        print(f"⏱️  Avg processing time: {metrics['average_processing_time']:.3f}s")
        print(f"📝 Recent events logged: {len(recent_events)}")
        
        return True
        
    finally:
        event_bus.stop_processing()
        processing_task.cancel()
        try:
            await processing_task
        except asyncio.CancelledError:
            pass

async def test_ai_event_handlers():
    """AI 이벤트 핸들러 테스트"""
    print("\n🤖 Testing AI Event Handlers...")
    
    # OpenAI API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found. Skipping AI handler test.")
        return False
    
    # 이벤트 버스 생성
    event_bus = EventBus()
    
    # AI 핸들러들 설정
    ai_handlers = setup_ai_event_handlers(event_bus)
    
    # 테스트 핸들러 추가
    test_handler = TestEventHandler()
    
    # 커스텀 핸들러 등록 (trade signal 수신용)
    class TradeSignalHandler:
        def __init__(self, test_handler):
            self.handler_id = "trade_signal_receiver"
            self.supported_events = {EventType.TRADE_SIGNAL}
            self.test_handler = test_handler
        
        async def handle_event(self, event):
            await self.test_handler.handle_event(event)
            return None
        
        def can_handle(self, event_type):
            return event_type in self.supported_events
    
    trade_handler = TradeSignalHandler(test_handler)
    event_bus.register_handler(trade_handler, [EventType.TRADE_SIGNAL])
    
    # 이벤트 처리 시작
    processing_task = asyncio.create_task(event_bus.start_processing())
    
    try:
        # 테스트 이벤트 발행 (AI 분석을 트리거할 이벤트들)
        test_events = [
            create_price_change_event("AAPL", 175.0, 182.0),  # 4% 상승
            create_news_event("AAPL", "Apple reports record iPhone sales", "positive"),
            MarketEvent(
                event_id="test_volume_aapl",
                event_type=EventType.VOLUME_SPIKE,
                symbol="AAPL",
                timestamp=time.time(),
                data={"current_volume": 80000000, "average_volume": 30000000, "spike_ratio": 2.67},
                priority=EventPriority.HIGH
            )
        ]
        
        print("📡 Publishing test events...")
        for event in test_events:
            await event_bus.publish_event(event)
            print(f"   📤 {event.event_type.value} for {event.symbol}")
            await asyncio.sleep(1)
        
        # AI 분석 완료 대기
        print("⏳ Waiting for AI analysis...")
        await asyncio.sleep(15)  # AI 분석 시간 고려
        
        # 결과 확인
        metrics = event_bus.get_metrics()
        
        print(f"\n📊 Event System Metrics:")
        print(f"   Events processed: {metrics['events_processed']}")
        print(f"   Success rate: {metrics['success_rate']:.2%}")
        print(f"   Queue size: {metrics['queue_size']}")
        print(f"   Handlers count: {metrics['handlers_count']}")
        
        print(f"\n🎯 Test Results:")
        print(f"   Total events received: {len(test_handler.received_events)}")
        print(f"   Trade signals generated: {len(test_handler.trade_signals)}")
        
        # 거래 신호 상세 정보
        for signal in test_handler.trade_signals:
            data = signal.data
            print(f"\n🚨 Trade Signal for {signal.symbol}:")
            print(f"   Action: {data['action']}")
            print(f"   Strength: {data['strength']:.2f}")
            print(f"   Confidence: {data['confidence']:.2f}")
            print(f"   Agent Recommendations: {data['agent_recommendations']}")
        
        return len(test_handler.trade_signals) > 0
        
    finally:
        event_bus.stop_processing()
        processing_task.cancel()
        try:
            await processing_task
        except asyncio.CancelledError:
            pass

async def test_real_time_streaming():
    """실시간 데이터 스트리밍 테스트"""
    print("\n📡 Testing Real-time Data Streaming...")
    
    # 이벤트 버스 생성
    event_bus = EventBus()
    
    # 이벤트 로거 등록
    event_logger = EventLogger()
    event_bus.register_handler(event_logger, list(EventType))
    
    # 실시간 데이터 스트림 생성
    data_stream = RealTimeDataStream(event_bus)
    
    # 이벤트 처리 및 스트리밍 시작
    processing_task = asyncio.create_task(event_bus.start_processing())
    streaming_task = asyncio.create_task(data_stream.start_streaming())
    
    try:
        print("🔄 Streaming market data for 10 seconds...")
        await asyncio.sleep(10)
        
        # 결과 확인
        metrics = event_bus.get_metrics()
        recent_events = event_logger.get_recent_events(10)
        
        print(f"✅ Streaming completed!")
        print(f"📊 Events processed: {metrics['events_processed']}")
        print(f"⚡ Avg processing time: {metrics['average_processing_time']:.3f}s")
        
        print(f"\n📝 Recent Events:")
        for event in recent_events[-5:]:  # 최근 5개만 표시
            print(f"   {event['timestamp'][:19]} - {event['event_type']} - {event['symbol']}")
        
        return metrics['events_processed'] > 0
        
    finally:
        data_stream.stop_streaming()
        event_bus.stop_processing()
        
        streaming_task.cancel()
        processing_task.cancel()
        
        try:
            await streaming_task
        except asyncio.CancelledError:
            pass
        
        try:
            await processing_task
        except asyncio.CancelledError:
            pass

async def test_performance_metrics():
    """성능 메트릭 테스트"""
    print("\n📈 Testing Performance Metrics...")
    
    event_bus = EventBus()
    event_logger = EventLogger()
    event_bus.register_handler(event_logger, list(EventType))
    
    processing_task = asyncio.create_task(event_bus.start_processing())
    
    try:
        # 대량 이벤트 발행
        start_time = time.time()
        
        for i in range(100):
            event = create_price_change_event(
                f"TEST{i%10}", 
                100.0, 
                100.0 + (i % 20 - 10) * 0.1
            )
            await event_bus.publish_event(event)
        
        # 처리 완료 대기
        await asyncio.sleep(3)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        metrics = event_bus.get_metrics()
        
        print(f"⚡ Performance Test Results:")
        print(f"   Total events: 100")
        print(f"   Processing time: {total_time:.2f}s")
        print(f"   Events per second: {100/total_time:.1f}")
        print(f"   Success rate: {metrics['success_rate']:.2%}")
        print(f"   Avg event processing: {metrics['average_processing_time']*1000:.1f}ms")
        
        return metrics['success_rate'] > 0.95
        
    finally:
        event_bus.stop_processing()
        processing_task.cancel()
        try:
            await processing_task
        except asyncio.CancelledError:
            pass

async def main():
    """메인 테스트 함수"""
    print("🚀 Real-time Event System Test Suite")
    print("=" * 60)
    
    # 환경 확인
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"🔑 OpenAI API Key: {'✅ Found' if openai_key else '❌ Not found'}")
    print()
    
    tests = [
        ("Basic Event System", test_basic_event_system),
        ("AI Event Handlers", test_ai_event_handlers),
        ("Real-time Streaming", test_real_time_streaming),
        ("Performance Metrics", test_performance_metrics)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Real-time event system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
