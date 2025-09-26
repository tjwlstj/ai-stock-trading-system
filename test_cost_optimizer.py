#!/usr/bin/env python3
"""
비용 최적화 시스템 테스트 스크립트
모델 캐스케이딩, 캐싱, 비용 모니터링 기능을 테스트합니다.
"""

import asyncio
import sys
import os
import time
import logging

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimization.cost_optimizer import (
    CostOptimizer, OptimizationStrategy, CostBudget, 
    create_cost_optimizer, optimized_analysis
)
from agents.ai_provider import AnalysisRequest

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_basic_optimization():
    """기본 최적화 기능 테스트"""
    print("🧪 Testing Basic Cost Optimization...")
    
    # OpenAI API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found. Skipping optimization test.")
        return False
    
    try:
        # 비용 최적화기 생성
        optimizer = create_cost_optimizer(
            strategy="balanced",
            daily_budget=5.0,
            enable_caching=True
        )
        
        # 테스트 요청 생성
        request = AnalysisRequest(
            prompt="Analyze AAPL stock performance and provide investment recommendation.",
            stock_data={
                "symbol": "AAPL",
                "current_price": 175.0,
                "change_percent": 2.5,
                "volume": 45000000
            },
            temperature=0.7,
            max_tokens=500
        )
        
        # 최적화된 분석 수행
        print("📊 Performing optimized analysis...")
        start_time = time.time()
        
        response = await optimizer.optimize_analysis(request)
        
        processing_time = time.time() - start_time
        
        # 결과 확인
        print(f"✅ Analysis completed in {processing_time:.2f}s")
        print(f"📊 Model used: {response.model_used}")
        print(f"💰 Cost: ${response.cost_estimate:.6f}")
        print(f"🎯 Confidence: {response.confidence_score:.2f}")
        print(f"📝 Content preview: {response.content[:100]}...")
        
        # 메트릭 확인
        metrics = optimizer.get_optimization_metrics()
        print(f"\n📈 Optimization Metrics:")
        print(f"   Strategy: {metrics['strategy']}")
        print(f"   Total requests: {metrics['total_requests']}")
        print(f"   Total cost: ${metrics['total_cost']:.6f}")
        print(f"   Budget usage: {metrics['budget_usage']['usage_percent']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic optimization test failed: {e}")
        return False

async def test_caching_system():
    """캐싱 시스템 테스트"""
    print("\n💾 Testing Caching System...")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found. Skipping caching test.")
        return False
    
    try:
        optimizer = create_cost_optimizer(enable_caching=True)
        
        # 동일한 요청을 여러 번 수행
        request = AnalysisRequest(
            prompt="Quick analysis of MSFT stock trends.",
            stock_data={"symbol": "MSFT", "current_price": 350.0},
            temperature=0.5,
            max_tokens=300
        )
        
        print("🔄 Performing first analysis (should miss cache)...")
        start_time = time.time()
        response1 = await optimizer.optimize_analysis(request)
        time1 = time.time() - start_time
        
        print("🔄 Performing second analysis (should hit cache)...")
        start_time = time.time()
        response2 = await optimizer.optimize_analysis(request)
        time2 = time.time() - start_time
        
        # 결과 비교
        print(f"✅ First analysis: {time1:.2f}s, Cost: ${response1.cost_estimate:.6f}")
        print(f"✅ Second analysis: {time2:.2f}s, Cost: ${response2.cost_estimate:.6f}")
        
        # 캐시 메트릭 확인
        metrics = optimizer.get_optimization_metrics()
        cache_metrics = metrics.get('cache_metrics', {})
        
        print(f"\n📊 Cache Performance:")
        print(f"   Hit rate: {cache_metrics.get('hit_rate', 0):.2%}")
        print(f"   Cache size: {cache_metrics.get('cache_size', 0)}")
        print(f"   Cost saved: ${metrics.get('cost_saved', 0):.6f}")
        
        # 캐시가 작동했는지 확인 (두 번째 요청이 더 빨라야 함)
        cache_worked = time2 < time1 * 0.5  # 50% 이상 빨라야 함
        
        if cache_worked:
            print("✅ Caching system working correctly!")
        else:
            print("⚠️  Caching may not be working as expected")
        
        return cache_worked
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False

async def test_model_cascading():
    """모델 캐스케이딩 테스트"""
    print("\n🏗️ Testing Model Cascading...")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found. Skipping cascading test.")
        return False
    
    try:
        # 다른 전략으로 최적화기 생성
        strategies = [
            ("cost_first", "비용 우선"),
            ("balanced", "균형"),
            ("performance_first", "성능 우선")
        ]
        
        results = []
        
        for strategy_name, strategy_desc in strategies:
            print(f"\n🎯 Testing {strategy_desc} strategy...")
            
            optimizer = create_cost_optimizer(strategy=strategy_name)
            
            # 중요도가 다른 요청들 테스트
            requests = [
                # 낮은 중요도 (작은 변동)
                AnalysisRequest(
                    prompt="Analyze minor price movement in GOOGL.",
                    stock_data={"symbol": "GOOGL", "change_percent": 0.5, "volume": 15000000},
                    max_tokens=200
                ),
                # 높은 중요도 (큰 변동)
                AnalysisRequest(
                    prompt="Analyze significant price surge in TSLA.",
                    stock_data={"symbol": "TSLA", "change_percent": 8.0, "volume": 80000000},
                    max_tokens=500
                )
            ]
            
            strategy_results = []
            
            for i, request in enumerate(requests):
                context = {
                    "priority": "low" if i == 0 else "high",
                    "market_hours": True
                }
                
                response = await optimizer.optimize_analysis(request, context)
                strategy_results.append({
                    "importance": "low" if i == 0 else "high",
                    "model": response.model_used,
                    "cost": response.cost_estimate
                })
            
            results.append((strategy_name, strategy_desc, strategy_results))
        
        # 결과 분석
        print(f"\n📊 Model Selection Results:")
        for strategy_name, strategy_desc, strategy_results in results:
            print(f"\n🎯 {strategy_desc} ({strategy_name}):")
            for result in strategy_results:
                print(f"   {result['importance']} importance: {result['model']} (${result['cost']:.6f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Model cascading test failed: {e}")
        return False

async def test_budget_management():
    """예산 관리 테스트"""
    print("\n💰 Testing Budget Management...")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found. Skipping budget test.")
        return False
    
    try:
        # 낮은 예산으로 최적화기 생성
        budget = CostBudget(
            daily_limit=0.01,  # $0.01 제한
            per_request_limit=0.005,  # 요청당 $0.005 제한
            alert_threshold=0.5  # 50%에서 경고
        )
        
        optimizer = CostOptimizer(
            strategy=OptimizationStrategy.COST_FIRST,
            budget=budget,
            enable_caching=True
        )
        
        # 여러 요청 수행하여 예산 한도 테스트
        request = AnalysisRequest(
            prompt="Brief analysis of stock market trends.",
            stock_data={"symbol": "SPY"},
            max_tokens=100  # 작은 토큰으로 비용 절약
        )
        
        successful_requests = 0
        total_cost = 0.0
        
        for i in range(5):  # 5번 시도
            try:
                print(f"📊 Request {i+1}/5...")
                response = await optimizer.optimize_analysis(request)
                successful_requests += 1
                total_cost += response.cost_estimate
                
                metrics = optimizer.get_optimization_metrics()
                budget_usage = metrics['budget_usage']['usage_percent']
                
                print(f"   ✅ Success - Budget usage: {budget_usage:.1f}%")
                
                if budget_usage > 90:  # 90% 이상 사용시 중단
                    print("   ⚠️  Budget nearly exhausted, stopping test")
                    break
                    
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
                break
        
        print(f"\n📊 Budget Test Results:")
        print(f"   Successful requests: {successful_requests}/5")
        print(f"   Total cost: ${total_cost:.6f}")
        print(f"   Budget limit: ${budget.daily_limit:.6f}")
        print(f"   Budget protection: {'✅ Working' if successful_requests < 5 else '⚠️  May need adjustment'}")
        
        return successful_requests > 0
        
    except Exception as e:
        print(f"❌ Budget management test failed: {e}")
        return False

async def test_performance_metrics():
    """성능 메트릭 테스트"""
    print("\n📈 Testing Performance Metrics...")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found. Skipping metrics test.")
        return False
    
    try:
        optimizer = create_cost_optimizer(strategy="balanced")
        
        # 여러 요청으로 메트릭 수집
        requests = [
            AnalysisRequest(
                prompt=f"Analyze stock {symbol} performance.",
                stock_data={"symbol": symbol, "current_price": 100 + i * 10},
                max_tokens=200
            )
            for i, symbol in enumerate(["AAPL", "GOOGL", "MSFT"])
        ]
        
        print("🔄 Performing multiple analyses for metrics...")
        
        for i, request in enumerate(requests):
            print(f"   📊 Analysis {i+1}/3...")
            await optimizer.optimize_analysis(request)
        
        # 최종 메트릭 확인
        metrics = optimizer.get_optimization_metrics()
        
        print(f"\n📊 Final Performance Metrics:")
        print(f"   Strategy: {metrics['strategy']}")
        print(f"   Total requests: {metrics['total_requests']}")
        print(f"   Cache hit rate: {metrics['cache_hit_rate']:.2%}")
        print(f"   Total cost: ${metrics['total_cost']:.6f}")
        print(f"   Cost saved: ${metrics['cost_saved']:.6f}")
        print(f"   Savings rate: {metrics['savings_rate']:.2%}")
        print(f"   Avg response time: {metrics['average_response_time']:.2f}s")
        
        print(f"\n🤖 Model Usage:")
        for model, count in metrics['model_usage'].items():
            print(f"   {model}: {count} requests")
        
        return metrics['total_requests'] > 0
        
    except Exception as e:
        print(f"❌ Performance metrics test failed: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 Cost Optimization System Test Suite")
    print("=" * 60)
    
    # 환경 확인
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"🔑 OpenAI API Key: {'✅ Found' if openai_key else '❌ Not found'}")
    print()
    
    tests = [
        ("Basic Optimization", test_basic_optimization),
        ("Caching System", test_caching_system),
        ("Model Cascading", test_model_cascading),
        ("Budget Management", test_budget_management),
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
        print("🎉 All tests passed! Cost optimization system is working perfectly.")
    elif passed > len(results) // 2:
        print("✅ Most tests passed. Cost optimization system is mostly functional.")
    else:
        print("⚠️  Many tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
