#!/usr/bin/env python3
"""
AI Provider 시스템 테스트 스크립트
다양한 AI 모델 어댑터의 기능을 테스트합니다.
"""

import os
import sys
import time
from typing import Dict, Any

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ai_provider import ModelType, AnalysisRequest
from agents.ai_provider_factory import AIProviderFactory, create_provider_by_name

def test_openai_adapter():
    """OpenAI 어댑터 테스트"""
    print("🤖 Testing OpenAI Adapter...")
    
    try:
        # OpenAI API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            return False
        
        # Provider 생성
        provider = create_provider_by_name("openai_gpt4o_mini")
        
        # 테스트 데이터
        stock_data = {
            "symbol": "AAPL",
            "current_price": 175.50,
            "volume": 50000000,
            "market_cap": 2800000000000,
            "pe_ratio": 28.5
        }
        
        # 분석 요청
        request = AnalysisRequest(
            prompt="이 주식에 대한 간단한 분석을 제공해주세요.",
            stock_data=stock_data,
            max_tokens=500
        )
        
        # 분석 실행
        start_time = time.time()
        response = provider.generate_analysis(request)
        end_time = time.time()
        
        print(f"✅ OpenAI Analysis completed in {end_time - start_time:.2f}s")
        print(f"📊 Model: {response.model_used}")
        print(f"🎯 Tokens: {response.tokens_used}")
        print(f"💰 Cost: ${response.cost_estimate:.4f}")
        print(f"📝 Content preview: {response.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

def test_gemini_adapter():
    """Gemini 어댑터 테스트"""
    print("\n🧠 Testing Gemini Adapter...")
    
    try:
        # Gemini 라이브러리 확인
        try:
            import google.generativeai as genai
        except ImportError:
            print("❌ Google Generative AI library not installed.")
            return False
        
        # API 키 확인
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ Google API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
            return False
        
        # Provider 생성
        provider = create_provider_by_name("google_gemini_flash", api_key)
        
        # 테스트 데이터
        stock_data = {
            "symbol": "GOOGL",
            "current_price": 140.25,
            "volume": 25000000,
            "market_cap": 1800000000000,
            "pe_ratio": 22.8
        }
        
        # 분석 요청
        request = AnalysisRequest(
            prompt="이 주식에 대한 간단한 분석을 제공해주세요.",
            stock_data=stock_data,
            max_tokens=500
        )
        
        # 분석 실행
        start_time = time.time()
        response = provider.generate_analysis(request)
        end_time = time.time()
        
        print(f"✅ Gemini Analysis completed in {end_time - start_time:.2f}s")
        print(f"📊 Model: {response.model_used}")
        print(f"🎯 Tokens: {response.tokens_used}")
        print(f"💰 Cost: ${response.cost_estimate:.4f}")
        print(f"📝 Content preview: {response.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

def test_factory_functionality():
    """팩토리 기능 테스트"""
    print("\n🏭 Testing Factory Functionality...")
    
    try:
        factory = AIProviderFactory()
        
        # 사용 가능한 Provider 목록
        available = factory.get_available_providers()
        print(f"📋 Available providers: {[p.value for p in available]}")
        
        # 가장 저렴한 모델
        cheapest = factory.get_cheapest_provider()
        if cheapest:
            print(f"💰 Cheapest model: {cheapest.value}")
        
        # 가장 성능이 좋은 모델
        most_capable = factory.get_most_capable_provider()
        if most_capable:
            print(f"🚀 Most capable model: {most_capable.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Factory test failed: {e}")
        return False

def test_cost_estimation():
    """비용 추정 테스트"""
    print("\n💰 Testing Cost Estimation...")
    
    try:
        # 다양한 모델의 비용 비교
        test_prompt = "Analyze this stock and provide a detailed investment recommendation with risk assessment."
        
        models_to_test = [
            "openai_gpt4o_mini",
            "google_gemini_flash"
        ]
        
        for model_name in models_to_test:
            try:
                provider = create_provider_by_name(model_name)
                cost = provider.estimate_cost(test_prompt, max_tokens=1000)
                print(f"📊 {model_name}: ${cost:.6f}")
            except Exception as e:
                print(f"❌ {model_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost estimation test failed: {e}")
        return False

def test_enhanced_base_agent():
    """향상된 기본 에이전트 테스트"""
    print("\n🤖 Testing Enhanced Base Agent...")
    
    try:
        from agents.enhanced_base_agent import EnhancedBaseAgent
        
        # 테스트용 에이전트 클래스
        class TestAgent(EnhancedBaseAgent):
            def _build_analysis_prompt(self, symbol, stock_data, context=None):
                return f"Provide a brief analysis of {symbol} stock."
            
            def _get_agent_role(self):
                return "Test Analyst"
        
        # 에이전트 생성
        agent = TestAgent(
            agent_name="test_agent",
            primary_model="openai_gpt4o_mini",
            config={"temperature": 0.7, "max_tokens": 500}
        )
        
        # 테스트 데이터
        stock_data = {
            "symbol": "MSFT",
            "current_price": 380.00,
            "volume": 30000000
        }
        
        # 분석 실행
        result = agent.analyze_stock("MSFT", stock_data)
        
        print(f"✅ Agent analysis completed")
        print(f"📊 Recommendation: {result.get('recommendation')}")
        print(f"🎯 Confidence: {result.get('confidence')}")
        print(f"💰 Cost: ${result.get('cost', 0):.4f}")
        
        # 메트릭 확인
        metrics = agent.get_metrics()
        print(f"📈 Success rate: {metrics['success_rate']:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced base agent test failed: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 AI Provider System Test Suite")
    print("=" * 50)
    
    tests = [
        ("OpenAI Adapter", test_openai_adapter),
        ("Gemini Adapter", test_gemini_adapter),
        ("Factory Functionality", test_factory_functionality),
        ("Cost Estimation", test_cost_estimation),
        ("Enhanced Base Agent", test_enhanced_base_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! AI Provider system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
