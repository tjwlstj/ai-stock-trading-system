"""
AI Quality Management System for Stock Trading Analysis
Provides comprehensive AI response validation, quality monitoring, and cost optimization
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
import hashlib
import asyncio
from functools import lru_cache
import re

from pydantic import BaseModel, validator
try:
    from redis.asyncio import Redis as AsyncRedis
except (ImportError, ModuleNotFoundError):  # pragma: no cover - optional dependency
    AsyncRedis = None  # type: ignore

if TYPE_CHECKING:  # pragma: no cover - typing only
    from redis.asyncio import Redis as AsyncRedis
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class AnalysisLevel(str, Enum):
    """Analysis complexity levels for cost optimization"""
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"

class ValidationResult(str, Enum):
    """AI response validation results"""
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"

@dataclass
class AIUsageMetrics:
    """AI API usage tracking"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_reset: datetime = None

class AIResponseValidator:
    """Validates AI responses for quality and consistency"""
    
    def __init__(self):
        self.validation_rules = {
            'recommendation': ['BUY', 'SELL', 'HOLD', 'STRONG_BUY', 'STRONG_SELL'],
            'confidence_range': (0.0, 1.0),
            'required_fields': ['recommendation', 'confidence', 'reasoning'],
            'max_reasoning_length': 1000,
            'min_confidence_threshold': 0.1
        }
    
    def validate_response(self, response: Dict[str, Any], stock_data: Dict[str, Any]) -> Tuple[ValidationResult, List[str]]:
        """Comprehensive AI response validation"""
        issues = []
        
        # 1. Structure validation
        structure_issues = self._validate_structure(response)
        issues.extend(structure_issues)
        
        # 2. Content validation
        content_issues = self._validate_content(response)
        issues.extend(content_issues)
        
        # 3. Consistency validation with stock data
        consistency_issues = self._validate_consistency(response, stock_data)
        issues.extend(consistency_issues)
        
        # 4. Logical validation
        logic_issues = self._validate_logic(response)
        issues.extend(logic_issues)
        
        # Determine overall validation result
        if not issues:
            return ValidationResult.VALID, []
        elif any("critical" in issue.lower() for issue in issues):
            return ValidationResult.INVALID, issues
        elif any("review" in issue.lower() for issue in issues):
            return ValidationResult.REQUIRES_HUMAN_REVIEW, issues
        else:
            return ValidationResult.WARNING, issues
    
    def _validate_structure(self, response: Dict[str, Any]) -> List[str]:
        """Validate response structure"""
        issues = []
        
        # Check required fields
        for field in self.validation_rules['required_fields']:
            if field not in response:
                issues.append(f"Critical: Missing required field '{field}'")
        
        # Check data types
        if 'confidence' in response:
            try:
                confidence = float(response['confidence'])
                if not (self.validation_rules['confidence_range'][0] <= confidence <= self.validation_rules['confidence_range'][1]):
                    issues.append(f"Warning: Confidence {confidence} outside valid range")
            except (ValueError, TypeError):
                issues.append("Critical: Confidence must be a number")
        
        # Check recommendation format
        if 'recommendation' in response:
            rec = str(response['recommendation']).upper()
            if rec not in self.validation_rules['recommendation']:
                issues.append(f"Warning: Unusual recommendation '{rec}'")
        
        return issues
    
    def _validate_content(self, response: Dict[str, Any]) -> List[str]:
        """Validate response content quality"""
        issues = []
        
        # Check reasoning length and quality
        if 'reasoning' in response:
            reasoning = str(response['reasoning'])
            if len(reasoning) < 50:
                issues.append("Warning: Reasoning too brief, may lack depth")
            elif len(reasoning) > self.validation_rules['max_reasoning_length']:
                issues.append("Warning: Reasoning too verbose")
            
            # Check for generic/template responses
            generic_phrases = [
                "based on the analysis",
                "considering the factors",
                "after careful review",
                "taking into account"
            ]
            if any(phrase in reasoning.lower() for phrase in generic_phrases):
                issues.append("Warning: Response may be too generic")
        
        # Check confidence threshold
        if 'confidence' in response:
            confidence = float(response.get('confidence', 0))
            if confidence < self.validation_rules['min_confidence_threshold']:
                issues.append("Critical: Confidence too low for reliable analysis")
        
        return issues
    
    def _validate_consistency(self, response: Dict[str, Any], stock_data: Dict[str, Any]) -> List[str]:
        """Validate consistency with actual stock data"""
        issues = []
        
        if not stock_data:
            return issues
        
        recommendation = response.get('recommendation', '').upper()
        confidence = float(response.get('confidence', 0))
        price_change = stock_data.get('change_percent', 0)
        
        # Check for logical inconsistencies
        if recommendation in ['BUY', 'STRONG_BUY'] and price_change < -10:
            if confidence > 0.7:
                issues.append("Review: High confidence BUY recommendation despite significant price drop")
        
        if recommendation in ['SELL', 'STRONG_SELL'] and price_change > 10:
            if confidence > 0.7:
                issues.append("Review: High confidence SELL recommendation despite significant price gain")
        
        # Check for extreme confidence with neutral recommendation
        if recommendation == 'HOLD' and confidence > 0.9:
            issues.append("Warning: Very high confidence for HOLD recommendation seems unusual")
        
        return issues
    
    def _validate_logic(self, response: Dict[str, Any]) -> List[str]:
        """Validate logical consistency within the response"""
        issues = []
        
        reasoning = response.get('reasoning', '').lower()
        recommendation = response.get('recommendation', '').upper()
        confidence = float(response.get('confidence', 0))
        
        # Check for contradictions in reasoning
        positive_indicators = ['growth', 'increase', 'strong', 'positive', 'bullish', 'upward']
        negative_indicators = ['decline', 'decrease', 'weak', 'negative', 'bearish', 'downward']
        
        positive_count = sum(1 for word in positive_indicators if word in reasoning)
        negative_count = sum(1 for word in negative_indicators if word in reasoning)
        
        if recommendation in ['BUY', 'STRONG_BUY'] and negative_count > positive_count:
            issues.append("Warning: BUY recommendation but reasoning contains more negative indicators")
        
        if recommendation in ['SELL', 'STRONG_SELL'] and positive_count > negative_count:
            issues.append("Warning: SELL recommendation but reasoning contains more positive indicators")
        
        return issues

class AIUsageOptimizer:
    """Optimizes AI API usage for cost efficiency"""
    
    def __init__(self, redis_client: Optional["AsyncRedis"] = None):
        self.redis_client = redis_client
        self.cache_ttl = {
            AnalysisLevel.QUICK: 3600,      # 1 hour
            AnalysisLevel.STANDARD: 1800,   # 30 minutes
            AnalysisLevel.COMPREHENSIVE: 900 # 15 minutes
        }
        self.token_costs = {
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006}  # per 1K tokens
        }
    
    def generate_cache_key(self, symbol: str, analysis_level: AnalysisLevel, additional_params: Dict = None) -> str:
        """Generate cache key for analysis results"""
        params_str = json.dumps(additional_params or {}, sort_keys=True)
        content = f"{symbol}:{analysis_level.value}:{params_str}"
        return f"ai_analysis:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis result"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if isinstance(cached_data, bytes):
                cached_data = cached_data.decode("utf-8")
            if cached_data:
                result = json.loads(cached_data)
                result['is_cached'] = True
                result['cache_hit'] = True
                return result
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        
        return None
    
    async def cache_analysis(self, cache_key: str, analysis: Dict[str, Any], level: AnalysisLevel):
        """Cache analysis result"""
        if not self.redis_client:
            return
        
        try:
            analysis['cached_at'] = datetime.now().isoformat()
            analysis['cache_ttl'] = self.cache_ttl[level]
            
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl[level],
                json.dumps(analysis)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    def optimize_prompt(self, base_prompt: str, level: AnalysisLevel) -> str:
        """Optimize prompt based on analysis level"""
        
        if level == AnalysisLevel.QUICK:
            return f"""
            Analyze {base_prompt} briefly. Respond in JSON format only:
            {{
                "recommendation": "BUY/SELL/HOLD",
                "confidence": 0.0-1.0,
                "reasoning": "Brief 2-3 sentence explanation",
                "key_factor": "Single most important factor"
            }}
            """
        
        elif level == AnalysisLevel.STANDARD:
            return f"""
            Analyze {base_prompt}. Respond in JSON format:
            {{
                "recommendation": "BUY/SELL/HOLD/STRONG_BUY/STRONG_SELL",
                "confidence": 0.0-1.0,
                "reasoning": "Detailed explanation (max 200 words)",
                "key_factors": ["factor1", "factor2", "factor3"],
                "risks": ["risk1", "risk2"],
                "price_target": "estimated target price or null"
            }}
            """
        
        else:  # COMPREHENSIVE
            return f"""
            Provide comprehensive analysis for {base_prompt}. Respond in JSON format:
            {{
                "recommendation": "BUY/SELL/HOLD/STRONG_BUY/STRONG_SELL",
                "confidence": 0.0-1.0,
                "reasoning": "Comprehensive analysis",
                "technical_analysis": "Technical indicators summary",
                "fundamental_analysis": "Fundamental factors summary",
                "key_factors": ["factor1", "factor2", "factor3", "factor4"],
                "risks": ["risk1", "risk2", "risk3"],
                "opportunities": ["opportunity1", "opportunity2"],
                "price_target": "estimated target price or null",
                "time_horizon": "short/medium/long term"
            }}
            """
    
    def estimate_token_usage(self, prompt: str, expected_response_length: int = 200) -> Dict[str, int]:
        """Estimate token usage for cost calculation"""
        # Rough estimation: 1 token ≈ 4 characters for English text
        input_tokens = len(prompt) // 4
        output_tokens = expected_response_length // 4
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens
        }
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate API call cost"""
        if model not in self.token_costs:
            return 0.0
        
        costs = self.token_costs[model]
        input_cost = (input_tokens / 1000) * costs['input']
        output_cost = (output_tokens / 1000) * costs['output']
        
        return input_cost + output_cost

class AIQualityMonitor:
    """Monitors AI response quality and system performance"""
    
    def __init__(self, redis_client: Optional["AsyncRedis"] = None):
        self.redis_client = redis_client
        self.metrics = AIUsageMetrics()
        self.quality_thresholds = {
            'min_confidence': 0.3,
            'max_response_time': 30.0,
            'max_error_rate': 0.05,
            'min_validation_score': 0.7
        }
    
    async def record_request(self, 
                           model: str,
                           input_tokens: int,
                           output_tokens: int,
                           response_time: float,
                           validation_result: ValidationResult,
                           cost: float):
        """Record AI API request metrics"""
        
        self.metrics.total_requests += 1
        self.metrics.total_tokens += input_tokens + output_tokens
        self.metrics.total_cost += cost
        
        # Update average response time
        self.metrics.average_response_time = (
            (self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time) /
            self.metrics.total_requests
        )
        
        if validation_result == ValidationResult.INVALID:
            self.metrics.failed_requests += 1
        
        # Store in Redis for persistence
        if self.redis_client:
            try:
                metrics_key = f"ai_metrics:{datetime.now().strftime('%Y-%m-%d')}"
                await self.redis_client.hincrby(metrics_key, 'total_requests', 1)
                await self.redis_client.hincrby(metrics_key, 'total_tokens', input_tokens + output_tokens)
                await self.redis_client.hincrbyfloat(metrics_key, 'total_cost', cost)
                await self.redis_client.expire(metrics_key, 86400 * 30)  # Keep for 30 days
            except Exception as e:
                logger.warning(f"Failed to store metrics: {e}")
    
    def get_quality_score(self, validation_result: ValidationResult, confidence: float, response_time: float) -> float:
        """Calculate overall quality score (0-1)"""
        
        # Base score from validation
        validation_scores = {
            ValidationResult.VALID: 1.0,
            ValidationResult.WARNING: 0.7,
            ValidationResult.REQUIRES_HUMAN_REVIEW: 0.5,
            ValidationResult.INVALID: 0.0
        }
        
        base_score = validation_scores[validation_result]
        
        # Confidence factor (0.5 to 1.0 multiplier)
        confidence_factor = 0.5 + (confidence * 0.5)
        
        # Response time factor (penalty for slow responses)
        time_factor = max(0.5, 1.0 - (response_time / 60.0))  # Penalty after 60 seconds
        
        return base_score * confidence_factor * time_factor
    
    def should_trigger_alert(self) -> Tuple[bool, List[str]]:
        """Check if quality metrics warrant an alert"""
        alerts = []
        
        if self.metrics.total_requests > 0:
            error_rate = self.metrics.failed_requests / self.metrics.total_requests
            if error_rate > self.quality_thresholds['max_error_rate']:
                alerts.append(f"High error rate: {error_rate:.2%}")
        
        if self.metrics.average_response_time > self.quality_thresholds['max_response_time']:
            alerts.append(f"Slow response time: {self.metrics.average_response_time:.1f}s")
        
        # Daily cost check
        daily_cost_limit = 50.0  # $50 per day
        if self.metrics.total_cost > daily_cost_limit:
            alerts.append(f"Daily cost limit exceeded: ${self.metrics.total_cost:.2f}")
        
        return len(alerts) > 0, alerts
    
    async def get_daily_summary(self) -> Dict[str, Any]:
        """Get daily usage summary"""
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_requests': self.metrics.total_requests,
            'total_tokens': self.metrics.total_tokens,
            'total_cost': round(self.metrics.total_cost, 4),
            'average_response_time': round(self.metrics.average_response_time, 2),
            'error_rate': round(self.metrics.failed_requests / max(1, self.metrics.total_requests), 4),
            'estimated_monthly_cost': round(self.metrics.total_cost * 30, 2)
        }

class BatchAnalyzer:
    """Handles batch analysis for multiple stocks efficiently"""
    
    def __init__(self, ai_client, optimizer: AIUsageOptimizer):
        self.ai_client = ai_client
        self.optimizer = optimizer
        self.max_batch_size = 10  # Maximum stocks per batch request
    
    async def analyze_portfolio(self, symbols: List[str], level: AnalysisLevel = AnalysisLevel.STANDARD) -> Dict[str, Any]:
        """Analyze multiple stocks in batches for efficiency"""
        
        if len(symbols) <= self.max_batch_size:
            return await self._analyze_single_batch(symbols, level)
        
        # Split into multiple batches
        results = {}
        for i in range(0, len(symbols), self.max_batch_size):
            batch = symbols[i:i + self.max_batch_size]
            batch_results = await self._analyze_single_batch(batch, level)
            results.update(batch_results)
        
        return results
    
    async def _analyze_single_batch(self, symbols: List[str], level: AnalysisLevel) -> Dict[str, Any]:
        """Analyze a single batch of stocks"""
        
        # Check cache for each symbol
        cached_results = {}
        uncached_symbols = []
        
        for symbol in symbols:
            cache_key = self.optimizer.generate_cache_key(symbol, level)
            cached = await self.optimizer.get_cached_analysis(cache_key)
            if cached:
                cached_results[symbol] = cached
            else:
                uncached_symbols.append(symbol)
        
        # Batch analyze uncached symbols
        if uncached_symbols:
            batch_prompt = self._create_batch_prompt(uncached_symbols, level)
            
            try:
                # This would integrate with your actual AI client
                batch_response = await self.ai_client.analyze_batch(batch_prompt)
                
                # Parse and cache results
                for symbol in uncached_symbols:
                    if symbol in batch_response:
                        cache_key = self.optimizer.generate_cache_key(symbol, level)
                        await self.optimizer.cache_analysis(cache_key, batch_response[symbol], level)
                        cached_results[symbol] = batch_response[symbol]
            
            except Exception as e:
                logger.error(f"Batch analysis failed: {e}")
                # Fallback to individual analysis
                for symbol in uncached_symbols:
                    try:
                        individual_result = await self._analyze_individual(symbol, level)
                        cached_results[symbol] = individual_result
                    except Exception as individual_error:
                        logger.error(f"Individual analysis failed for {symbol}: {individual_error}")
                        cached_results[symbol] = {
                            'error': str(individual_error),
                            'recommendation': 'HOLD',
                            'confidence': 0.1
                        }
        
        return cached_results
    
    def _create_batch_prompt(self, symbols: List[str], level: AnalysisLevel) -> str:
        """Create optimized prompt for batch analysis"""
        
        symbols_str = ', '.join(symbols)
        
        if level == AnalysisLevel.QUICK:
            return f"""
            Analyze these stocks briefly: {symbols_str}
            
            Respond in JSON format:
            {{
                "SYMBOL1": {{"recommendation": "BUY/SELL/HOLD", "confidence": 0.0-1.0, "reasoning": "brief"}},
                "SYMBOL2": {{"recommendation": "BUY/SELL/HOLD", "confidence": 0.0-1.0, "reasoning": "brief"}},
                ...
            }}
            """
        
        return f"""
        Analyze these stocks: {symbols_str}
        
        For each stock, provide:
        {{
            "SYMBOL": {{
                "recommendation": "BUY/SELL/HOLD/STRONG_BUY/STRONG_SELL",
                "confidence": 0.0-1.0,
                "reasoning": "explanation",
                "key_factors": ["factor1", "factor2"],
                "risks": ["risk1", "risk2"]
            }}
        }}
        """
    
    async def _analyze_individual(self, symbol: str, level: AnalysisLevel) -> Dict[str, Any]:
        """Fallback individual analysis"""
        # This would integrate with your existing individual analysis logic
        pass

# Global instances
ai_validator = AIResponseValidator()
ai_optimizer = AIUsageOptimizer()
ai_monitor = AIQualityMonitor()

# Utility functions
@lru_cache(maxsize=1000)
def get_analysis_cache_key(symbol: str, date: str, level: str) -> str:
    """Generate cache key for analysis (with LRU cache for key generation)"""
    return f"analysis:{symbol}:{date}:{level}"

async def validate_and_monitor_response(
    response: Dict[str, Any],
    stock_data: Dict[str, Any],
    model: str,
    input_tokens: int,
    output_tokens: int,
    response_time: float
) -> Tuple[ValidationResult, List[str], float]:
    """Complete validation and monitoring pipeline"""
    
    # Validate response
    validation_result, issues = ai_validator.validate_response(response, stock_data)
    
    # Calculate cost
    cost = ai_optimizer.calculate_cost(model, input_tokens, output_tokens)
    
    # Calculate quality score
    confidence = float(response.get('confidence', 0))
    quality_score = ai_monitor.get_quality_score(validation_result, confidence, response_time)
    
    # Record metrics
    await ai_monitor.record_request(
        model, input_tokens, output_tokens, response_time, validation_result, cost
    )
    
    # Check for alerts
    should_alert, alerts = ai_monitor.should_trigger_alert()
    if should_alert:
        logger.warning(f"AI Quality Alert: {alerts}")
    
    return validation_result, issues, quality_score
