import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'
import Navbar from '@/components/Navbar'
import Dashboard from '@/components/Dashboard'
import StockAnalysis from '@/components/StockAnalysis'
import Portfolio from '@/components/Portfolio'
import Settings from '@/components/Settings'
import EventMonitor from '@/components/EventMonitor'
import CostOptimizer from '@/components/CostOptimizer'
import './App.css'

function App() {
  const [theme, setTheme] = useState('light')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 앱 초기화
    const initializeApp = async () => {
      try {
        // 테마 설정 로드
        const savedTheme = localStorage.getItem('theme') || 'light'
        setTheme(savedTheme)
        
        // 초기 데이터 로드 시뮬레이션
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        setIsLoading(false)
      } catch (error) {
        console.error('App initialization failed:', error)
        setIsLoading(false)
      }
    }

    initializeApp()
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <h2 className="text-xl font-semibold text-foreground">AI Stock Trading System v2.0</h2>
          <p className="text-muted-foreground">Initializing advanced multi-agent system...</p>
          <div className="text-sm text-muted-foreground space-y-1">
            <div>✓ AI Model Abstraction Layer</div>
            <div>✓ Real-time Event Architecture</div>
            <div>✓ Cost Optimization Engine</div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <ThemeProvider defaultTheme={theme} storageKey="vite-ui-theme">
      <Router>
        <div className={`min-h-screen bg-background transition-colors duration-300 ${theme}`}>
          <Navbar theme={theme} toggleTheme={toggleTheme} />
          
          <main className="container mx-auto px-4 py-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analysis" element={<StockAnalysis />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/events" element={<EventMonitor />} />
              <Route path="/optimizer" element={<CostOptimizer />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
          
          <Toaster />
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App
