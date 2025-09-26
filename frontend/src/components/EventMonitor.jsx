import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Volume2, 
  Newspaper, 
  AlertTriangle,
  Play,
  Pause,
  RefreshCw
} from 'lucide-react';

const EventMonitor = () => {
  const [events, setEvents] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [metrics, setMetrics] = useState({
    eventsProcessed: 0,
    successRate: 100,
    avgProcessingTime: 0,
    queueSize: 0
  });

  // 이벤트 타입별 아이콘 매핑
  const getEventIcon = (eventType) => {
    const iconMap = {
      'price_change': TrendingUp,
      'volume_spike': Volume2,
      'news_alert': Newspaper,
      'risk_alert': AlertTriangle,
      'ai_analysis_complete': Activity,
      'trade_signal': TrendingDown
    };
    return iconMap[eventType] || Activity;
  };

  // 이벤트 우선순위별 색상
  const getPriorityColor = (priority) => {
    const colorMap = {
      'critical': 'destructive',
      'high': 'destructive',
      'medium': 'default',
      'low': 'secondary'
    };
    return colorMap[priority] || 'default';
  };

  // 실시간 이벤트 시뮬레이션
  useEffect(() => {
    let interval;
    
    if (isStreaming) {
      interval = setInterval(() => {
        const eventTypes = ['price_change', 'volume_spike', 'news_alert', 'ai_analysis_complete', 'trade_signal'];
        const symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'];
        const priorities = ['low', 'medium', 'high', 'critical'];
        
        const newEvent = {
          id: Date.now() + Math.random(),
          eventType: eventTypes[Math.floor(Math.random() * eventTypes.length)],
          symbol: symbols[Math.floor(Math.random() * symbols.length)],
          timestamp: new Date().toISOString(),
          priority: priorities[Math.floor(Math.random() * priorities.length)],
          data: generateEventData(),
          processed: Math.random() > 0.1 // 90% 성공률
        };

        setEvents(prev => [newEvent, ...prev.slice(0, 49)]); // 최근 50개만 유지
        
        // 메트릭 업데이트
        setMetrics(prev => ({
          eventsProcessed: prev.eventsProcessed + 1,
          successRate: Math.round((prev.eventsProcessed * prev.successRate + (newEvent.processed ? 100 : 0)) / (prev.eventsProcessed + 1)),
          avgProcessingTime: Math.round((Math.random() * 2 + 0.5) * 1000) / 1000,
          queueSize: Math.floor(Math.random() * 10)
        }));
      }, 2000 + Math.random() * 3000); // 2-5초 간격
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isStreaming]);

  const generateEventData = () => {
    return {
      changePercent: (Math.random() - 0.5) * 10,
      volume: Math.floor(Math.random() * 100000000),
      price: Math.round((Math.random() * 200 + 50) * 100) / 100,
      confidence: Math.round(Math.random() * 100),
      recommendation: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)]
    };
  };

  const formatEventData = (event) => {
    const { data } = event;
    switch (event.eventType) {
      case 'price_change':
        return `${data.changePercent > 0 ? '+' : ''}${data.changePercent?.toFixed(2)}% → $${data.price}`;
      case 'volume_spike':
        return `Volume: ${(data.volume / 1000000).toFixed(1)}M`;
      case 'ai_analysis_complete':
        return `${data.recommendation} (${data.confidence}% confidence)`;
      case 'trade_signal':
        return `Signal: ${data.recommendation}`;
      default:
        return 'Event processed';
    }
  };

  const clearEvents = () => {
    setEvents([]);
    setMetrics({
      eventsProcessed: 0,
      successRate: 100,
      avgProcessingTime: 0,
      queueSize: 0
    });
  };

  return (
    <div className="space-y-6">
      {/* 컨트롤 패널 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                실시간 이벤트 모니터
              </CardTitle>
              <CardDescription>
                시장 이벤트와 AI 분석 결과를 실시간으로 모니터링합니다
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant={isStreaming ? "destructive" : "default"}
                size="sm"
                onClick={() => setIsStreaming(!isStreaming)}
              >
                {isStreaming ? (
                  <>
                    <Pause className="h-4 w-4 mr-2" />
                    중지
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    시작
                  </>
                )}
              </Button>
              <Button variant="outline" size="sm" onClick={clearEvents}>
                <RefreshCw className="h-4 w-4 mr-2" />
                초기화
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* 메트릭 대시보드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-blue-600">{metrics.eventsProcessed}</div>
            <p className="text-sm text-muted-foreground">처리된 이벤트</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">{metrics.successRate}%</div>
            <p className="text-sm text-muted-foreground">성공률</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-purple-600">{metrics.avgProcessingTime}s</div>
            <p className="text-sm text-muted-foreground">평균 처리시간</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-orange-600">{metrics.queueSize}</div>
            <p className="text-sm text-muted-foreground">대기열 크기</p>
          </CardContent>
        </Card>
      </div>

      {/* 이벤트 스트림 */}
      <Card>
        <CardHeader>
          <CardTitle>이벤트 스트림</CardTitle>
          <CardDescription>
            최근 이벤트 {events.length}개 표시 중
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96">
            <div className="space-y-3">
              {events.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  이벤트 스트리밍을 시작하여 실시간 데이터를 확인하세요
                </div>
              ) : (
                events.map((event) => {
                  const IconComponent = getEventIcon(event.eventType);
                  return (
                    <div
                      key={event.id}
                      className={`flex items-center gap-3 p-3 rounded-lg border ${
                        event.processed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <div className={`p-2 rounded-full ${
                        event.processed ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        <IconComponent className={`h-4 w-4 ${
                          event.processed ? 'text-green-600' : 'text-red-600'
                        }`} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-sm">{event.symbol}</span>
                          <Badge variant={getPriorityColor(event.priority)} className="text-xs">
                            {event.priority.toUpperCase()}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {event.eventType.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {formatEventData(event)}
                        </div>
                      </div>
                      
                      <div className="text-xs text-muted-foreground">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default EventMonitor;
