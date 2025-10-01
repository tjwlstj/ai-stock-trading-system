/**
 * Enhanced Stock Analysis Component with Progressive Loading and Real-time Updates
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  Button,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Badge,
  Progress,
  Alert,
  AlertDescription,
  Skeleton,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from '@/components/ui';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  DollarSign,
  BarChart3,
  Wifi,
  WifiOff
} from 'lucide-react';

// Types
interface StockQuote {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_status: string;
  timestamp: string;
}

interface AnalysisResult {
  symbol: string;
  recommendation: string;
  confidence: number;
  reasoning: string;
  key_factors: string[];
  risks: string[];
  price_target?: number;
  market_status: string;
  data_freshness: {
    cache_age_seconds: number;
    is_cached: boolean;
    data_source: string;
  };
  validation_result: string;
  quality_score: number;
  cost_info: {
    estimated_cost: number;
    tokens_used: number;
  };
  timestamp: string;
  correlation_id: string;
}

interface LoadingState {
  phase: 'idle' | 'fetching_data' | 'ai_analysis' | 'validation' | 'complete';
  progress: number;
  message: string;
}

// Custom hooks
const useWebSocket = (symbol: string) => {
  const [quote, setQuote] = useState<StockQuote | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!symbol) return;

    const connectWebSocket = () => {
      const ws = new WebSocket(`ws://localhost:8000/ws/realtime/${symbol}`);
      
      ws.onopen = () => {
        setIsConnected(true);
        console.log(`WebSocket connected for ${symbol}`);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setQuote(data);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log(`WebSocket disconnected for ${symbol}`);
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [symbol]);

  return { quote, isConnected };
};

const useAnalysisCache = () => {
  const [cache, setCache] = useState<Map<string, AnalysisResult>>(new Map());

  const getCachedAnalysis = useCallback((symbol: string, level: string) => {
    const key = `${symbol}:${level}`;
    return cache.get(key);
  }, [cache]);

  const setCachedAnalysis = useCallback((analysis: AnalysisResult, level: string) => {
    const key = `${analysis.symbol}:${level}`;
    setCache(prev => new Map(prev.set(key, analysis)));
  }, []);

  return { getCachedAnalysis, setCachedAnalysis };
};

// Main component
export const EnhancedStockAnalysis: React.FC = () => {
  const [symbol, setSymbol] = useState('');
  const [analysisLevel, setAnalysisLevel] = useState('standard');
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState<LoadingState>({
    phase: 'idle',
    progress: 0,
    message: ''
  });
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const { quote, isConnected } = useWebSocket(symbol);
  const { getCachedAnalysis, setCachedAnalysis } = useAnalysisCache();

  // Progressive loading simulation
  const updateLoadingState = useCallback((phase: LoadingState['phase'], progress: number, message: string) => {
    setLoading({ phase, progress, message });
  }, []);

  const analyzeStock = async () => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setError(null);
    
    // Check cache first
    const cached = getCachedAnalysis(symbol.toUpperCase(), analysisLevel);
    if (cached) {
      setAnalysis(cached);
      updateLoadingState('complete', 100, 'Using cached analysis');
      return;
    }

    try {
      // Phase 1: Fetching market data
      updateLoadingState('fetching_data', 20, 'Fetching real-time market data...');
      
      // Simulate progressive loading
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Phase 2: AI Analysis
      updateLoadingState('ai_analysis', 60, 'AI agents analyzing stock...');
      
      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-ID': crypto.randomUUID()
        },
        body: JSON.stringify({
          symbol: symbol.toUpperCase(),
          analysis_level: analysisLevel,
          force_refresh: false,
          include_technical: true,
          include_fundamental: true
        })
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      // Phase 3: Validation
      updateLoadingState('validation', 85, 'Validating AI response...');
      await new Promise(resolve => setTimeout(resolve, 500));

      const result: AnalysisResult = await response.json();
      
      // Phase 4: Complete
      updateLoadingState('complete', 100, 'Analysis complete');
      
      setAnalysis(result);
      setCachedAnalysis(result, analysisLevel);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      updateLoadingState('idle', 0, '');
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation.toUpperCase()) {
      case 'BUY':
      case 'STRONG_BUY':
        return 'text-green-600 bg-green-50';
      case 'SELL':
      case 'STRONG_SELL':
        return 'text-red-600 bg-red-50';
      case 'HOLD':
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getValidationBadge = (validation: string, quality: number) => {
    if (validation === 'valid' && quality > 0.8) {
      return <Badge className="bg-green-100 text-green-800">High Quality</Badge>;
    } else if (validation === 'warning') {
      return <Badge className="bg-yellow-100 text-yellow-800">Needs Review</Badge>;
    } else {
      return <Badge className="bg-red-100 text-red-800">Low Quality</Badge>;
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Stock Analysis System
        </h1>
        <p className="text-gray-600">
          Enhanced with real-time data, quality monitoring, and cost optimization
        </p>
      </div>

      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Stock Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">Stock Symbol</label>
              <Input
                type="text"
                placeholder="e.g., AAPL, GOOGL, TSLA"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                onKeyPress={(e) => e.key === 'Enter' && analyzeStock()}
                className="uppercase"
              />
            </div>
            
            <div className="w-48">
              <label className="block text-sm font-medium mb-2">Analysis Level</label>
              <Select value={analysisLevel} onValueChange={setAnalysisLevel}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="quick">Quick ($0.001)</SelectItem>
                  <SelectItem value="standard">Standard ($0.005)</SelectItem>
                  <SelectItem value="comprehensive">Comprehensive ($0.015)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button 
              onClick={analyzeStock} 
              disabled={loading.phase !== 'idle' && loading.phase !== 'complete'}
              className="px-8"
            >
              {loading.phase !== 'idle' && loading.phase !== 'complete' ? 'Analyzing...' : 'Analyze'}
            </Button>
          </div>

          {/* Real-time Connection Status */}
          {symbol && (
            <div className="flex items-center gap-2 text-sm">
              {isConnected ? (
                <>
                  <Wifi className="h-4 w-4 text-green-500" />
                  <span className="text-green-600">Real-time data connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-500">Connecting to real-time data...</span>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Loading Progress */}
      {loading.phase !== 'idle' && loading.phase !== 'complete' && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{loading.message}</span>
                <span className="text-sm text-gray-500">{loading.progress}%</span>
              </div>
              <Progress value={loading.progress} className="h-2" />
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Activity className="h-3 w-3 animate-pulse" />
                <span>AI agents are working on your analysis...</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Real-time Quote */}
      {quote && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{quote.symbol} - Real-time Quote</span>
              <Badge className={quote.market_status === 'open' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                {quote.market_status.replace('_', ' ').toUpperCase()}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-500">Price</p>
                <p className="text-2xl font-bold">{formatCurrency(quote.price)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Change</p>
                <p className={`text-lg font-semibold ${quote.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {quote.change >= 0 ? '+' : ''}{formatCurrency(quote.change)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Change %</p>
                <p className={`text-lg font-semibold ${quote.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercentage(quote.change_percent)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Volume</p>
                <p className="text-lg font-semibold">{quote.volume.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Main Analysis Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>AI Analysis Results</span>
                <div className="flex items-center gap-2">
                  {getValidationBadge(analysis.validation_result, analysis.quality_score)}
                  <Badge className={getRecommendationColor(analysis.recommendation)}>
                    {analysis.recommendation.replace('_', ' ')}
                  </Badge>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="analysis" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="analysis">Analysis</TabsTrigger>
                  <TabsTrigger value="factors">Key Factors</TabsTrigger>
                  <TabsTrigger value="risks">Risks</TabsTrigger>
                  <TabsTrigger value="metadata">Metadata</TabsTrigger>
                </TabsList>

                <TabsContent value="analysis" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-500">Confidence</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {(analysis.confidence * 100).toFixed(1)}%
                      </p>
                      <Progress value={analysis.confidence * 100} className="mt-2" />
                    </div>
                    
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-500">Quality Score</p>
                      <p className="text-2xl font-bold text-green-600">
                        {(analysis.quality_score * 100).toFixed(1)}%
                      </p>
                      <Progress value={analysis.quality_score * 100} className="mt-2" />
                    </div>

                    {analysis.price_target && (
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-500">Price Target</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {formatCurrency(analysis.price_target)}
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="mt-6">
                    <h4 className="font-semibold mb-3">AI Reasoning</h4>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-gray-700 leading-relaxed">{analysis.reasoning}</p>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="factors">
                  <div className="space-y-3">
                    <h4 className="font-semibold">Key Factors Supporting This Analysis</h4>
                    {analysis.key_factors.map((factor, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                        <span className="text-green-800">{factor}</span>
                      </div>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="risks">
                  <div className="space-y-3">
                    <h4 className="font-semibold">Identified Risks</h4>
                    {analysis.risks.map((risk, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
                        <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                        <span className="text-red-800">{risk}</span>
                      </div>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="metadata">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Data Quality</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Data Source:</span>
                          <span className="font-medium">{analysis.data_freshness.data_source}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Cache Age:</span>
                          <span className="font-medium">
                            {analysis.data_freshness.cache_age_seconds}s
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Validation:</span>
                          <span className="font-medium capitalize">{analysis.validation_result}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-3">Cost Information</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Estimated Cost:</span>
                          <span className="font-medium">
                            ${analysis.cost_info.estimated_cost.toFixed(4)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Tokens Used:</span>
                          <span className="font-medium">{analysis.cost_info.tokens_used}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Analysis Time:</span>
                          <span className="font-medium">
                            {new Date(analysis.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Disclaimer */}
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Educational Purpose Only:</strong> This analysis is generated by AI for educational and research purposes. 
              It should not be considered as financial advice. Always consult with qualified financial professionals before making investment decisions.
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
};

export default EnhancedStockAnalysis;
