#!/usr/bin/env python3
"""
지원되는 AI 모델 테스트 스크립트
실제 지원되는 모델들로 테스트를 수행합니다.
"""

import os
import sys
import time

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ai_provider import ModelType, AnalysisRequest
from agents.ai_provider_factory import create_provider_by_name

def test_supported_openai_models():
    """지원되는 OpenAI 모델 테스트"""
    print("🤖 Testing Supported OpenAI Models...")
    
    # 지원되는 모델들
    supported_models = ["gpt-4.1-mini", "gpt-4.1-nano"]
    
    for model_name in supported_models:
        print(f"\n📊 Testing {model_name}...")
        
        try:
            # Provider 생성
            provider = create_provider_by_name(model_name)
            
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
                prompt="Provide a brief analysis of this stock with a recommendation.",
                stock_data=stock_data,
                max_tokens=300,
                temperature=0.7
            )
            
            # 분석 실행
            start_time = time.time()
            response = provider.generate_analysis(request)
            end_time = time.time()
            
            print(f"✅ {model_name} Analysis completed in {end_time - start_time:.2f}s")
            print(f"📊 Model: {response.model_used}")
            print(f"🎯 Tokens: {response.tokens_used}")
            print(f"💰 Cost: ${response.cost_estimate:.6f}")
            print(f"📝 Content preview: {response.content[:150]}...")
            
            # 신뢰도 점수 확인
            if response.confidence_score:
                print(f"🎯 Confidence: {response.confidence_score:.2%}")
            
        except Exception as e:
            print(f"❌ {model_name} test failed: {e}")

def test_gemini_model():
    """Gemini 모델 테스트"""
    print("\n🧠 Testing Gemini 2.5 Flash...")
    
    try:
        # Gemini 라이브러리 확인
        try:
            import google.generativeai as genai
        except ImportError:
            print("❌ Google Generative AI library not installed.")
            return
        
        # API 키 확인
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ Google API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
            return
        
        # Provider 생성
        provider = create_provider_by_name("gemini-2.5-flash", api_key)
        
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
            prompt="Provide a brief analysis of this stock with a recommendation.",
            stock_data=stock_data,
            max_tokens=300,
            temperature=0.7
        )
        
        # 분석 실행
        start_time = time.time()
        response = provider.generate_analysis(request)
        end_time = time.time()
        
        print(f"✅ Gemini 2.5 Flash Analysis completed in {end_time - start_time:.2f}s")
        print(f"📊 Model: {response.model_used}")
        print(f"🎯 Tokens: {response.tokens_used}")
        print(f"💰 Cost: ${response.cost_estimate:.6f}")
        print(f"📝 Content preview: {response.content[:150]}...")
        
        if response.confidence_score:
            print(f"🎯 Confidence: {response.confidence_score:.2%}")
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")

def test_enhanced_agent_with_supported_models():
    """지원되는 모델로 향상된 에이전트 테스트"""
    print("\n🤖 Testing Enhanced Agent with Supported Models...")
    
    try:
        from agents.enhanced_base_agent import EnhancedBaseAgent
        
        # 테스트용 에이전트 클래스
        class TestAgent(EnhancedBaseAgent):
            def _build_analysis_prompt(self, symbol, stock_data, context=None):
                return f"Analyze {symbol} stock and provide a clear BUY/HOLD/SELL recommendation with confidence level."
            
            def _get_agent_role(self):
                return "Test Stock Analyst"
        
        # 지원되는 모델로 에이전트 생성
        agent = TestAgent(
            agent_name="test_agent",
            primary_model="gpt-4.1-mini",
            fallback_model="gpt-4.1-nano",
            config={"temperature": 0.7, "max_tokens": 400}
        )
        
        # 테스트 데이터
        stock_data = {
            "symbol": "MSFT",
            "current_price": 380.00,
            "volume": 30000000,
            "market_cap": 2900000000000,
            "pe_ratio": 32.1,
            "week_52_high": 420.00,
            "week_52_low": 310.00
        }
        
        # 분석 실행
        result = agent.analyze_stock("MSFT", stock_data)
        
        print(f"✅ Enhanced Agent analysis completed")
        print(f"📊 Agent: {result.get('agent')}")
        print(f"📈 Recommendation: {result.get('recommendation')}")
        print(f"🎯 Confidence: {result.get('confidence', 0):.2%}")
        print(f"💰 Target Price: ${result.get('target_price', 'N/A')}")
        print(f"⚠️  Risk Level: {result.get('risk_level')}")
        print(f"💰 Cost: ${result.get('cost', 0):.6f}")
        print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
        
        # 메트릭 확인
        metrics = agent.get_metrics()
        print(f"\n📈 Agent Metrics:")
        print(f"   Success Rate: {metrics['success_rate']:.2%}")
        print(f"   Total Requests: {metrics['total_requests']}")
        print(f"   Total Cost: ${metrics['total_cost']:.6f}")
        print(f"   Avg Response Time: {metrics['average_response_time']:.2f}s")
        
    except Exception as e:
        print(f"❌ Enhanced agent test failed: {e}")

def test_cost_comparison():
    """지원되는 모델들의 비용 비교"""
    print("\n💰 Cost Comparison of Supported Models...")
    
    test_prompt = "Analyze this stock and provide a detailed investment recommendation with risk assessment and target price."
    
    models_to_test = [
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "gemini-2.5-flash"
    ]
    
    print(f"📝 Test prompt length: {len(test_prompt)} characters")
    print(f"🎯 Max tokens: 1000")
    print()
    
    for model_name in models_to_test:
        try:
            provider = create_provider_by_name(model_name)
            cost = provider.estimate_cost(test_prompt, max_tokens=1000)
            model_info = provider.get_model_info()
            
            print(f"📊 {model_name}:")
            print(f"   💰 Estimated Cost: ${cost:.8f}")
            print(f"   📈 Max Tokens: {model_info.max_tokens:,}")
            print(f"   🏷️  Input Cost: ${model_info.cost_per_input_token:.8f}/token")
            print(f"   🏷️  Output Cost: ${model_info.cost_per_output_token:.8f}/token")
            print()
            
        except Exception as e:
            print(f"❌ {model_name}: {e}")
            print()

def main():
    """메인 테스트 함수"""
    print("🚀 Supported AI Models Test Suite")
    print("=" * 60)
    
    # 환경 확인
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    print("🔑 API Keys Status:")
    print(f"   OpenAI: {'✅ Found' if openai_key else '❌ Not found'}")
    print(f"   Google: {'✅ Found' if google_key else '❌ Not found'}")
    print()
    
    # 테스트 실행
    test_supported_openai_models()
    test_gemini_model()
    test_enhanced_agent_with_supported_models()
    test_cost_comparison()
    
    print("=" * 60)
    print("🎉 Test suite completed!")
    print("💡 Tip: Set OPENAI_API_KEY and GOOGLE_API_KEY environment variables for full testing")

if __name__ == "__main__":
    main()
