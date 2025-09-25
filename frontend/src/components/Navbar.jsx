import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  BarChart3, 
  TrendingUp, 
  Briefcase, 
  Settings, 
  Moon, 
  Sun,
  Menu,
  X,
  Bot,
  Activity
} from 'lucide-react'

const Navbar = ({ theme, toggleTheme }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/analysis', label: 'AI Analysis', icon: Bot },
    { path: '/portfolio', label: 'Portfolio', icon: Briefcase },
    { path: '/settings', label: 'Settings', icon: Settings }
  ]

  const isActivePath = (path) => location.pathname === path

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-foreground">AI Stock Trader</h1>
              <p className="text-xs text-muted-foreground">Multi-Agent Analysis System</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <Link key={item.path} to={item.path}>
                  <Button
                    variant={isActivePath(item.path) ? "default" : "ghost"}
                    size="sm"
                    className="flex items-center space-x-2 transition-all duration-200"
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                    {item.path === '/analysis' && (
                      <Badge variant="secondary" className="ml-1 text-xs">
                        AI
                      </Badge>
                    )}
                  </Button>
                </Link>
              )
            })}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-2">
            {/* Market Status Indicator */}
            <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/20">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-700 dark:text-green-400">
                Market Open
              </span>
            </div>

            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="w-9 h-9 p-0"
            >
              {theme === 'light' ? (
                <Moon className="h-4 w-4" />
              ) : (
                <Sun className="h-4 w-4" />
              )}
            </Button>

            {/* Mobile Menu Toggle */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden w-9 h-9 p-0"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? (
                <X className="h-4 w-4" />
              ) : (
                <Menu className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t bg-background/95 backdrop-blur">
            <div className="px-2 py-3 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <Button
                      variant={isActivePath(item.path) ? "default" : "ghost"}
                      size="sm"
                      className="w-full justify-start space-x-2"
                    >
                      <Icon className="h-4 w-4" />
                      <span>{item.label}</span>
                      {item.path === '/analysis' && (
                        <Badge variant="secondary" className="ml-auto text-xs">
                          AI
                        </Badge>
                      )}
                    </Button>
                  </Link>
                )
              })}
              
              {/* Mobile Market Status */}
              <div className="flex items-center justify-center space-x-2 py-2 mt-3 border-t">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-700 dark:text-green-400">
                  Market Open
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
