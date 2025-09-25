import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Search, 
  Bot, 
  TrendingUp, 
  TrendingDown, 
  Shield, 
  Target,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Brain,
  BarChart3
} from 'lucide-react'

const StockAnalysis = () => {
  const [searchSymbol, setSearchSymbol] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [selectedStock, setSelectedStock] = useState('AAPL')

  // 모의 분석 결과 데이터
  const mockAnalysisResults = {
    symbol: 'AAPL',
    currentPrice: 256.87,
    finalRecommendation: 'BUY',
    confidence: 0.85,
    targetPrice: 280.00,
    positionSize: 7.5,
    stopLoss: 240.00,
    riskLevel: 'MEDIUM',
    agentAnalyses: {
      optimistic: {
        recommendation: 'BUY',
        confidence: 0.91,
        reasoning: 'Strong fundamentals with consistent innovation and market leadership in technology sector. Recent product launches show promising growth potential.',
        targetPrice: 285.00
      },
      pessimistic: {
        recommendation: 'HOLD',
        confidence: 0.74,
        reasoning: 'While Apple is strong, current market conditions and high valuation suggest caution. Potential headwinds from economic uncertainty.',
        targetPrice: 245.00
      },
      risk: {
        riskAssessment: 'MEDIUM',
        positionSize: 7.5,
        stopLoss: 240.00,
        riskScore: 45.2,
        volatility: 0.28
      }
    },
    consensus: {
      recommendation: 'BUY',
      agreementLevel: 0.67,
      keyFactors: [
        'Strong revenue growth in services segment',
        'Solid cash flow generation',
        'Market leadership in premium smartphone segment'
      ]
    },
    conflicts: [],
    timestamp: new Date().toISOString()
  }

  const performAnalysis = async (symbol) => {
    setIsAnalyzing(true)
    setSelectedStock(symbol)
    
    // 분석 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // 실제로는 백엔드 API 호출
    // const response = await fetch(`/api/analyze/${symbol}`)
    // const results = await response.json()
    
    setAnalysisResults({
      ...mockAnalysisResults,
      symbol: symbol,
      timestamp: new Date().toISOString()
    })
    setIsAnalyzing(false)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchSymbol.trim()) {
      performAnalysis(searchSymbol.toUpperCase())
    }
  }

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'BUY': return 'text-green-600 bg-green-100 dark:bg-green-900/20'
      case 'SELL': return 'text-red-600 bg-red-100 dark:bg-red-900/20'
      default: return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
    }
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'LOW': return 'text-green-600'
      case 'HIGH': return 'text-red-600'
      default: return 'text-yellow-600'
    }
  }

  useEffect(() => {
    // 초기 분석 실행
    performAnalysis('AAPL')
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AI Stock Analysis</h1>
          <p className="text-muted-foreground">
            Multi-agent comprehensive stock analysis system
          </p>
        </div>
      </div>

      {/* Search Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Stock Analysis</span>
          </CardTitle>
          <CardDescription>
            Enter a stock symbol to get comprehensive AI-powered analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex space-x-2">
            <Input
              placeholder="Enter stock symbol (e.g., AAPL, GOOGL, MSFT)"
              value={searchSymbol}
              onChange={(e) => setSearchSymbol(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" disabled={isAnalyzing}>
              {isAnalyzing ? (
                <>
                  <Bot className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Analyze
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Analysis Progress */}
      {isAnalyzing && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Bot className="h-5 w-5 text-blue-500 animate-pulse" />
                <span className="font-medium">AI Analysis in Progress</span>
              </div>
              <Progress value={66} className="w-full" />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Data Collection Complete</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-yellow-500 animate-spin" />
                  <span>Multi-Agent Analysis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span>Generating Report</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysisResults && !isAnalyzing && (
        <div className="space-y-6">
          {/* Summary Card */}
          <Card className="border-2 border-primary/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-2xl">{analysisResults.symbol} Analysis</CardTitle>
                <Badge variant="outline" className="text-sm">
                  {new Date(analysisResults.timestamp).toLocaleString()}
                </Badge>
              </div>
              <CardDescription>
                Current Price: ${analysisResults.currentPrice}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center p-4 rounded-lg bg-muted/50">
                  <div className={`text-2xl font-bold ${getRecommendationColor(analysisResults.finalRecommendation)}`}>
                    {analysisResults.finalRecommendation}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">Final Recommendation</p>
                </div>
                <div className="text-center p-4 rounded-lg bg-muted/50">
                  <div className="text-2xl font-bold text-foreground">
                    {(analysisResults.confidence * 100).toFixed(0)}%
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">Confidence Level</p>
                </div>
                <div className="text-center p-4 rounded-lg bg-muted/50">
                  <div className="text-2xl font-bold text-foreground">
                    ${analysisResults.targetPrice}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">Target Price</p>
                </div>
                <div className="text-center p-4 rounded-lg bg-muted/50">
                  <div className={`text-2xl font-bold ${getRiskColor(analysisResults.riskLevel)}`}>
                    {analysisResults.riskLevel}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">Risk Level</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detailed Analysis Tabs */}
          <Tabs defaultValue="agents" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="agents">AI Agents</TabsTrigger>
              <TabsTrigger value="consensus">Consensus</TabsTrigger>
              <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
              <TabsTrigger value="recommendations">Actions</TabsTrigger>
            </TabsList>

            <TabsContent value="agents" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Optimistic Agent */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <TrendingUp className="h-5 w-5 text-green-500" />
                      <span>Optimistic Analyst</span>
                    </CardTitle>
                    <CardDescription>Growth-focused analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <Badge className={getRecommendationColor(analysisResults.agentAnalyses.optimistic.recommendation)}>
                        {analysisResults.agentAnalyses.optimistic.recommendation}
                      </Badge>
                      <span className="text-sm font-medium">
                        Confidence: {(analysisResults.agentAnalyses.optimistic.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={analysisResults.agentAnalyses.optimistic.confidence * 100} />
                    <p className="text-sm text-muted-foreground">
                      {analysisResults.agentAnalyses.optimistic.reasoning}
                    </p>
                    <div className="text-sm">
                      <span className="font-medium">Target Price: </span>
                      <span className="text-green-600">${analysisResults.agentAnalyses.optimistic.targetPrice}</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Pessimistic Agent */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <TrendingDown className="h-5 w-5 text-red-500" />
                      <span>Pessimistic Analyst</span>
                    </CardTitle>
                    <CardDescription>Risk-focused analysis</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <Badge className={getRecommendationColor(analysisResults.agentAnalyses.pessimistic.recommendation)}>
                        {analysisResults.agentAnalyses.pessimistic.recommendation}
                      </Badge>
                      <span className="text-sm font-medium">
                        Confidence: {(analysisResults.agentAnalyses.pessimistic.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={analysisResults.agentAnalyses.pessimistic.confidence * 100} />
                    <p className="text-sm text-muted-foreground">
                      {analysisResults.agentAnalyses.pessimistic.reasoning}
                    </p>
                    <div className="text-sm">
                      <span className="font-medium">Target Price: </span>
                      <span className="text-red-600">${analysisResults.agentAnalyses.pessimistic.targetPrice}</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Risk Manager */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Shield className="h-5 w-5 text-blue-500" />
                    <span>Risk Manager</span>
                  </CardTitle>
                  <CardDescription>Portfolio risk assessment and position sizing</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 rounded-lg bg-muted/50">
                      <div className="text-xl font-bold text-foreground">
                        {analysisResults.agentAnalyses.risk.positionSize}%
                      </div>
                      <p className="text-sm text-muted-foreground">Recommended Position</p>
                    </div>
                    <div className="text-center p-4 rounded-lg bg-muted/50">
                      <div className="text-xl font-bold text-foreground">
                        ${analysisResults.agentAnalyses.risk.stopLoss}
                      </div>
                      <p className="text-sm text-muted-foreground">Stop Loss Level</p>
                    </div>
                    <div className="text-center p-4 rounded-lg bg-muted/50">
                      <div className="text-xl font-bold text-foreground">
                        {analysisResults.agentAnalyses.risk.riskScore}
                      </div>
                      <p className="text-sm text-muted-foreground">Risk Score</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="consensus" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-purple-500" />
                    <span>Agent Consensus</span>
                  </CardTitle>
                  <CardDescription>Integrated analysis from all AI agents</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Agreement Level</span>
                    <span className="text-sm text-muted-foreground">
                      {(analysisResults.consensus.agreementLevel * 100).toFixed(0)}%
                    </span>
                  </div>
                  <Progress value={analysisResults.consensus.agreementLevel * 100} />
                  
                  <div className="space-y-2">
                    <h4 className="font-medium">Key Factors</h4>
                    <ul className="space-y-1">
                      {analysisResults.consensus.keyFactors.map((factor, index) => (
                        <li key={index} className="flex items-start space-x-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {analysisResults.conflicts.length > 0 && (
                    <Alert>
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Conflicts Detected:</strong> Some agents have differing opinions. 
                        Review individual agent analyses for details.
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="risk" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="h-5 w-5 text-orange-500" />
                    <span>Risk Metrics</span>
                  </CardTitle>
                  <CardDescription>Detailed risk analysis and volatility assessment</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">Volatility</span>
                          <span className="text-sm text-muted-foreground">
                            {(analysisResults.agentAnalyses.risk.volatility * 100).toFixed(1)}%
                          </span>
                        </div>
                        <Progress value={analysisResults.agentAnalyses.risk.volatility * 100} />
                      </div>
                      
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">Risk Score</span>
                          <span className="text-sm text-muted-foreground">
                            {analysisResults.agentAnalyses.risk.riskScore}/100
                          </span>
                        </div>
                        <Progress value={analysisResults.agentAnalyses.risk.riskScore} />
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <h4 className="font-medium">Risk Recommendations</h4>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-start space-x-2">
                          <Target className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                          <span>Position size: {analysisResults.positionSize}% of portfolio</span>
                        </li>
                        <li className="flex items-start space-x-2">
                          <Shield className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <span>Set stop-loss at ${analysisResults.stopLoss}</span>
                        </li>
                        <li className="flex items-start space-x-2">
                          <Zap className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                          <span>Monitor position closely for exit signals</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="recommendations" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Recommended Actions</CardTitle>
                  <CardDescription>Based on comprehensive AI analysis</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Alert className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <AlertDescription className="text-green-800 dark:text-green-200">
                        <strong>Primary Action:</strong> {analysisResults.finalRecommendation} {analysisResults.symbol} 
                        with {analysisResults.positionSize}% position size
                      </AlertDescription>
                    </Alert>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 border rounded-lg">
                        <h4 className="font-medium mb-2">Entry Strategy</h4>
                        <ul className="text-sm space-y-1 text-muted-foreground">
                          <li>• Target entry around current price: ${analysisResults.currentPrice}</li>
                          <li>• Consider dollar-cost averaging for large positions</li>
                          <li>• Monitor for better entry points on dips</li>
                        </ul>
                      </div>
                      
                      <div className="p-4 border rounded-lg">
                        <h4 className="font-medium mb-2">Risk Management</h4>
                        <ul className="text-sm space-y-1 text-muted-foreground">
                          <li>• Set stop-loss at ${analysisResults.stopLoss}</li>
                          <li>• Take profits at ${analysisResults.targetPrice}</li>
                          <li>• Review position weekly</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  )
}

export default StockAnalysis
