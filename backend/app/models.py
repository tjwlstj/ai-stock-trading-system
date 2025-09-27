"""
Pydantic Models
Request/Response models for API endpoints with validation
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class StockAnalysisRequest(BaseModel):
    """Request model for stock analysis"""
    time_horizon: Optional[str] = Field(default="MEDIUM", description="Analysis time horizon")
    risk_tolerance: Optional[str] = Field(default="MEDIUM", description="Risk tolerance level")
    analysis_type: Optional[str] = Field(default="COMPREHENSIVE", description="Type of analysis")

class AgentAnalysis(BaseModel):
    """Individual agent analysis result"""
    score: float = Field(ge=0.0, le=1.0, description="Analysis score")
    reasoning: str = Field(description="Analysis reasoning")

class StockAnalysisResponse(BaseModel):
    """Response model for stock analysis"""
    symbol: str = Field(description="Stock symbol")
    recommendation: str = Field(description="Investment recommendation")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    target_price: float = Field(description="Target price")
    analysis: Dict[str, AgentAnalysis] = Field(description="Multi-agent analysis")
    timestamp: str = Field(description="Analysis timestamp")
    model_used: str = Field(description="AI model used")

class StockData(BaseModel):
    """Stock data model"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[str] = None
    timestamp: str
    source: str = "yahoo_finance"

class PortfolioSummary(BaseModel):
    """Portfolio summary model"""
    total_value: float
    daily_change: float
    daily_change_percent: float
    positions: int
    cash: float
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str
    environment: str
    services: Dict[str, str]

class ConfigResponse(BaseModel):
    """Configuration response model"""
    backend_url: str
    openai_model: str
    environment: str
    features: Dict[str, bool]
    version: str

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
