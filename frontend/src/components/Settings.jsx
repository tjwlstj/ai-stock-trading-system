import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Settings as SettingsIcon, 
  Key, 
  Bot, 
  Shield, 
  Bell,
  Database,
  Cloud,
  Save,
  TestTube,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'

const Settings = () => {
  const [settings, setSettings] = useState({
    // API Settings
    openaiApiKey: '',
    stockApiKey: '',
    
    // AI Agent Settings
    optimisticAgentEnabled: true,
    pessimisticAgentEnabled: true,
    riskManagerEnabled: true,
    analysisFrequency: 'hourly',
    confidenceThreshold: 0.7,
    
    // Risk Management
    maxPositionSize: 10,
    stopLossPercentage: 5,
    takeProfitPercentage: 15,
    
    // Notifications
    emailNotifications: true,
    pushNotifications: false,
    alertThreshold: 5,
    
    // Data Storage
    dataRetentionDays: 90,
    cloudBackupEnabled: true,
    localStorageEnabled: true
  })

  const [testResults, setTestResults] = useState({
    openaiConnection: null,
    stockDataConnection: null,
    cloudStorage: null
  })

  const [isSaving, setIsSaving] = useState(false)
  const [isTesting, setIsTesting] = useState(false)

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const testConnections = async () => {
    setIsTesting(true)
    setTestResults({
      openaiConnection: null,
      stockDataConnection: null,
      cloudStorage: null
    })

    // OpenAI API 테스트
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      setTestResults(prev => ({
        ...prev,
        openaiConnection: settings.openaiApiKey ? 'success' : 'error'
      }))
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        openaiConnection: 'error'
      }))
    }

    // Stock Data API 테스트
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      setTestResults(prev => ({
        ...prev,
        stockDataConnection: 'success'
      }))
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        stockDataConnection: 'error'
      }))
    }

    // Cloud Storage 테스트
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      setTestResults(prev => ({
        ...prev,
        cloudStorage: settings.cloudBackupEnabled ? 'success' : 'warning'
      }))
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        cloudStorage: 'error'
      }))
    }

    setIsTesting(false)
  }

  const saveSettings = async () => {
    setIsSaving(true)
    
    // 설정 저장 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 실제로는 백엔드 API 호출
    // await fetch('/api/settings', { method: 'POST', body: JSON.stringify(settings) })
    
    setIsSaving(false)
  }

  const getTestResultIcon = (result) => {
    switch (result) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default:
        return <div className="h-4 w-4 rounded-full bg-gray-300 animate-pulse" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">
            Configure your AI trading system preferences
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            onClick={testConnections}
            disabled={isTesting}
          >
            <TestTube className={`h-4 w-4 mr-2 ${isTesting ? 'animate-spin' : ''}`} />
            Test Connections
          </Button>
          <Button 
            onClick={saveSettings}
            disabled={isSaving}
          >
            <Save className={`h-4 w-4 mr-2 ${isSaving ? 'animate-spin' : ''}`} />
            Save Settings
          </Button>
        </div>
      </div>

      {/* Settings Tabs */}
      <Tabs defaultValue="api" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="api">API Keys</TabsTrigger>
          <TabsTrigger value="agents">AI Agents</TabsTrigger>
          <TabsTrigger value="risk">Risk Management</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="data">Data & Storage</TabsTrigger>
        </TabsList>

        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Key className="h-5 w-5" />
                <span>API Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure API keys for external services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="openai-key">OpenAI API Key</Label>
                <Input
                  id="openai-key"
                  type="password"
                  placeholder="sk-..."
                  value={settings.openaiApiKey}
                  onChange={(e) => handleSettingChange('openaiApiKey', e.target.value)}
                />
                <p className="text-sm text-muted-foreground">
                  Required for AI agent analysis and recommendations
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="stock-key">Stock Data API Key</Label>
                <Input
                  id="stock-key"
                  type="password"
                  placeholder="Enter your stock data API key"
                  value={settings.stockApiKey}
                  onChange={(e) => handleSettingChange('stockApiKey', e.target.value)}
                />
                <p className="text-sm text-muted-foreground">
                  For real-time stock data (Yahoo Finance, Alpha Vantage, etc.)
                </p>
              </div>

              {/* Connection Test Results */}
              {Object.values(testResults).some(result => result !== null) && (
                <div className="space-y-3 p-4 border rounded-lg bg-muted/50">
                  <h4 className="font-medium">Connection Test Results</h4>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">OpenAI API</span>
                    <div className="flex items-center space-x-2">
                      {getTestResultIcon(testResults.openaiConnection)}
                      <span className="text-sm">
                        {testResults.openaiConnection === 'success' ? 'Connected' : 
                         testResults.openaiConnection === 'error' ? 'Failed' : 'Testing...'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm">Stock Data API</span>
                    <div className="flex items-center space-x-2">
                      {getTestResultIcon(testResults.stockDataConnection)}
                      <span className="text-sm">
                        {testResults.stockDataConnection === 'success' ? 'Connected' : 
                         testResults.stockDataConnection === 'error' ? 'Failed' : 'Testing...'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm">Cloud Storage</span>
                    <div className="flex items-center space-x-2">
                      {getTestResultIcon(testResults.cloudStorage)}
                      <span className="text-sm">
                        {testResults.cloudStorage === 'success' ? 'Connected' : 
                         testResults.cloudStorage === 'warning' ? 'Disabled' :
                         testResults.cloudStorage === 'error' ? 'Failed' : 'Testing...'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bot className="h-5 w-5" />
                <span>AI Agent Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure AI agents and analysis parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Optimistic Analyst</Label>
                    <p className="text-sm text-muted-foreground">
                      Focuses on growth opportunities and positive signals
                    </p>
                  </div>
                  <Switch
                    checked={settings.optimisticAgentEnabled}
                    onCheckedChange={(checked) => handleSettingChange('optimisticAgentEnabled', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Pessimistic Analyst</Label>
                    <p className="text-sm text-muted-foreground">
                      Identifies risks and potential downside scenarios
                    </p>
                  </div>
                  <Switch
                    checked={settings.pessimisticAgentEnabled}
                    onCheckedChange={(checked) => handleSettingChange('pessimisticAgentEnabled', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Risk Manager</Label>
                    <p className="text-sm text-muted-foreground">
                      Provides position sizing and risk assessment
                    </p>
                  </div>
                  <Switch
                    checked={settings.riskManagerEnabled}
                    onCheckedChange={(checked) => handleSettingChange('riskManagerEnabled', checked)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Analysis Frequency</Label>
                  <Select 
                    value={settings.analysisFrequency}
                    onValueChange={(value) => handleSettingChange('analysisFrequency', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="realtime">Real-time</SelectItem>
                      <SelectItem value="15min">Every 15 minutes</SelectItem>
                      <SelectItem value="hourly">Hourly</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Confidence Threshold</Label>
                  <Input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={settings.confidenceThreshold}
                    onChange={(e) => handleSettingChange('confidenceThreshold', parseFloat(e.target.value))}
                  />
                  <p className="text-sm text-muted-foreground">
                    Minimum confidence level for recommendations (0.0 - 1.0)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risk" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Risk Management</span>
              </CardTitle>
              <CardDescription>
                Configure risk parameters and position limits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Max Position Size (%)</Label>
                  <Input
                    type="number"
                    min="1"
                    max="50"
                    value={settings.maxPositionSize}
                    onChange={(e) => handleSettingChange('maxPositionSize', parseInt(e.target.value))}
                  />
                  <p className="text-sm text-muted-foreground">
                    Maximum percentage of portfolio per position
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Stop Loss (%)</Label>
                  <Input
                    type="number"
                    min="1"
                    max="20"
                    value={settings.stopLossPercentage}
                    onChange={(e) => handleSettingChange('stopLossPercentage', parseInt(e.target.value))}
                  />
                  <p className="text-sm text-muted-foreground">
                    Default stop loss percentage
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Take Profit (%)</Label>
                  <Input
                    type="number"
                    min="5"
                    max="100"
                    value={settings.takeProfitPercentage}
                    onChange={(e) => handleSettingChange('takeProfitPercentage', parseInt(e.target.value))}
                  />
                  <p className="text-sm text-muted-foreground">
                    Default take profit percentage
                  </p>
                </div>
              </div>

              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  Risk management settings help protect your portfolio from significant losses. 
                  These are default values that can be overridden per position.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Notification Settings</span>
              </CardTitle>
              <CardDescription>
                Configure alerts and notification preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive analysis updates and alerts via email
                    </p>
                  </div>
                  <Switch
                    checked={settings.emailNotifications}
                    onCheckedChange={(checked) => handleSettingChange('emailNotifications', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Real-time browser notifications for urgent alerts
                    </p>
                  </div>
                  <Switch
                    checked={settings.pushNotifications}
                    onCheckedChange={(checked) => handleSettingChange('pushNotifications', checked)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Alert Threshold (%)</Label>
                <Input
                  type="number"
                  min="1"
                  max="20"
                  value={settings.alertThreshold}
                  onChange={(e) => handleSettingChange('alertThreshold', parseInt(e.target.value))}
                />
                <p className="text-sm text-muted-foreground">
                  Send alerts when position changes exceed this percentage
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5" />
                <span>Data & Storage</span>
              </CardTitle>
              <CardDescription>
                Configure data retention and backup settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Cloud Backup</Label>
                    <p className="text-sm text-muted-foreground">
                      Automatically backup analysis results to cloud storage
                    </p>
                  </div>
                  <Switch
                    checked={settings.cloudBackupEnabled}
                    onCheckedChange={(checked) => handleSettingChange('cloudBackupEnabled', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Local Storage</Label>
                    <p className="text-sm text-muted-foreground">
                      Store data locally for faster access
                    </p>
                  </div>
                  <Switch
                    checked={settings.localStorageEnabled}
                    onCheckedChange={(checked) => handleSettingChange('localStorageEnabled', checked)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Data Retention (Days)</Label>
                <Input
                  type="number"
                  min="7"
                  max="365"
                  value={settings.dataRetentionDays}
                  onChange={(e) => handleSettingChange('dataRetentionDays', parseInt(e.target.value))}
                />
                <p className="text-sm text-muted-foreground">
                  How long to keep historical analysis data
                </p>
              </div>

              <Alert>
                <Cloud className="h-4 w-4" />
                <AlertDescription>
                  Cloud backup ensures your analysis history is preserved even if local data is lost. 
                  Local storage improves performance but requires sufficient disk space.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Settings
