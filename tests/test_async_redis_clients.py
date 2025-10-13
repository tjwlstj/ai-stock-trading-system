import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.realtime_data_manager import SmartCache, StockQuote
from backend.app.ai_quality_manager import (
    AIQualityMonitor,
    AIUsageOptimizer,
    AnalysisLevel,
    ValidationResult,
)
from backend.app.cost_optimizer import CostTracker, CostCategory


class AsyncFakeRedis:
    """A minimal async Redis clone for testing."""

    def __init__(self):
        self.kv_store = {}
        self.hash_store = {}
        self.list_store = {}

    async def get(self, key):
        return self.kv_store.get(key)

    async def setex(self, key, ttl, value):
        if isinstance(value, str):
            value = value.encode("utf-8")
        self.kv_store[key] = value
        return True

    async def expire(self, key, ttl):
        return True

    async def hincrby(self, key, field, amount):
        hash_map = self.hash_store.setdefault(key, {})
        current = int(hash_map.get(field, 0))
        current += amount
        hash_map[field] = current
        return current

    async def hincrbyfloat(self, key, field, amount):
        hash_map = self.hash_store.setdefault(key, {})
        current = float(hash_map.get(field, 0.0))
        current += amount
        hash_map[field] = current
        return current

    async def incrbyfloat(self, key, amount):
        raw_value = self.kv_store.get(key, b"0")
        if isinstance(raw_value, bytes):
            current = float(raw_value.decode("utf-8"))
        else:
            current = float(raw_value)
        current += amount
        self.kv_store[key] = str(current).encode("utf-8")
        return current

    async def lpush(self, key, value):
        if isinstance(value, str):
            value = value.encode("utf-8")
        values = self.list_store.setdefault(key, [])
        values.insert(0, value)
        return len(values)

    async def lrange(self, key, start, stop):
        values = self.list_store.get(key, [])
        end_index = None if stop == -1 else stop + 1
        return values[start:end_index]


@pytest.mark.asyncio
async def test_smart_cache_uses_async_redis():
    fake_redis = AsyncFakeRedis()
    cache = SmartCache(redis_client=fake_redis)

    quote = StockQuote(
        symbol="AAPL",
        price=150.0,
        change=1.0,
        change_percent=0.75,
        volume=1_000_000,
        open_price=149.5,
        high=151.0,
        low=148.5,
        previous_close=149.0,
        timestamp=datetime.now() - timedelta(seconds=10),
    )

    await cache.cache_quote(quote)
    cached_quote = await cache.get_cached_quote("AAPL")

    assert cached_quote is not None
    assert cached_quote.symbol == "AAPL"
    assert cached_quote.is_cached is True
    assert cached_quote.cache_age_seconds >= 0


@pytest.mark.asyncio
async def test_ai_quality_monitor_records_metrics_with_fake_redis():
    fake_redis = AsyncFakeRedis()
    monitor = AIQualityMonitor(redis_client=fake_redis)

    await monitor.record_request(
        model="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        response_time=1.2,
        validation_result=ValidationResult.VALID,
        cost=0.01,
    )

    metrics_key = f"ai_metrics:{datetime.now().strftime('%Y-%m-%d')}"
    stored_metrics = fake_redis.hash_store.get(metrics_key, {})

    assert stored_metrics.get("total_requests") == 1
    assert stored_metrics.get("total_tokens") == 150
    assert pytest.approx(stored_metrics.get("total_cost", 0.0), rel=1e-6) == 0.01


@pytest.mark.asyncio
async def test_ai_usage_optimizer_graceful_without_redis():
    optimizer = AIUsageOptimizer(redis_client=None)
    cache_key = optimizer.generate_cache_key("AAPL", AnalysisLevel.QUICK)

    cached = await optimizer.get_cached_analysis(cache_key)
    assert cached is None

    # Should not raise even without Redis configured
    await optimizer.cache_analysis(cache_key, {"result": "ok"}, AnalysisLevel.QUICK)


@pytest.mark.asyncio
async def test_cost_tracker_stores_entries_with_async_redis():
    fake_redis = AsyncFakeRedis()
    tracker = CostTracker(redis_client=fake_redis)

    await tracker.record_infrastructure_cost(
        service="redis",
        amount=Decimal("2.50"),
        description="testing",
    )

    today = datetime.now().date()
    results = await tracker.get_costs_for_period(today, today)

    assert len(results) == 1
    assert results[0].category == CostCategory.INFRASTRUCTURE
    assert results[0].amount == Decimal("2.50")
