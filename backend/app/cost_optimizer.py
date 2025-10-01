"""
Cost Optimization and Budget Management System
Provides comprehensive cost tracking, budget controls, and optimization strategies
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import json
from decimal import Decimal, ROUND_HALF_UP

import redis
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CostCategory(str, Enum):
    """Cost categories for tracking"""
    AI_API = "ai_api"
    DATA_API = "data_api"
    INFRASTRUCTURE = "infrastructure"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"

class BudgetPeriod(str, Enum):
    """Budget tracking periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class AlertLevel(str, Enum):
    """Budget alert levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class CostEntry:
    """Individual cost entry"""
    timestamp: datetime
    category: CostCategory
    amount: Decimal
    description: str
    metadata: Dict[str, Any] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class BudgetLimit:
    """Budget limit configuration"""
    category: CostCategory
    period: BudgetPeriod
    limit: Decimal
    alert_thresholds: Dict[str, float]  # percentage thresholds for alerts
    enabled: bool = True

@dataclass
class UsageStats:
    """Usage statistics for cost analysis"""
    period_start: datetime
    period_end: datetime
    total_cost: Decimal
    cost_by_category: Dict[CostCategory, Decimal]
    request_count: int
    average_cost_per_request: Decimal
    top_cost_drivers: List[Dict[str, Any]]

class CostTracker:
    """Tracks and records all system costs"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.local_costs: List[CostEntry] = []
        self.max_local_entries = 1000
        
        # Cost rates (would be configurable)
        self.cost_rates = {
            'gpt-4o-mini': {
                'input_tokens': Decimal('0.00015') / 1000,  # per token
                'output_tokens': Decimal('0.0006') / 1000   # per token
            },
            'yahoo_finance': Decimal('0.0'),  # Free
            'alpha_vantage': Decimal('0.01'),  # per request (example)
            'redis': Decimal('0.001'),  # per operation (example)
        }
    
    async def record_ai_cost(self, 
                           model: str,
                           input_tokens: int,
                           output_tokens: int,
                           user_id: Optional[str] = None,
                           session_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None):
        """Record AI API cost"""
        
        if model not in self.cost_rates:
            logger.warning(f"Unknown model for cost calculation: {model}")
            return
        
        rates = self.cost_rates[model]
        input_cost = Decimal(input_tokens) * rates['input_tokens']
        output_cost = Decimal(output_tokens) * rates['output_tokens']
        total_cost = input_cost + output_cost
        
        cost_entry = CostEntry(
            timestamp=datetime.now(),
            category=CostCategory.AI_API,
            amount=total_cost,
            description=f"{model} API call: {input_tokens}+{output_tokens} tokens",
            metadata={
                'model': model,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'input_cost': float(input_cost),
                'output_cost': float(output_cost),
                **(metadata or {})
            },
            user_id=user_id,
            session_id=session_id
        )
        
        await self._store_cost_entry(cost_entry)
    
    async def record_data_cost(self,
                             provider: str,
                             requests_count: int = 1,
                             user_id: Optional[str] = None,
                             session_id: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None):
        """Record data API cost"""
        
        cost_per_request = self.cost_rates.get(provider, Decimal('0.0'))
        total_cost = Decimal(requests_count) * cost_per_request
        
        if total_cost > 0:
            cost_entry = CostEntry(
                timestamp=datetime.now(),
                category=CostCategory.DATA_API,
                amount=total_cost,
                description=f"{provider} API: {requests_count} requests",
                metadata={
                    'provider': provider,
                    'requests_count': requests_count,
                    'cost_per_request': float(cost_per_request),
                    **(metadata or {})
                },
                user_id=user_id,
                session_id=session_id
            )
            
            await self._store_cost_entry(cost_entry)
    
    async def record_infrastructure_cost(self,
                                       service: str,
                                       amount: Decimal,
                                       description: str,
                                       metadata: Optional[Dict[str, Any]] = None):
        """Record infrastructure costs (servers, storage, etc.)"""
        
        cost_entry = CostEntry(
            timestamp=datetime.now(),
            category=CostCategory.INFRASTRUCTURE,
            amount=amount,
            description=f"{service}: {description}",
            metadata={
                'service': service,
                **(metadata or {})
            }
        )
        
        await self._store_cost_entry(cost_entry)
    
    async def _store_cost_entry(self, entry: CostEntry):
        """Store cost entry in Redis and local cache"""
        
        # Store in Redis
        if self.redis_client:
            try:
                # Daily aggregation key
                date_key = entry.timestamp.strftime('%Y-%m-%d')
                redis_key = f"costs:{date_key}"
                
                entry_data = asdict(entry)
                entry_data['timestamp'] = entry.timestamp.isoformat()
                entry_data['amount'] = str(entry.amount)
                
                await self.redis_client.lpush(redis_key, json.dumps(entry_data))
                await self.redis_client.expire(redis_key, 86400 * 90)  # Keep for 90 days
                
                # Update daily totals
                total_key = f"cost_totals:{date_key}:{entry.category.value}"
                await self.redis_client.incrbyfloat(total_key, float(entry.amount))
                await self.redis_client.expire(total_key, 86400 * 90)
                
            except Exception as e:
                logger.error(f"Failed to store cost entry in Redis: {e}")
        
        # Store locally
        self.local_costs.append(entry)
        if len(self.local_costs) > self.max_local_entries:
            self.local_costs = self.local_costs[-self.max_local_entries:]
    
    async def get_costs_for_period(self, 
                                 start_date: date,
                                 end_date: date,
                                 category: Optional[CostCategory] = None) -> List[CostEntry]:
        """Retrieve costs for a specific period"""
        
        costs = []
        
        if self.redis_client:
            try:
                current_date = start_date
                while current_date <= end_date:
                    date_key = current_date.strftime('%Y-%m-%d')
                    redis_key = f"costs:{date_key}"
                    
                    entries = await self.redis_client.lrange(redis_key, 0, -1)
                    for entry_json in entries:
                        entry_data = json.loads(entry_json)
                        entry_data['timestamp'] = datetime.fromisoformat(entry_data['timestamp'])
                        entry_data['amount'] = Decimal(entry_data['amount'])
                        entry_data['category'] = CostCategory(entry_data['category'])
                        
                        entry = CostEntry(**entry_data)
                        
                        if category is None or entry.category == category:
                            costs.append(entry)
                    
                    current_date += timedelta(days=1)
                    
            except Exception as e:
                logger.error(f"Failed to retrieve costs from Redis: {e}")
        
        # Fallback to local costs
        if not costs:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            costs = [
                entry for entry in self.local_costs
                if start_datetime <= entry.timestamp <= end_datetime
                and (category is None or entry.category == category)
            ]
        
        return sorted(costs, key=lambda x: x.timestamp)

class BudgetManager:
    """Manages budget limits and alerts"""
    
    def __init__(self, cost_tracker: CostTracker, redis_client: Optional[redis.Redis] = None):
        self.cost_tracker = cost_tracker
        self.redis_client = redis_client
        self.budget_limits: Dict[str, BudgetLimit] = {}
        self.alert_callbacks: List[callable] = []
        
        # Default budget limits
        self._setup_default_budgets()
    
    def _setup_default_budgets(self):
        """Setup default budget limits"""
        
        # Daily AI API budget
        self.budget_limits['ai_daily'] = BudgetLimit(
            category=CostCategory.AI_API,
            period=BudgetPeriod.DAILY,
            limit=Decimal('10.00'),  # $10 per day
            alert_thresholds={
                'warning': 0.7,    # 70%
                'critical': 0.9,   # 90%
                'emergency': 1.0   # 100%
            }
        )
        
        # Monthly total budget
        self.budget_limits['total_monthly'] = BudgetLimit(
            category=None,  # All categories
            period=BudgetPeriod.MONTHLY,
            limit=Decimal('200.00'),  # $200 per month
            alert_thresholds={
                'warning': 0.6,
                'critical': 0.8,
                'emergency': 0.95
            }
        )
    
    def set_budget_limit(self, 
                        name: str,
                        category: Optional[CostCategory],
                        period: BudgetPeriod,
                        limit: Decimal,
                        alert_thresholds: Dict[str, float]):
        """Set a custom budget limit"""
        
        self.budget_limits[name] = BudgetLimit(
            category=category,
            period=period,
            limit=limit,
            alert_thresholds=alert_thresholds
        )
    
    async def check_budgets(self) -> List[Dict[str, Any]]:
        """Check all budget limits and return alerts"""
        
        alerts = []
        current_date = date.today()
        
        for name, budget in self.budget_limits.items():
            if not budget.enabled:
                continue
            
            # Calculate period start/end
            period_start, period_end = self._get_period_dates(current_date, budget.period)
            
            # Get costs for period
            costs = await self.cost_tracker.get_costs_for_period(
                period_start, period_end, budget.category
            )
            
            # Calculate total cost
            total_cost = sum(entry.amount for entry in costs)
            usage_percentage = float(total_cost / budget.limit) if budget.limit > 0 else 0
            
            # Check thresholds
            for alert_type, threshold in budget.alert_thresholds.items():
                if usage_percentage >= threshold:
                    alert = {
                        'budget_name': name,
                        'alert_level': AlertLevel(alert_type),
                        'category': budget.category.value if budget.category else 'all',
                        'period': budget.period.value,
                        'current_cost': float(total_cost),
                        'budget_limit': float(budget.limit),
                        'usage_percentage': usage_percentage,
                        'threshold': threshold,
                        'period_start': period_start.isoformat(),
                        'period_end': period_end.isoformat(),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    alerts.append(alert)
                    
                    # Trigger callbacks
                    for callback in self.alert_callbacks:
                        try:
                            await callback(alert)
                        except Exception as e:
                            logger.error(f"Budget alert callback failed: {e}")
                    
                    break  # Only send highest priority alert
        
        return alerts
    
    def _get_period_dates(self, current_date: date, period: BudgetPeriod) -> Tuple[date, date]:
        """Get start and end dates for a budget period"""
        
        if period == BudgetPeriod.DAILY:
            return current_date, current_date
        
        elif period == BudgetPeriod.WEEKLY:
            # Week starts on Monday
            start = current_date - timedelta(days=current_date.weekday())
            end = start + timedelta(days=6)
            return start, end
        
        elif period == BudgetPeriod.MONTHLY:
            start = current_date.replace(day=1)
            if current_date.month == 12:
                end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
            return start, end
        
        elif period == BudgetPeriod.YEARLY:
            start = current_date.replace(month=1, day=1)
            end = current_date.replace(month=12, day=31)
            return start, end
        
        return current_date, current_date
    
    def add_alert_callback(self, callback: callable):
        """Add callback for budget alerts"""
        self.alert_callbacks.append(callback)
    
    async def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status for all limits"""
        
        status = {}
        current_date = date.today()
        
        for name, budget in self.budget_limits.items():
            period_start, period_end = self._get_period_dates(current_date, budget.period)
            
            costs = await self.cost_tracker.get_costs_for_period(
                period_start, period_end, budget.category
            )
            
            total_cost = sum(entry.amount for entry in costs)
            usage_percentage = float(total_cost / budget.limit) if budget.limit > 0 else 0
            
            status[name] = {
                'category': budget.category.value if budget.category else 'all',
                'period': budget.period.value,
                'current_cost': float(total_cost),
                'budget_limit': float(budget.limit),
                'remaining_budget': float(budget.limit - total_cost),
                'usage_percentage': usage_percentage,
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'enabled': budget.enabled
            }
        
        return status

class CostOptimizer:
    """Provides cost optimization recommendations and strategies"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
    
    async def analyze_usage_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze usage patterns to identify optimization opportunities"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        costs = await self.cost_tracker.get_costs_for_period(start_date, end_date)
        
        if not costs:
            return {'recommendations': [], 'analysis': {}}
        
        # Group by category
        category_costs = {}
        for cost in costs:
            if cost.category not in category_costs:
                category_costs[cost.category] = []
            category_costs[cost.category].append(cost)
        
        # Analyze AI API usage
        ai_analysis = await self._analyze_ai_usage(category_costs.get(CostCategory.AI_API, []))
        
        # Generate recommendations
        recommendations = []
        
        # AI cost optimization
        if ai_analysis['total_cost'] > 50:  # If spending more than $50
            recommendations.extend(self._get_ai_optimization_recommendations(ai_analysis))
        
        # Data API optimization
        data_costs = category_costs.get(CostCategory.DATA_API, [])
        if data_costs:
            recommendations.extend(self._get_data_optimization_recommendations(data_costs))
        
        return {
            'analysis_period': f"{start_date} to {end_date}",
            'total_costs': float(sum(cost.amount for cost in costs)),
            'category_breakdown': {
                category.value: float(sum(cost.amount for cost in costs))
                for category, costs in category_costs.items()
            },
            'ai_analysis': ai_analysis,
            'recommendations': recommendations
        }
    
    async def _analyze_ai_usage(self, ai_costs: List[CostEntry]) -> Dict[str, Any]:
        """Analyze AI API usage patterns"""
        
        if not ai_costs:
            return {}
        
        total_cost = sum(cost.amount for cost in ai_costs)
        total_requests = len(ai_costs)
        
        # Analyze by model
        model_usage = {}
        for cost in ai_costs:
            model = cost.metadata.get('model', 'unknown')
            if model not in model_usage:
                model_usage[model] = {
                    'requests': 0,
                    'total_cost': Decimal('0'),
                    'total_tokens': 0
                }
            
            model_usage[model]['requests'] += 1
            model_usage[model]['total_cost'] += cost.amount
            model_usage[model]['total_tokens'] += (
                cost.metadata.get('input_tokens', 0) + 
                cost.metadata.get('output_tokens', 0)
            )
        
        # Find patterns
        avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
        
        return {
            'total_cost': float(total_cost),
            'total_requests': total_requests,
            'average_cost_per_request': float(avg_cost_per_request),
            'model_breakdown': {
                model: {
                    'requests': stats['requests'],
                    'total_cost': float(stats['total_cost']),
                    'average_cost': float(stats['total_cost'] / stats['requests']),
                    'total_tokens': stats['total_tokens']
                }
                for model, stats in model_usage.items()
            }
        }
    
    def _get_ai_optimization_recommendations(self, ai_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI cost optimization recommendations"""
        
        recommendations = []
        
        # High cost per request
        if ai_analysis.get('average_cost_per_request', 0) > 0.05:  # $0.05
            recommendations.append({
                'type': 'ai_optimization',
                'priority': 'high',
                'title': 'Optimize AI Prompts',
                'description': 'Your average AI request cost is high. Consider optimizing prompts to reduce token usage.',
                'potential_savings': '20-40%',
                'actions': [
                    'Use more concise prompts',
                    'Implement prompt caching for similar requests',
                    'Use batch processing for multiple analyses'
                ]
            })
        
        # Model usage optimization
        model_breakdown = ai_analysis.get('model_breakdown', {})
        if len(model_breakdown) > 1:
            # Check if using expensive models for simple tasks
            recommendations.append({
                'type': 'model_optimization',
                'priority': 'medium',
                'title': 'Optimize Model Selection',
                'description': 'Consider using less expensive models for simpler analysis tasks.',
                'potential_savings': '30-50%',
                'actions': [
                    'Use gpt-4o-mini for quick analyses',
                    'Reserve comprehensive models for complex tasks',
                    'Implement analysis level selection'
                ]
            })
        
        return recommendations
    
    def _get_data_optimization_recommendations(self, data_costs: List[CostEntry]) -> List[Dict[str, Any]]:
        """Generate data API optimization recommendations"""
        
        recommendations = []
        
        if len(data_costs) > 1000:  # High volume
            recommendations.append({
                'type': 'data_optimization',
                'priority': 'high',
                'title': 'Implement Aggressive Caching',
                'description': 'High volume of data API requests detected. Implement more aggressive caching.',
                'potential_savings': '50-70%',
                'actions': [
                    'Increase cache TTL during market hours',
                    'Implement batch data fetching',
                    'Use WebSocket connections for real-time data'
                ]
            })
        
        return recommendations

class CostReporter:
    """Generates cost reports and analytics"""
    
    def __init__(self, cost_tracker: CostTracker, budget_manager: BudgetManager):
        self.cost_tracker = cost_tracker
        self.budget_manager = budget_manager
    
    async def generate_daily_report(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Generate daily cost report"""
        
        if target_date is None:
            target_date = date.today()
        
        costs = await self.cost_tracker.get_costs_for_period(target_date, target_date)
        
        # Calculate totals by category
        category_totals = {}
        for cost in costs:
            if cost.category not in category_totals:
                category_totals[cost.category] = Decimal('0')
            category_totals[cost.category] += cost.amount
        
        total_cost = sum(category_totals.values())
        
        # Get budget status
        budget_status = await self.budget_manager.get_budget_status()
        
        return {
            'date': target_date.isoformat(),
            'total_cost': float(total_cost),
            'category_breakdown': {
                category.value: float(amount)
                for category, amount in category_totals.items()
            },
            'transaction_count': len(costs),
            'budget_status': budget_status,
            'top_expenses': [
                {
                    'description': cost.description,
                    'amount': float(cost.amount),
                    'category': cost.category.value,
                    'timestamp': cost.timestamp.isoformat()
                }
                for cost in sorted(costs, key=lambda x: x.amount, reverse=True)[:5]
            ]
        }
    
    async def generate_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Generate monthly cost summary"""
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        costs = await self.cost_tracker.get_costs_for_period(start_date, end_date)
        
        # Daily breakdown
        daily_totals = {}
        current_date = start_date
        while current_date <= end_date:
            daily_costs = [c for c in costs if c.timestamp.date() == current_date]
            daily_totals[current_date.isoformat()] = float(sum(c.amount for c in daily_costs))
            current_date += timedelta(days=1)
        
        # Category breakdown
        category_totals = {}
        for cost in costs:
            if cost.category not in category_totals:
                category_totals[cost.category] = Decimal('0')
            category_totals[cost.category] += cost.amount
        
        total_cost = sum(category_totals.values())
        
        return {
            'period': f"{year}-{month:02d}",
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_cost': float(total_cost),
            'daily_breakdown': daily_totals,
            'category_breakdown': {
                category.value: float(amount)
                for category, amount in category_totals.items()
            },
            'average_daily_cost': float(total_cost / (end_date - start_date).days) if costs else 0,
            'total_transactions': len(costs)
        }

# Global instances
cost_tracker = CostTracker()
budget_manager = BudgetManager(cost_tracker)
cost_optimizer = CostOptimizer(cost_tracker)
cost_reporter = CostReporter(cost_tracker, budget_manager)

# Utility functions
async def track_ai_request_cost(model: str, input_tokens: int, output_tokens: int, **kwargs):
    """Convenience function to track AI request costs"""
    await cost_tracker.record_ai_cost(model, input_tokens, output_tokens, **kwargs)

async def get_current_budget_status() -> Dict[str, Any]:
    """Get current budget status across all limits"""
    return await budget_manager.get_budget_status()

async def check_budget_alerts() -> List[Dict[str, Any]]:
    """Check for budget alerts"""
    return await budget_manager.check_budgets()

async def get_cost_optimization_recommendations(days: int = 30) -> Dict[str, Any]:
    """Get cost optimization recommendations"""
    return await cost_optimizer.analyze_usage_patterns(days)
