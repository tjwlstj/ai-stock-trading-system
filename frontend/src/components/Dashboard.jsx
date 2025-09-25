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
  Activity, 
  AlertTriangle,
  Bot,
  Target,
  Shield,
  Zap,
  RefreshCw
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

const Dashboard = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [marketData, setMarketData] = useState({
    totalValue: 125430.50,
    dailyChange: 2.34,
    dailyChangePercent: 1.89,
    activePositions: 8,
    aiRecommendations: 12
  })

  // 모의 주식 데이터
  const [stockData] = useState([
    { symbol: 'AAPL', price: 256.87, change: 2.45, changePercent: 0.96, recommendation: 'BUY', confidence: 0.85 },
    { symbol: 'GOOGL', price: 178.32, change: -1.23, changePercent: -0.68, recommendation: 'HOLD', confidence: 0.72 },
    { symbol: 'MSFT', price: 445.67, change: 5.89, changePercent: 1.34, recommendation: 'BUY', confidence: 0.91 },
    { symbol: 'TSLA', price: 267.89, change: -8.45, changePercent: -3.06, recommendation: 'SELL', confidence: 0.78 },
    { symbol: 'NVDA', price: 145.23, change: 12.34, changePercent: 9.29, recommendation: 'BUY', confidence: 0.88 }
  ])

  // AI 에이전트 상태
  const [agentStatus] = useState([
    { name: 'Optimistic Analyst', status: 'active', lastAnalysis: '2 min ago', confidence: 0.87 },
    { name: 'Pessimistic Analyst', status: 'active', lastAnalysis: '3 min ago', confidence: 0.74 },
    { name: 'Risk Manager', status: 'active', lastAnalysis: '1 min ago', confidence: 0.92 },
    { name: 'Data Collector', status: 'active', lastAnalysis: '30 sec ago', confidence: 0.95 }
  ])

  // 차트 데이터
  const [chartData] = useState([
    { time: '09:30', value: 123500, volume: 1200000 },
    { time: '10:00', value: 124200, volume: 1350000 },
    { time: '10:30', value: 123800, volume: 1100000 },
    { time: '11:00', value: 125100, volume: 1450000 },
    { time: '11:30', value: 124900, volume: 1300000 },
    { time: '12:00', value: 125430, volume: 1250000 }
  ])

  const pieData = [
    { name: 'Technology', value: 45, color: '#3b82f6' },
    { name: 'Healthcare', value: 25, color: '#10b981' },
    { name: 'Finance', value: 20, color: '#f59e0b' },
    { name: 'Energy', value: 10, color: '#ef4444' }
  ]

  const refreshData = async () => {
    setIsLoading(true)
    // 데이터 새로고침 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1500))
    setLastUpdate(new Date())
    setIsLoading(false)
  }

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'BUY': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'SELL': return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
      default: return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AI Trading Dashboard</h1>
          <p className="text-muted-foreground">
            Multi-agent analysis system • Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <Button onClick={refreshData} disabled={isLoading} className="flex items-center space-x-2">
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Portfolio Value</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${marketData.totalValue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className={`inline-flex items-center ${marketData.dailyChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {marketData.dailyChange >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                ${Math.abs(marketData.dailyChange)} ({marketData.dailyChangePercent}%) today
              </span>
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Positions</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{marketData.activePositions}</div>
            <p className="text-xs text-muted-foreground">
              Across {pieData.length} sectors
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Recommendations</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{marketData.aiRecommendations}</div>
            <p className="text-xs text-muted-foreground">
              From {agentStatus.length} active agents
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Level</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">Medium</div>
            <Progress value={45} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="stocks">Stocks</TabsTrigger>
          <TabsTrigger value="agents">AI Agents</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Portfolio Performance Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Performance</CardTitle>
                <CardDescription>Real-time value tracking</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Value']} />
                    <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Sector Allocation */}
            <Card>
              <CardHeader>
                <CardTitle>Sector Allocation</CardTitle>
                <CardDescription>Portfolio diversification</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value}%`, 'Allocation']} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="grid grid-cols-2 gap-2 mt-4">
                  {pieData.map((item, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                      <span className="text-sm">{item.name} ({item.value}%)</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="stocks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Stock Watchlist</CardTitle>
              <CardDescription>AI-powered recommendations and analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stockData.map((stock, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div>
                        <h3 className="font-semibold">{stock.symbol}</h3>
                        <p className="text-sm text-muted-foreground">${stock.price}</p>
                      </div>
                      <div className={`flex items-center space-x-1 ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {stock.change >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                        <span className="text-sm font-medium">
                          ${Math.abs(stock.change)} ({stock.changePercent}%)
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge className={getRecommendationColor(stock.recommendation)}>
                        {stock.recommendation}
                      </Badge>
                      <div className="text-right">
                        <p className="text-sm font-medium">Confidence</p>
                        <p className="text-sm text-muted-foreground">{(stock.confidence * 100).toFixed(0)}%</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {agentStatus.map((agent, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
                      {agent.status}
                    </Badge>
                  </div>
                  <CardDescription>Last analysis: {agent.lastAnalysis}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Confidence Level</span>
                      <span className="text-sm text-muted-foreground">{(agent.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <Progress value={agent.confidence * 100} />
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <Zap className="h-4 w-4" />
                      <span>Processing real-time data</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Trading Volume Analysis</CardTitle>
              <CardDescription>Market activity throughout the day</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip formatter={(value) => [value.toLocaleString(), 'Volume']} />
                  <Bar dataKey="volume" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Dashboard
