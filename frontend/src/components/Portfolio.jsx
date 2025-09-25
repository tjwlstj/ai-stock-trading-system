import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Percent,
  Target,
  AlertTriangle,
  Plus,
  Minus,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

const Portfolio = () => {
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 125430.50,
    totalCost: 118750.00,
    totalGainLoss: 6680.50,
    totalGainLossPercent: 5.63,
    dayChange: 2340.75,
    dayChangePercent: 1.89
  })

  const [holdings, setHoldings] = useState([
    {
      symbol: 'AAPL',
      shares: 50,
      avgCost: 245.30,
      currentPrice: 256.87,
      marketValue: 12843.50,
      gainLoss: 578.50,
      gainLossPercent: 4.71,
      dayChange: 122.50,
      dayChangePercent: 0.96,
      allocation: 10.2,
      recommendation: 'BUY',
      aiConfidence: 0.85
    },
    {
      symbol: 'GOOGL',
      shares: 25,
      avgCost: 175.80,
      currentPrice: 178.32,
      marketValue: 4458.00,
      gainLoss: 63.00,
      gainLossPercent: 1.43,
      dayChange: -30.75,
      dayChangePercent: -0.68,
      allocation: 3.6,
      recommendation: 'HOLD',
      aiConfidence: 0.72
    },
    {
      symbol: 'MSFT',
      shares: 30,
      avgCost: 420.15,
      currentPrice: 445.67,
      marketValue: 13370.10,
      gainLoss: 765.60,
      gainLossPercent: 6.08,
      dayChange: 176.70,
      dayChangePercent: 1.34,
      allocation: 10.7,
      recommendation: 'BUY',
      aiConfidence: 0.91
    },
    {
      symbol: 'TSLA',
      shares: 40,
      avgCost: 275.20,
      currentPrice: 267.89,
      marketValue: 10715.60,
      gainLoss: -292.40,
      gainLossPercent: -2.66,
      dayChange: -338.00,
      dayChangePercent: -3.06,
      allocation: 8.5,
      recommendation: 'SELL',
      aiConfidence: 0.78
    },
    {
      symbol: 'NVDA',
      shares: 60,
      avgCost: 132.45,
      currentPrice: 145.23,
      marketValue: 8713.80,
      gainLoss: 766.80,
      gainLossPercent: 9.65,
      dayChange: 740.40,
      dayChangePercent: 9.29,
      allocation: 6.9,
      recommendation: 'BUY',
      aiConfidence: 0.88
    }
  ])

  const [performanceData] = useState([
    { date: '2025-09-01', value: 118750, benchmark: 118000 },
    { date: '2025-09-05', value: 120200, benchmark: 119500 },
    { date: '2025-09-10', value: 119800, benchmark: 118800 },
    { date: '2025-09-15', value: 122100, benchmark: 120200 },
    { date: '2025-09-20', value: 123900, benchmark: 121800 },
    { date: '2025-09-25', value: 125430, benchmark: 122500 }
  ])

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'BUY': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'SELL': return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
      default: return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value)
  }

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Portfolio Management</h1>
          <p className="text-muted-foreground">
            AI-powered portfolio optimization and tracking
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Position
          </Button>
          <Button variant="outline" size="sm">
            <BarChart3 className="h-4 w-4 mr-2" />
            Rebalance
          </Button>
        </div>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(portfolioData.totalValue)}</div>
            <p className="text-xs text-muted-foreground">
              Cost basis: {formatCurrency(portfolioData.totalCost)}
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Gain/Loss</CardTitle>
            <Percent className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${portfolioData.totalGainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(portfolioData.totalGainLoss)}
            </div>
            <p className={`text-xs ${portfolioData.totalGainLossPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent(portfolioData.totalGainLossPercent)}
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Day Change</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${portfolioData.dayChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(portfolioData.dayChange)}
            </div>
            <p className={`text-xs ${portfolioData.dayChangePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent(portfolioData.dayChangePercent)}
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Holdings</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{holdings.length}</div>
            <p className="text-xs text-muted-foreground">
              Active positions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="holdings" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="holdings">Holdings</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="analysis">AI Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="holdings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Current Holdings</CardTitle>
              <CardDescription>Your portfolio positions with AI recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {holdings.map((holding, index) => (
                  <div key={index} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="grid grid-cols-1 lg:grid-cols-6 gap-4 items-center">
                      {/* Stock Info */}
                      <div className="lg:col-span-1">
                        <h3 className="font-semibold text-lg">{holding.symbol}</h3>
                        <p className="text-sm text-muted-foreground">
                          {holding.shares} shares
                        </p>
                      </div>

                      {/* Price Info */}
                      <div className="lg:col-span-1">
                        <p className="font-medium">{formatCurrency(holding.currentPrice)}</p>
                        <p className={`text-sm ${holding.dayChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {holding.dayChange >= 0 ? '+' : ''}{formatCurrency(holding.dayChange)} ({formatPercent(holding.dayChangePercent)})
                        </p>
                      </div>

                      {/* Market Value */}
                      <div className="lg:col-span-1">
                        <p className="font-medium">{formatCurrency(holding.marketValue)}</p>
                        <p className="text-sm text-muted-foreground">
                          {holding.allocation}% of portfolio
                        </p>
                      </div>

                      {/* Gain/Loss */}
                      <div className="lg:col-span-1">
                        <p className={`font-medium ${holding.gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(holding.gainLoss)}
                        </p>
                        <p className={`text-sm ${holding.gainLossPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatPercent(holding.gainLossPercent)}
                        </p>
                      </div>

                      {/* AI Recommendation */}
                      <div className="lg:col-span-1">
                        <Badge className={getRecommendationColor(holding.recommendation)}>
                          {holding.recommendation}
                        </Badge>
                        <p className="text-sm text-muted-foreground mt-1">
                          AI: {(holding.aiConfidence * 100).toFixed(0)}%
                        </p>
                      </div>

                      {/* Actions */}
                      <div className="lg:col-span-1 flex space-x-2">
                        <Button variant="outline" size="sm">
                          <Plus className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Minus className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Target className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Chart */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Portfolio Performance</CardTitle>
                <CardDescription>Portfolio value vs benchmark over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value) => [formatCurrency(value), '']} />
                    <Area 
                      type="monotone" 
                      dataKey="value" 
                      stackId="1" 
                      stroke="#3b82f6" 
                      fill="#3b82f6" 
                      fillOpacity={0.3}
                      name="Portfolio"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="benchmark" 
                      stackId="2" 
                      stroke="#10b981" 
                      fill="#10b981" 
                      fillOpacity={0.2}
                      name="Benchmark"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>Key portfolio statistics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Total Return</span>
                  <span className="text-sm font-bold text-green-600">
                    {formatPercent(portfolioData.totalGainLossPercent)}
                  </span>
                </div>
                <Progress value={Math.abs(portfolioData.totalGainLossPercent) * 10} />

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Best Performer</span>
                  <span className="text-sm font-bold">NVDA (+9.65%)</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Worst Performer</span>
                  <span className="text-sm font-bold text-red-600">TSLA (-2.66%)</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Sharpe Ratio</span>
                  <span className="text-sm font-bold">1.24</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Max Drawdown</span>
                  <span className="text-sm font-bold text-red-600">-3.2%</span>
                </div>
              </CardContent>
            </Card>

            {/* Allocation Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Asset Allocation</CardTitle>
                <CardDescription>Portfolio distribution by holding</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {holdings.map((holding, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">{holding.symbol}</span>
                        <span className="text-sm text-muted-foreground">{holding.allocation}%</span>
                      </div>
                      <Progress value={holding.allocation * 10} />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* AI Recommendations Summary */}
            <Card>
              <CardHeader>
                <CardTitle>AI Recommendations Summary</CardTitle>
                <CardDescription>Current AI analysis across all holdings</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="p-3 rounded-lg bg-green-100 dark:bg-green-900/20">
                      <div className="text-2xl font-bold text-green-600">
                        {holdings.filter(h => h.recommendation === 'BUY').length}
                      </div>
                      <p className="text-sm text-green-700 dark:text-green-400">BUY</p>
                    </div>
                    <div className="p-3 rounded-lg bg-yellow-100 dark:bg-yellow-900/20">
                      <div className="text-2xl font-bold text-yellow-600">
                        {holdings.filter(h => h.recommendation === 'HOLD').length}
                      </div>
                      <p className="text-sm text-yellow-700 dark:text-yellow-400">HOLD</p>
                    </div>
                    <div className="p-3 rounded-lg bg-red-100 dark:bg-red-900/20">
                      <div className="text-2xl font-bold text-red-600">
                        {holdings.filter(h => h.recommendation === 'SELL').length}
                      </div>
                      <p className="text-sm text-red-700 dark:text-red-400">SELL</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-medium">Average AI Confidence</h4>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">
                        {(holdings.reduce((sum, h) => sum + h.aiConfidence, 0) / holdings.length * 100).toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={holdings.reduce((sum, h) => sum + h.aiConfidence, 0) / holdings.length * 100} />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Portfolio Optimization */}
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Optimization</CardTitle>
                <CardDescription>AI-suggested improvements</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-3 border rounded-lg bg-blue-50 dark:bg-blue-900/20">
                    <div className="flex items-start space-x-2">
                      <TrendingUp className="h-5 w-5 text-blue-500 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-700 dark:text-blue-300">Increase MSFT Position</h4>
                        <p className="text-sm text-blue-600 dark:text-blue-400">
                          Strong AI confidence (91%) suggests increasing allocation
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-3 border rounded-lg bg-red-50 dark:bg-red-900/20">
                    <div className="flex items-start space-x-2">
                      <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-red-700 dark:text-red-300">Consider Reducing TSLA</h4>
                        <p className="text-sm text-red-600 dark:text-red-400">
                          AI recommends SELL with current market conditions
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-3 border rounded-lg bg-green-50 dark:bg-green-900/20">
                    <div className="flex items-start space-x-2">
                      <Target className="h-5 w-5 text-green-500 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-green-700 dark:text-green-300">Rebalance Opportunity</h4>
                        <p className="text-sm text-green-600 dark:text-green-400">
                          Portfolio could benefit from sector diversification
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Portfolio
