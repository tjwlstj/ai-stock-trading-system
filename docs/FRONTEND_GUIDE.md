# 🎨 Frontend Development Guide

## UI/UX Best Practices

### Loading States & Skeleton UI

**Stock Quote Loading**
```tsx
// components/StockQuote.tsx
import { Skeleton } from '@/components/ui/skeleton'

interface StockQuoteProps {
  symbol: string
  isLoading?: boolean
}

export function StockQuote({ symbol, isLoading }: StockQuoteProps) {
  if (isLoading) {
    return (
      <div className="p-4 border rounded-lg">
        <Skeleton className="h-6 w-20 mb-2" />
        <Skeleton className="h-8 w-32 mb-1" />
        <Skeleton className="h-4 w-24" />
      </div>
    )
  }

  return (
    <div className="p-4 border rounded-lg">
      <h3 className="font-semibold text-lg">{symbol}</h3>
      <p className="text-2xl font-bold">$150.25</p>
      <p className="text-green-600">+2.35 (1.59%)</p>
    </div>
  )
}
```

**Analysis Loading with Progress**
```tsx
// components/AnalysisCard.tsx
import { Progress } from '@/components/ui/progress'
import { Loader2 } from 'lucide-react'

interface AnalysisCardProps {
  symbol: string
  isAnalyzing?: boolean
  progress?: number
}

export function AnalysisCard({ symbol, isAnalyzing, progress = 0 }: AnalysisCardProps) {
  if (isAnalyzing) {
    return (
      <div className="p-6 border rounded-lg">
        <div className="flex items-center gap-2 mb-4">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Analyzing {symbol}...</span>
        </div>
        <Progress value={progress} className="mb-2" />
        <p className="text-sm text-gray-600">
          {progress < 30 && "Fetching market data..."}
          {progress >= 30 && progress < 70 && "Running AI analysis..."}
          {progress >= 70 && "Generating recommendations..."}
        </p>
      </div>
    )
  }

  return (
    <div className="p-6 border rounded-lg">
      {/* Analysis results */}
    </div>
  )
}
```

### Error Handling & Retry

**Error Boundary Component**
```tsx
// components/ErrorBoundary.tsx
import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
          <p className="text-gray-600 mb-4">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <Button
            onClick={() => this.setState({ hasError: false })}
            className="flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Try Again
          </Button>
        </div>
      )
    }

    return this.props.children
  }
}
```

**Network Error Handling**
```tsx
// hooks/useStockData.ts
import { useState, useEffect } from 'react'
import { toast } from '@/components/ui/use-toast'

interface UseStockDataResult {
  data: StockQuote | null
  isLoading: boolean
  error: string | null
  retry: () => void
}

export function useStockData(symbol: string): UseStockDataResult {
  const [data, setData] = useState<StockQuote | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/stocks/${symbol}`)
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Symbol "${symbol}" not found`)
        } else if (response.status === 429) {
          throw new Error('Rate limit exceeded. Please try again later.')
        } else if (response.status >= 500) {
          throw new Error('Server error. Please try again.')
        } else {
          throw new Error('Failed to fetch stock data')
        }
      }

      const stockData = await response.json()
      setData(stockData)
      
      // Reset retry count on success
      setRetryCount(0)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      
      // Show toast notification
      toast({
        title: "Error fetching stock data",
        description: errorMessage,
        variant: "destructive",
      })
      
    } finally {
      setIsLoading(false)
    }
  }

  const retry = () => {
    setRetryCount(prev => prev + 1)
    fetchData()
  }

  useEffect(() => {
    if (symbol) {
      fetchData()
    }
  }, [symbol, retryCount])

  return { data, isLoading, error, retry }
}
```

**Retry Button Component**
```tsx
// components/RetryButton.tsx
import { Button } from '@/components/ui/button'
import { RefreshCw, Wifi } from 'lucide-react'

interface RetryButtonProps {
  onRetry: () => void
  isRetrying?: boolean
  error?: string
}

export function RetryButton({ onRetry, isRetrying, error }: RetryButtonProps) {
  const isNetworkError = error?.includes('fetch') || error?.includes('network')

  return (
    <div className="flex flex-col items-center gap-3 p-4">
      {isNetworkError && (
        <Wifi className="h-8 w-8 text-gray-400" />
      )}
      
      <p className="text-sm text-gray-600 text-center">
        {isNetworkError 
          ? "Check your internet connection and try again"
          : error || "Something went wrong"
        }
      </p>
      
      <Button
        onClick={onRetry}
        disabled={isRetrying}
        variant="outline"
        size="sm"
        className="flex items-center gap-2"
      >
        <RefreshCw className={`h-4 w-4 ${isRetrying ? 'animate-spin' : ''}`} />
        {isRetrying ? 'Retrying...' : 'Try Again'}
      </Button>
    </div>
  )
}
```

### Real-time Updates & WebSocket

**WebSocket Hook**
```tsx
// hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react'

interface UseWebSocketOptions {
  onMessage?: (data: any) => void
  onError?: (error: Event) => void
  reconnectInterval?: number
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<NodeJS.Timeout>()

  const connect = () => {
    try {
      ws.current = new WebSocket(url)
      
      ws.current.onopen = () => {
        setIsConnected(true)
        console.log('WebSocket connected')
      }
      
      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data)
        setLastMessage(data)
        options.onMessage?.(data)
      }
      
      ws.current.onclose = () => {
        setIsConnected(false)
        console.log('WebSocket disconnected')
        
        // Auto-reconnect
        if (options.reconnectInterval) {
          reconnectTimer.current = setTimeout(connect, options.reconnectInterval)
        }
      }
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        options.onError?.(error)
      }
      
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }

  const disconnect = () => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current)
    }
    ws.current?.close()
  }

  const sendMessage = (message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }

  useEffect(() => {
    connect()
    return disconnect
  }, [url])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect
  }
}
```

**Real-time Stock Ticker**
```tsx
// components/StockTicker.tsx
import { useWebSocket } from '@/hooks/useWebSocket'
import { Badge } from '@/components/ui/badge'

interface StockTickerProps {
  symbols: string[]
}

export function StockTicker({ symbols }: StockTickerProps) {
  const [quotes, setQuotes] = useState<Record<string, StockQuote>>({})

  const { isConnected } = useWebSocket('ws://localhost:8000/ws/quotes', {
    onMessage: (data) => {
      if (data.type === 'quote_update') {
        setQuotes(prev => ({
          ...prev,
          [data.symbol]: data.quote
        }))
      }
    },
    reconnectInterval: 5000
  })

  return (
    <div className="flex items-center gap-4 p-2 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-sm font-medium">
          {isConnected ? 'Live' : 'Disconnected'}
        </span>
      </div>
      
      <div className="flex gap-4 overflow-x-auto">
        {symbols.map(symbol => {
          const quote = quotes[symbol]
          if (!quote) return null
          
          return (
            <div key={symbol} className="flex items-center gap-2 whitespace-nowrap">
              <span className="font-medium">{symbol}</span>
              <span className="text-lg">${quote.price}</span>
              <Badge variant={quote.change >= 0 ? 'default' : 'destructive'}>
                {quote.change >= 0 ? '+' : ''}{quote.change_percent}%
              </Badge>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

### Responsive Design

**Mobile-First Dashboard**
```tsx
// components/Dashboard.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function Dashboard() {
  return (
    <div className="container mx-auto p-4">
      {/* Mobile: Tabs, Desktop: Grid */}
      <div className="block md:hidden">
        <Tabs defaultValue="portfolio" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
            <TabsTrigger value="watchlist">Watchlist</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>
          
          <TabsContent value="portfolio">
            <PortfolioCard />
          </TabsContent>
          
          <TabsContent value="watchlist">
            <WatchlistCard />
          </TabsContent>
          
          <TabsContent value="analysis">
            <AnalysisCard />
          </TabsContent>
        </Tabs>
      </div>

      {/* Desktop: Grid Layout */}
      <div className="hidden md:grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PortfolioCard />
        <WatchlistCard />
        <AnalysisCard />
      </div>
    </div>
  )
}
```

**Responsive Chart Component**
```tsx
// components/StockChart.tsx
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts'

interface StockChartProps {
  data: ChartDataPoint[]
  height?: number
}

export function StockChart({ data, height = 300 }: StockChartProps) {
  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis 
            dataKey="timestamp" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => new Date(value).toLocaleDateString()}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip 
            labelFormatter={(value) => new Date(value).toLocaleString()}
            formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
          />
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#2563eb" 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
```

### Performance Optimization

**Lazy Loading & Code Splitting**
```tsx
// App.tsx
import { lazy, Suspense } from 'react'
import { Skeleton } from '@/components/ui/skeleton'

// Lazy load heavy components
const Dashboard = lazy(() => import('@/components/Dashboard'))
const AnalysisPage = lazy(() => import('@/pages/AnalysisPage'))
const PortfolioPage = lazy(() => import('@/pages/PortfolioPage'))

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={
          <Suspense fallback={<DashboardSkeleton />}>
            <Dashboard />
          </Suspense>
        } />
        
        <Route path="/analysis" element={
          <Suspense fallback={<PageSkeleton />}>
            <AnalysisPage />
          </Suspense>
        } />
        
        <Route path="/portfolio" element={
          <Suspense fallback={<PageSkeleton />}>
            <PortfolioPage />
          </Suspense>
        } />
      </Routes>
    </Router>
  )
}
```

**Memoization & Virtual Scrolling**
```tsx
// components/StockList.tsx
import { memo, useMemo } from 'react'
import { FixedSizeList as List } from 'react-window'

interface StockListProps {
  stocks: StockQuote[]
  onSelectStock: (symbol: string) => void
}

const StockItem = memo(({ index, style, data }: any) => {
  const { stocks, onSelectStock } = data
  const stock = stocks[index]

  return (
    <div style={style} className="p-2 border-b">
      <button
        onClick={() => onSelectStock(stock.symbol)}
        className="w-full text-left hover:bg-gray-50 p-2 rounded"
      >
        <div className="flex justify-between items-center">
          <span className="font-medium">{stock.symbol}</span>
          <span className="text-lg">${stock.price}</span>
        </div>
      </button>
    </div>
  )
})

export const StockList = memo(({ stocks, onSelectStock }: StockListProps) => {
  const itemData = useMemo(() => ({ stocks, onSelectStock }), [stocks, onSelectStock])

  return (
    <List
      height={400}
      itemCount={stocks.length}
      itemSize={60}
      itemData={itemData}
    >
      {StockItem}
    </List>
  )
})
```

### Accessibility

**Keyboard Navigation**
```tsx
// components/SearchInput.tsx
import { useState, useRef, useEffect } from 'react'
import { Input } from '@/components/ui/input'

interface SearchInputProps {
  onSearch: (query: string) => void
  suggestions: string[]
}

export function SearchInput({ onSearch, suggestions }: SearchInputProps) {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        )
        break
        
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
        break
        
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0) {
          setQuery(suggestions[selectedIndex])
          onSearch(suggestions[selectedIndex])
        } else {
          onSearch(query)
        }
        setShowSuggestions(false)
        break
        
      case 'Escape':
        setShowSuggestions(false)
        inputRef.current?.blur()
        break
    }
  }

  return (
    <div className="relative">
      <Input
        ref={inputRef}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => setShowSuggestions(true)}
        placeholder="Search stocks..."
        aria-label="Search for stocks"
        aria-expanded={showSuggestions}
        aria-haspopup="listbox"
        role="combobox"
      />
      
      {showSuggestions && suggestions.length > 0 && (
        <ul
          className="absolute z-10 w-full bg-white border rounded-md shadow-lg max-h-60 overflow-auto"
          role="listbox"
        >
          {suggestions.map((suggestion, index) => (
            <li
              key={suggestion}
              className={`p-2 cursor-pointer hover:bg-gray-100 ${
                index === selectedIndex ? 'bg-blue-100' : ''
              }`}
              onClick={() => {
                setQuery(suggestion)
                onSearch(suggestion)
                setShowSuggestions(false)
              }}
              role="option"
              aria-selected={index === selectedIndex}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

**Screen Reader Support**
```tsx
// components/StockQuote.tsx
interface StockQuoteProps {
  quote: StockQuote
}

export function StockQuote({ quote }: StockQuoteProps) {
  const changeDirection = quote.change >= 0 ? 'up' : 'down'
  const changeColor = quote.change >= 0 ? 'text-green-600' : 'text-red-600'

  return (
    <div 
      className="p-4 border rounded-lg"
      role="region"
      aria-label={`Stock quote for ${quote.symbol}`}
    >
      <h3 className="font-semibold text-lg">{quote.symbol}</h3>
      
      <p className="text-2xl font-bold">
        <span aria-label={`Current price: $${quote.price}`}>
          ${quote.price}
        </span>
      </p>
      
      <p className={changeColor}>
        <span 
          aria-label={`Price change: ${changeDirection} by $${Math.abs(quote.change)} or ${Math.abs(quote.change_percent)}%`}
        >
          {quote.change >= 0 ? '+' : ''}{quote.change} ({quote.change_percent}%)
        </span>
      </p>
      
      <p className="text-sm text-gray-600">
        <span aria-label={`Volume: ${quote.volume.toLocaleString()} shares`}>
          Volume: {quote.volume.toLocaleString()}
        </span>
      </p>
    </div>
  )
}
```

### Testing Frontend Components

**Component Testing with React Testing Library**
```tsx
// __tests__/StockQuote.test.tsx
import { render, screen } from '@testing-library/react'
import { StockQuote } from '@/components/StockQuote'

const mockQuote = {
  symbol: 'AAPL',
  price: 150.25,
  change: 2.35,
  change_percent: 1.59,
  volume: 1234567
}

describe('StockQuote', () => {
  it('renders stock information correctly', () => {
    render(<StockQuote quote={mockQuote} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('$150.25')).toBeInTheDocument()
    expect(screen.getByText('+2.35 (1.59%)')).toBeInTheDocument()
  })

  it('shows positive change in green', () => {
    render(<StockQuote quote={mockQuote} />)
    
    const changeElement = screen.getByText('+2.35 (1.59%)')
    expect(changeElement).toHaveClass('text-green-600')
  })

  it('shows negative change in red', () => {
    const negativeQuote = { ...mockQuote, change: -2.35, change_percent: -1.59 }
    render(<StockQuote quote={negativeQuote} />)
    
    const changeElement = screen.getByText('-2.35 (-1.59%)')
    expect(changeElement).toHaveClass('text-red-600')
  })
})
```

**E2E Testing with Playwright**
```typescript
// e2e/stock-search.spec.ts
import { test, expect } from '@playwright/test'

test('stock search workflow', async ({ page }) => {
  await page.goto('/')
  
  // Search for a stock
  await page.fill('[placeholder="Search stocks..."]', 'AAPL')
  await page.press('[placeholder="Search stocks..."]', 'Enter')
  
  // Wait for results
  await expect(page.locator('[data-testid="stock-quote"]')).toBeVisible()
  
  // Verify stock information is displayed
  await expect(page.locator('text=AAPL')).toBeVisible()
  await expect(page.locator('text=/\\$\\d+\\.\\d+/')).toBeVisible()
  
  // Test error handling
  await page.fill('[placeholder="Search stocks..."]', 'INVALID')
  await page.press('[placeholder="Search stocks..."]', 'Enter')
  
  await expect(page.locator('text=Symbol not found')).toBeVisible()
  await expect(page.locator('button:has-text("Try Again")')).toBeVisible()
})
```

This frontend guide provides comprehensive patterns for building a robust, accessible, and performant React application with proper error handling, loading states, and user experience considerations.
