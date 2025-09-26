import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { 
  DollarSign, 
  Zap, 
  Target, 
  TrendingDown, 
  Settings,
  PieChart,
  Clock,
  Database
} from 'lucide-react';
import { PieChart as RechartsPieChart, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const CostOptimizer = () => {
  const [strategy, setStrategy] = useState('balanced');
  const [cachingEnabled, setCachingEnabled] = useState(true);
  const [dailyBudget, setDailyBudget] = useState(10.0);
  const [metrics, setMetrics] = useState({
    totalRequests: 156,
    cacheHitRate: 0.35,
    totalCost: 2.47,
    costSaved: 1.23,
    savingsRate: 0.33,
    averageResponseTime: 2.8,
    budgetUsage: 24.7
  });

  const [modelUsage, setModelUsage] = useState([
    { name: 'GPT-4.1 Mini', value: 89, cost: 1.85, color: '#3b82f6' },
    { name: 'GPT-4.1 Nano', value: 67, cost: 0.62, color: '#10b981' }
  ]);

  const [costTrend, setCostTrend] = useState([
    { time: '00:00', cost: 0.12, requests: 8 },
    { time: '04:00', cost: 0.08, requests: 5 },
    { time: '08:00', cost: 0.35, requests: 23 },
    { time: '12:00', cost: 0.52, requests: 34 },
    { time: '16:00', cost: 0.78, requests: 51 },
    { time: '20:00', cost: 0.62, requests: 35 }
  ]);

  // 실시간 메트릭 업데이트 시뮬레이션
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalRequests: prev.totalRequests + Math.floor(Math.random() * 3),
        cacheHitRate: Math.min(0.95, prev.cacheHitRate + (Math.random() - 0.5) * 0.02),
        totalCost: prev.totalCost + Math.random() * 0.01,
        averageResponseTime: Math.max(0.5, prev.averageResponseTime + (Math.random() - 0.5) * 0.1)
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const strategyDescriptions = {
    cost_first: '비용을 최우선으로 고려하여 가장 저렴한 모델을 선택합니다.',
    balanced: '비용과 성능의 균형을 맞춰 최적의 모델을 선택합니다.',
    performance_first: '성능을 최우선으로 고려하여 가장 강력한 모델을 선택합니다.',
    adaptive: '실시간 상황에 따라 동적으로 최적 모델을 선택합니다.'
  };

  const getBudgetStatus = () => {
    const usage = metrics.budgetUsage;
    if (usage < 50) return { color: 'text-green-600', status: '안전' };
    if (usage < 80) return { color: 'text-yellow-600', status: '주의' };
    return { color: 'text-red-600', status: '위험' };
  };

  const budgetStatus = getBudgetStatus();

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            AI 비용 최적화 시스템
          </CardTitle>
          <CardDescription>
            모델 캐스케이딩과 캐싱을 통한 지능형 비용 관리
          </CardDescription>
        </CardHeader>
      </Card>

      {/* 설정 패널 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            최적화 설정
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* 최적화 전략 */}
            <div className="space-y-2">
              <Label htmlFor="strategy">최적화 전략</Label>
              <Select value={strategy} onValueChange={setStrategy}>
                <SelectTrigger>
                  <SelectValue placeholder="전략 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cost_first">비용 우선</SelectItem>
                  <SelectItem value="balanced">균형</SelectItem>
                  <SelectItem value="performance_first">성능 우선</SelectItem>
                  <SelectItem value="adaptive">적응형</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                {strategyDescriptions[strategy]}
              </p>
            </div>

            {/* 캐싱 설정 */}
            <div className="space-y-2">
              <Label htmlFor="caching">캐싱 시스템</Label>
              <div className="flex items-center space-x-2">
                <Switch
                  id="caching"
                  checked={cachingEnabled}
                  onCheckedChange={setCachingEnabled}
                />
                <Label htmlFor="caching">
                  {cachingEnabled ? '활성화' : '비활성화'}
                </Label>
              </div>
              <p className="text-sm text-muted-foreground">
                동일한 요청에 대한 응답을 캐시하여 비용을 절약합니다.
              </p>
            </div>

            {/* 일일 예산 */}
            <div className="space-y-2">
              <Label htmlFor="budget">일일 예산 (USD)</Label>
              <div className="flex items-center space-x-2">
                <DollarSign className="h-4 w-4 text-muted-foreground" />
                <span className="text-lg font-semibold">{dailyBudget.toFixed(2)}</span>
              </div>
              <Progress value={metrics.budgetUsage} className="w-full" />
              <p className={`text-sm ${budgetStatus.color}`}>
                {metrics.budgetUsage.toFixed(1)}% 사용 - {budgetStatus.status}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 메트릭 대시보드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">총 요청</p>
                <p className="text-2xl font-bold">{metrics.totalRequests}</p>
              </div>
              <Zap className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">캐시 히트율</p>
                <p className="text-2xl font-bold">{(metrics.cacheHitRate * 100).toFixed(1)}%</p>
              </div>
              <Database className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">총 비용</p>
                <p className="text-2xl font-bold">${metrics.totalCost.toFixed(3)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">절약률</p>
                <p className="text-2xl font-bold">{(metrics.savingsRate * 100).toFixed(1)}%</p>
              </div>
              <TrendingDown className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 차트 섹션 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 모델 사용량 파이 차트 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5" />
              모델 사용량 분포
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={modelUsage}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {modelUsage.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value, name, props) => [
                      `${value} 요청 ($${props.payload.cost})`,
                      props.payload.name
                    ]}
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-4">
              {modelUsage.map((model, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: model.color }}
                  />
                  <span className="text-sm">{model.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 비용 추이 바 차트 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              시간별 비용 추이
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={costTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'cost' ? `$${value}` : `${value} 요청`,
                      name === 'cost' ? '비용' : '요청 수'
                    ]}
                  />
                  <Bar dataKey="cost" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 최적화 권장사항 */}
      <Card>
        <CardHeader>
          <CardTitle>최적화 권장사항</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
              <div>
                <p className="font-medium text-blue-900">캐시 효율성 개선</p>
                <p className="text-sm text-blue-700">
                  현재 캐시 히트율이 {(metrics.cacheHitRate * 100).toFixed(1)}%입니다. 
                  유사한 요청 패턴을 분석하여 캐시 TTL을 조정하면 더 많은 비용을 절약할 수 있습니다.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
              <div>
                <p className="font-medium text-green-900">모델 선택 최적화</p>
                <p className="text-sm text-green-700">
                  현재 전략({strategy})이 잘 작동하고 있습니다. 
                  {metrics.savingsRate > 0.3 ? '높은 절약률을 달성했습니다.' : '더 공격적인 비용 절약을 위해 "비용 우선" 전략을 고려해보세요.'}
                </p>
              </div>
            </div>

            {metrics.budgetUsage > 80 && (
              <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
                <div className="w-2 h-2 bg-red-500 rounded-full mt-2" />
                <div>
                  <p className="font-medium text-red-900">예산 경고</p>
                  <p className="text-sm text-red-700">
                    일일 예산의 {metrics.budgetUsage.toFixed(1)}%를 사용했습니다. 
                    비용 우선 전략으로 변경하거나 캐싱을 활성화하여 비용을 절약하세요.
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CostOptimizer;
