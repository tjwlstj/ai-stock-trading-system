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
  Activity,
  Zap,
  Target
} from 'lucide-react'

const Navbar = ({ theme, toggleTheme }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/analysis', label: 'AI Analysis', icon: Bot, badge: 'AI' },
    { path: '/portfolio', label: 'Portfolio', icon: Briefcase },
    { path: '/events', label: 'Events', icon: Activity, badge: 'LIVE' },
    { path: '/optimizer', label: 'Optimizer', icon: Target, badge: 'NEW' },
    { path: '/settings', label: 'Settings', icon: Settings }
  ]

  const isActivePath = (path) => location.pathname === path

  const getBadgeVariant = (badge) => {
    switch (badge) {
      case 'AI': return 'default'
      case 'LIVE': return 'destructive'
      case 'NEW': return 'secondary'
      default: return 'secondary'
    }
  }

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
              <h1 className="text-xl font-bold text-foreground">AI Stock Trader v2.0</h1>
              <p className="text-xs text-muted-foreground">Advanced Multi-Agent System</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1">
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
                    {item.badge && (
                      <Badge variant={getBadgeVariant(item.badge)} className="ml-1 text-xs">
                        {item.badge}
                      </Badge>
                    )}
                  </Button>
                </Link>
              )
            })}
          </div>

          {/* Compact Desktop Navigation for medium screens */}
          <div className="hidden md:flex lg:hidden items-center space-x-1">
            {navItems.slice(0, 4).map((item) => {
              const Icon = item.icon
              return (
                <Link key={item.path} to={item.path}>
                  <Button
                    variant={isActivePath(item.path) ? "default" : "ghost"}
                    size="sm"
                    className="flex items-center space-x-1 transition-all duration-200"
                  >
                    <Icon className="h-4 w-4" />
                    <span className="hidden xl:inline">{item.label}</span>
                    {item.badge && (
                      <Badge variant={getBadgeVariant(item.badge)} className="ml-1 text-xs">
                        {item.badge}
                      </Badge>
                    )}
                  </Button>
                </Link>
              )
            })}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-2">
            {/* System Status Indicators */}
            <div className="hidden sm:flex items-center space-x-3">
              {/* Market Status */}
              <div className="flex items-center space-x-2 px-2 py-1 rounded-full bg-green-100 dark:bg-green-900/20">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-green-700 dark:text-green-400">
                  Market
                </span>
              </div>
              
              {/* AI Status */}
              <div className="flex items-center space-x-2 px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/20">
                <Zap className="w-3 h-3 text-blue-500" />
                <span className="text-xs font-medium text-blue-700 dark:text-blue-400">
                  AI Active
                </span>
              </div>
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
                      {item.badge && (
                        <Badge variant={getBadgeVariant(item.badge)} className="ml-auto text-xs">
                          {item.badge}
                        </Badge>
                      )}
                    </Button>
                  </Link>
                )
              })}
              
              {/* Mobile System Status */}
              <div className="flex items-center justify-center space-x-4 py-3 mt-3 border-t">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs font-medium text-green-700 dark:text-green-400">
                    Market Open
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Zap className="w-3 h-3 text-blue-500" />
                  <span className="text-xs font-medium text-blue-700 dark:text-blue-400">
                    AI Active
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
