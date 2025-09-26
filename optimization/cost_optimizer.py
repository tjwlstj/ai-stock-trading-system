"""
비용 최적화 시스템
모델 캐스케이딩, 캐싱, 비용 모니터링을 통한 AI 분석 비용 최적화
"""

import time
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.ai_provider import AnalysisRequest, AnalysisResponse, ModelType
from agents.ai_provider_factory import create_provider_by_name, AIProviderFactory

logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """최적화 전략"""
    COST_FIRST = "cost_first"  # 비용 우선
    PERFORMANCE_FIRST = "performance_first"  # 성능 우선
    BALANCED = "balanced"  # 균형
    ADAPTIVE = "adaptive"  # 적응형

@dataclass
class CostBudget:
    """비용 예산 설정"""
    daily_limit: float = 10.0  # 일일 한도 (USD)
    per_request_limit: float = 0.50  # 요청당 한도 (USD)
    alert_threshold: float = 0.80  # 경고 임계값 (80%)
    current_daily_spend: float = 0.0
    last_reset: datetime = None

@dataclass
class CacheEntry:
    """캐시 엔트리"""
    key: str
    response: AnalysisResponse
    timestamp: float
    access_count: int = 0
    cost_saved: float = 0.0

class InMemoryCache:
    """인메모리 캐시 시스템"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, CacheEntry] = {}
        self.access_times: Dict[str, float] = {}
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_cost_saved": 0.0
        }
    
    def _generate_key(self, request: AnalysisRequest, model_name: str) -> str:
        """캐시 키 생성"""
        # 요청의 핵심 내용을 해시화
        key_data = {
            "prompt": request.prompt[:500],  # 프롬프트 일부만 사용
            "stock_data": request.stock_data,
            "model": model_name,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, request: AnalysisRequest, model_name: str) -> Optional[AnalysisResponse]:
        """캐시에서 응답 조회"""
        key = self._generate_key(request, model_name)
        
        if key not in self.cache:
            self.metrics["misses"] += 1
            return None
        
        entry = self.cache[key]
        
        # TTL 확인
        if time.time() - entry.timestamp > self.ttl_seconds:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            self.metrics["misses"] += 1
            return None
        
        # 캐시 히트
        entry.access_count += 1
        self.access_times[key] = time.time()
        self.metrics["hits"] += 1
        
        logger.debug(f"Cache hit for key: {key[:8]}...")
        return entry.response
    
    def put(self, request: AnalysisRequest, model_name: str, response: AnalysisResponse):
        """캐시에 응답 저장"""
        key = self._generate_key(request, model_name)
        
        # 캐시 크기 제한 확인
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        entry = CacheEntry(
            key=key,
            response=response,
            timestamp=time.time()
        )
        
        self.cache[key] = entry
        self.access_times[key] = time.time()
        
        logger.debug(f"Cache stored for key: {key[:8]}...")
    
    def _evict_lru(self):
        """LRU 방식으로 캐시 엔트리 제거"""
        if not self.access_times:
            return
        
        # 가장 오래된 접근 시간을 가진 키 찾기
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
        self.metrics["evictions"] += 1
        
        logger.debug(f"Cache evicted key: {oldest_key[:8]}...")
    
    def get_metrics(self) -> Dict[str, Any]:
        """캐시 메트릭 반환"""
        total_requests = self.metrics["hits"] + self.metrics["misses"]
        hit_rate = self.metrics["hits"] / max(total_requests, 1)
        
        return {
            **self.metrics,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache),
            "max_size": self.max_size
        }

class ModelCascade:
    """모델 캐스케이딩 시스템"""
    
    def __init__(self, strategy: OptimizationStrategy = OptimizationStrategy.BALANCED):
        self.strategy = strategy
        self.factory = AIProviderFactory()
        
        # 모델 계층 정의
        self.model_tiers = {
            "tier1": ["gpt-4.1-nano"],  # 경량 모델
            "tier2": ["gpt-4.1-mini"],  # 중간 성능 모델
            "tier3": ["gpt-4.1-mini"]   # 고성능 모델 (현재는 동일)
        }
        
        # 전략별 설정
        self.strategy_configs = {
            OptimizationStrategy.COST_FIRST: {
                "tier1_threshold": 0.3,  # 낮은 임계값 (더 많이 tier1 사용)
                "tier2_threshold": 0.7,
                "confidence_requirement": 0.6
            },
            OptimizationStrategy.PERFORMANCE_FIRST: {
                "tier1_threshold": 0.8,  # 높은 임계값 (tier3 더 많이 사용)
                "tier2_threshold": 0.9,
                "confidence_requirement": 0.8
            },
            OptimizationStrategy.BALANCED: {
                "tier1_threshold": 0.5,
                "tier2_threshold": 0.8,
                "confidence_requirement": 0.7
            }
        }
    
    def select_model(self, request: AnalysisRequest, context: Dict[str, Any] = None) -> str:
        """요청에 따라 최적 모델 선택"""
        config = self.strategy_configs[self.strategy]
        
        # 컨텍스트 기반 중요도 계산
        importance_score = self._calculate_importance(request, context)
        
        if importance_score < config["tier1_threshold"]:
            return self.model_tiers["tier1"][0]
        elif importance_score < config["tier2_threshold"]:
            return self.model_tiers["tier2"][0]
        else:
            return self.model_tiers["tier3"][0]
    
    def _calculate_importance(self, request: AnalysisRequest, context: Dict[str, Any] = None) -> float:
        """요청의 중요도 계산"""
        importance = 0.5  # 기본값
        
        # 주식 데이터 기반 중요도
        if request.stock_data:
            # 가격 변동이 클수록 중요
            change_percent = abs(request.stock_data.get("change_percent", 0))
            if change_percent > 5:
                importance += 0.3
            elif change_percent > 2:
                importance += 0.2
            
            # 거래량이 많을수록 중요
            volume = request.stock_data.get("volume", 0)
            if volume > 50000000:
                importance += 0.2
            elif volume > 20000000:
                importance += 0.1
        
        # 컨텍스트 기반 중요도
        if context:
            # 이벤트 우선순위
            priority = context.get("priority", "medium")
            if priority == "critical":
                importance += 0.4
            elif priority == "high":
                importance += 0.2
            
            # 시장 시간 (장중이면 더 중요)
            if context.get("market_hours", False):
                importance += 0.1
        
        return min(importance, 1.0)

class CostOptimizer:
    """비용 최적화 메인 클래스"""
    
    def __init__(self, 
                 strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
                 budget: CostBudget = None,
                 enable_caching: bool = True):
        self.strategy = strategy
        self.budget = budget or CostBudget()
        self.enable_caching = enable_caching
        
        # 구성 요소 초기화
        self.cache = InMemoryCache() if enable_caching else None
        self.cascade = ModelCascade(strategy)
        self.factory = AIProviderFactory()
        
        # 메트릭
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cost_saved_by_cache": 0.0,
            "cost_saved_by_cascade": 0.0,
            "total_cost": 0.0,
            "model_usage": defaultdict(int),
            "average_response_time": 0.0
        }
        
        # 예산 초기화
        self._reset_daily_budget_if_needed()
    
    async def optimize_analysis(self, 
                              request: AnalysisRequest, 
                              context: Dict[str, Any] = None) -> AnalysisResponse:
        """최적화된 AI 분석 수행"""
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # 1. 캐시 확인
            if self.cache:
                cached_response = self._check_cache(request)
                if cached_response:
                    self.metrics["cache_hits"] += 1
                    processing_time = time.time() - start_time
                    self._update_response_time(processing_time)
                    return cached_response
            
            # 2. 예산 확인
            if not self._check_budget(request):
                raise Exception("Daily budget exceeded")
            
            # 3. 모델 선택 (캐스케이딩)
            selected_model = self.cascade.select_model(request, context)
            
            # 4. AI 분석 수행
            provider = create_provider_by_name(selected_model)
            response = provider.generate_analysis(request)
            
            # 5. 비용 추적
            self._track_cost(response.cost_estimate, selected_model)
            
            # 6. 캐시 저장
            if self.cache:
                self.cache.put(request, selected_model, response)
            
            # 7. 메트릭 업데이트
            processing_time = time.time() - start_time
            self._update_response_time(processing_time)
            
            logger.info(f"Optimized analysis completed with {selected_model} in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise
    
    def _check_cache(self, request: AnalysisRequest) -> Optional[AnalysisResponse]:
        """캐시 확인"""
        # 여러 모델에 대해 캐시 확인
        for tier_models in self.cascade.model_tiers.values():
            for model in tier_models:
                cached = self.cache.get(request, model)
                if cached:
                    # 캐시된 응답의 비용 절약 계산
                    provider = create_provider_by_name(model)
                    estimated_cost = provider.estimate_cost(request.prompt, request.max_tokens)
                    self.metrics["cost_saved_by_cache"] += estimated_cost
                    return cached
        return None
    
    def _check_budget(self, request: AnalysisRequest) -> bool:
        """예산 확인"""
        self._reset_daily_budget_if_needed()
        
        # 예상 비용 계산
        selected_model = self.cascade.select_model(request)
        provider = create_provider_by_name(selected_model)
        estimated_cost = provider.estimate_cost(request.prompt, request.max_tokens)
        
        # 예산 한도 확인
        if (self.budget.current_daily_spend + estimated_cost > self.budget.daily_limit or
            estimated_cost > self.budget.per_request_limit):
            return False
        
        return True
    
    def _track_cost(self, cost: float, model: str):
        """비용 추적"""
        self.budget.current_daily_spend += cost
        self.metrics["total_cost"] += cost
        self.metrics["model_usage"][model] += 1
        
        # 경고 임계값 확인
        if (self.budget.current_daily_spend / self.budget.daily_limit > 
            self.budget.alert_threshold):
            logger.warning(f"Budget alert: {self.budget.current_daily_spend:.4f}/"
                         f"{self.budget.daily_limit:.2f} USD used")
    
    def _reset_daily_budget_if_needed(self):
        """일일 예산 리셋 확인"""
        now = datetime.now()
        
        if (self.budget.last_reset is None or 
            now.date() > self.budget.last_reset.date()):
            self.budget.current_daily_spend = 0.0
            self.budget.last_reset = now
            logger.info("Daily budget reset")
    
    def _update_response_time(self, processing_time: float):
        """평균 응답 시간 업데이트"""
        total_time = (self.metrics["average_response_time"] * 
                     (self.metrics["total_requests"] - 1) + processing_time)
        self.metrics["average_response_time"] = total_time / self.metrics["total_requests"]
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """최적화 메트릭 반환"""
        cache_metrics = self.cache.get_metrics() if self.cache else {}
        
        total_cost_saved = (self.metrics["cost_saved_by_cache"] + 
                           self.metrics["cost_saved_by_cascade"])
        
        return {
            "strategy": self.strategy.value,
            "total_requests": self.metrics["total_requests"],
            "cache_hit_rate": cache_metrics.get("hit_rate", 0),
            "total_cost": self.metrics["total_cost"],
            "cost_saved": total_cost_saved,
            "savings_rate": total_cost_saved / max(self.metrics["total_cost"] + total_cost_saved, 0.01),
            "average_response_time": self.metrics["average_response_time"],
            "model_usage": dict(self.metrics["model_usage"]),
            "budget_usage": {
                "daily_spend": self.budget.current_daily_spend,
                "daily_limit": self.budget.daily_limit,
                "usage_percent": (self.budget.current_daily_spend / self.budget.daily_limit) * 100
            },
            "cache_metrics": cache_metrics
        }
    
    def adjust_strategy(self, new_strategy: OptimizationStrategy):
        """최적화 전략 변경"""
        old_strategy = self.strategy
        self.strategy = new_strategy
        self.cascade.strategy = new_strategy
        logger.info(f"Strategy changed from {old_strategy.value} to {new_strategy.value}")

# 편의 함수들
def create_cost_optimizer(strategy: str = "balanced", 
                         daily_budget: float = 10.0,
                         enable_caching: bool = True) -> CostOptimizer:
    """비용 최적화기 생성"""
    strategy_enum = OptimizationStrategy(strategy)
    budget = CostBudget(daily_limit=daily_budget)
    
    return CostOptimizer(
        strategy=strategy_enum,
        budget=budget,
        enable_caching=enable_caching
    )

async def optimized_analysis(request: AnalysisRequest, 
                           optimizer: CostOptimizer = None,
                           context: Dict[str, Any] = None) -> AnalysisResponse:
    """최적화된 분석 수행 (편의 함수)"""
    if optimizer is None:
        optimizer = create_cost_optimizer()
    
    return await optimizer.optimize_analysis(request, context)
