import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import {
  Key, Bot, Shield, Bell, Database, Cloud, Save,
  CheckCircle, AlertTriangle, Info, ExternalLink, Loader2, RefreshCw,
} from 'lucide-react'
import { api } from '@/lib/api'
import { PROVIDERS, RUN_MODES, ALTERNATIVES, ADVANCED_LINKS } from '@/lib/providers'

// Hover tooltip with an (i) trigger — used next to every key field.
const InfoTip = ({ text }) => (
  <Tooltip>
    <TooltipTrigger asChild>
      <button type="button" aria-label="도움말" className="inline-flex items-center text-muted-foreground hover:text-foreground">
        <Info className="h-3.5 w-3.5" />
      </button>
    </TooltipTrigger>
    <TooltipContent className="max-w-xs text-sm leading-relaxed">{text}</TooltipContent>
  </Tooltip>
)

const badgeVariant = (tone) =>
  tone === 'warning' ? 'destructive' : tone === 'success' ? 'secondary' : 'default'

const Settings = () => {
  // ---- API keys / secrets (wired to backend) ----
  const [status, setStatus] = useState({ secrets: {}, config: {} })
  const [drafts, setDrafts] = useState({})            // field key -> typed value
  const [providerState, setProviderState] = useState({}) // provider id -> {saving, testing, ok, msg}
  const [loadErr, setLoadErr] = useState(null)

  const loadStatus = async () => {
    try {
      const s = await api.getSecrets()
      setStatus({ secrets: s.secrets || {}, config: s.config || {} })
      setLoadErr(null)
    } catch (e) {
      setLoadErr(e.message)
    }
  }
  useEffect(() => { loadStatus() }, [])

  const setDraft = (key, val) => setDrafts((d) => ({ ...d, [key]: val }))
  const patchProvider = (id, patch) =>
    setProviderState((p) => ({ ...p, [id]: { ...p[id], ...patch } }))

  const saveProvider = async (provider) => {
    const updates = {}
    for (const f of provider.fields) {
      const v = drafts[f.key]
      if (v !== undefined && v !== '') updates[f.key] = v
    }
    if (Object.keys(updates).length === 0) {
      patchProvider(provider.id, { ok: false, msg: '변경할 값을 입력하세요.' })
      return
    }
    patchProvider(provider.id, { saving: true, msg: null })
    try {
      const res = await api.saveSecrets(updates)
      setStatus({ secrets: res.secrets, config: res.config })
      setDrafts((d) => {
        const nd = { ...d }
        Object.keys(updates).forEach((k) => delete nd[k])
        return nd
      })
      patchProvider(provider.id, { saving: false, ok: true, msg: '저장되었습니다.' })
    } catch (e) {
      patchProvider(provider.id, { saving: false, ok: false, msg: `저장 실패: ${e.message}` })
    }
  }

  const testProvider = async (provider) => {
    patchProvider(provider.id, { testing: true, msg: null })
    try {
      const res = await api.testProvider(provider.id)
      patchProvider(provider.id, { testing: false, ok: res.ok, msg: res.message })
    } catch (e) {
      patchProvider(provider.id, { testing: false, ok: false, msg: `테스트 실패: ${e.message}` })
    }
  }

  const saveConfig = async (updates) => {
    try {
      const res = await api.saveSecrets(updates)
      setStatus({ secrets: res.secrets, config: res.config })
    } catch (e) {
      setLoadErr(e.message)
    }
  }

  const broker = status.config.BROKER || 'paper'
  const liveOn = String(status.config.ALLOW_LIVE_TRADING).toLowerCase() === 'true'

  // ---- Other tabs (local-only preferences) ----
  const [settings, setSettings] = useState({
    optimisticAgentEnabled: true,
    pessimisticAgentEnabled: true,
    riskManagerEnabled: true,
    analysisFrequency: 'hourly',
    confidenceThreshold: 0.7,
    maxPositionSize: 10,
    stopLossPercentage: 5,
    takeProfitPercentage: 15,
    emailNotifications: true,
    pushNotifications: false,
    alertThreshold: 5,
    dataRetentionDays: 90,
    cloudBackupEnabled: true,
    localStorageEnabled: true,
  })
  const handleSettingChange = (key, value) => setSettings((prev) => ({ ...prev, [key]: value }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">설정 (Settings)</h1>
          <p className="text-muted-foreground">API 키·토큰을 직접 입력하고 실행 모드를 설정하세요.</p>
        </div>
        <Button variant="outline" onClick={loadStatus}>
          <RefreshCw className="h-4 w-4 mr-2" /> 상태 새로고침
        </Button>
      </div>

      <Tabs defaultValue="api" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="api">API & 키</TabsTrigger>
          <TabsTrigger value="agents">AI Agents</TabsTrigger>
          <TabsTrigger value="risk">Risk</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
        </TabsList>

        {/* ===================== API & KEYS ===================== */}
        <TabsContent value="api" className="space-y-4">
          {loadErr && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>백엔드 연결 실패: {loadErr} — 백엔드가 실행 중인지 확인하세요.</AlertDescription>
            </Alert>
          )}

          {/* Run mode */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Shield className="h-5 w-5" /> 실행 모드</CardTitle>
              <CardDescription>주문이 어디로 나갈지 결정합니다. 기본값은 안전한 시뮬레이션입니다.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2 max-w-sm">
                <div className="flex items-center gap-1.5">
                  <Label>브로커</Label>
                  <InfoTip text="paper=로컬 시뮬, kis=한국투자 모의투자, toss=토스 실거래" />
                </div>
                <Select value={broker} onValueChange={(v) => saveConfig({ BROKER: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {RUN_MODES.map((m) => <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>)}
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  {RUN_MODES.find((m) => m.value === broker)?.hint}
                </p>
              </div>

              <div className="flex items-center justify-between rounded-lg border p-3">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-1.5">
                    <Label>실거래 허용</Label>
                    <InfoTip text="이 스위치가 켜지고 브로커가 toss일 때에만 실제 주문이 실행됩니다." />
                  </div>
                  <p className="text-sm text-muted-foreground">끄면 토스를 선택해도 실주문이 차단됩니다(안전장치).</p>
                </div>
                <Switch checked={liveOn} onCheckedChange={(c) => saveConfig({ ALLOW_LIVE_TRADING: c ? 'true' : 'false' })} />
              </div>
              {liveOn && broker === 'toss' && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>실거래가 활성화되어 있습니다. 실제 자금으로 주문이 나갈 수 있습니다.</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Provider cards */}
          {PROVIDERS.map((p) => {
            const st = providerState[p.id] || {}
            return (
              <Card key={p.id}>
                <CardHeader>
                  <div className="flex items-center justify-between gap-2">
                    <CardTitle className="flex items-center gap-2"><Key className="h-5 w-5" /> {p.name}</CardTitle>
                    <Badge variant={badgeVariant(p.badgeTone)}>{p.badge}</Badge>
                  </div>
                  <CardDescription>{p.company} · {p.category}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">{p.summary}</p>
                  {p.warning && (
                    <Alert variant="destructive">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>{p.warning}</AlertDescription>
                    </Alert>
                  )}

                  {p.fields.map((f) => {
                    const cur = status.secrets[f.key]
                    return (
                      <div key={f.key} className="space-y-1.5">
                        <div className="flex items-center gap-1.5">
                          <Label htmlFor={f.key}>
                            {f.label}{f.required && <span className="text-destructive"> *</span>}
                          </Label>
                          <InfoTip text={f.tooltip} />
                          {cur?.set && (
                            <span className="ml-auto text-xs text-green-600 dark:text-green-400">설정됨 · {cur.preview}</span>
                          )}
                        </div>
                        <Input
                          id={f.key}
                          type={f.type}
                          autoComplete="off"
                          placeholder={cur?.set ? '재입력 시에만 변경됩니다' : f.placeholder}
                          value={drafts[f.key] ?? ''}
                          onChange={(e) => setDraft(f.key, e.target.value)}
                        />
                      </div>
                    )
                  })}

                  <details className="text-sm">
                    <summary className="cursor-pointer text-muted-foreground hover:text-foreground">발급 방법 보기</summary>
                    <ol className="mt-2 list-decimal space-y-1 pl-5 text-muted-foreground">
                      {p.howTo.map((step, i) => <li key={i}>{step}</li>)}
                    </ol>
                  </details>

                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <Button onClick={() => saveProvider(p)} disabled={st.saving}>
                      {st.saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                      저장
                    </Button>
                    {p.testable && (
                      <Button variant="outline" onClick={() => testProvider(p)} disabled={st.testing}>
                        {st.testing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <CheckCircle className="mr-2 h-4 w-4" />}
                        테스트
                      </Button>
                    )}
                    <Button variant="ghost" asChild>
                      <a href={p.issueUrl} target="_blank" rel="noreferrer">
                        발급 페이지 <ExternalLink className="ml-1.5 h-3.5 w-3.5" />
                      </a>
                    </Button>
                    <a href={p.docUrl} target="_blank" rel="noreferrer" className="text-sm text-muted-foreground underline-offset-4 hover:underline">
                      심화 가이드
                    </a>
                  </div>

                  {st.msg && (
                    <p className={`text-sm ${st.ok === false ? 'text-destructive' : st.ok === true ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`}>
                      {st.msg}
                    </p>
                  )}
                </CardContent>
              </Card>
            )
          })}

          {/* Alternatives + advanced links */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Info className="h-5 w-5" /> 기타 대안 & 심화 자료</CardTitle>
              <CardDescription>다른 증권사/데이터 소스와 자세한 설계 문서</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {ALTERNATIVES.map((a) => (
                <div key={a.name} className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium">{a.name} <span className="text-muted-foreground">· {a.company}</span></p>
                    <p className="text-sm text-muted-foreground">{a.note}</p>
                  </div>
                  <a href={a.url} target="_blank" rel="noreferrer" className="shrink-0 text-sm text-primary underline-offset-4 hover:underline">열기</a>
                </div>
              ))}
              <div className="border-t pt-3 flex flex-wrap gap-x-4 gap-y-1">
                {ADVANCED_LINKS.map((l) => (
                  <a key={l.href} href={l.href} target="_blank" rel="noreferrer" className="inline-flex items-center text-sm text-primary underline-offset-4 hover:underline">
                    {l.label} <ExternalLink className="ml-1 h-3 w-3" />
                  </a>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ===================== AI AGENTS ===================== */}
        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2"><Bot className="h-5 w-5" /><span>AI Agent Configuration</span></CardTitle>
              <CardDescription>Configure AI agents and analysis parameters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Optimistic Analyst</Label>
                    <p className="text-sm text-muted-foreground">Focuses on growth opportunities and positive signals</p>
                  </div>
                  <Switch checked={settings.optimisticAgentEnabled} onCheckedChange={(c) => handleSettingChange('optimisticAgentEnabled', c)} />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Pessimistic Analyst</Label>
                    <p className="text-sm text-muted-foreground">Identifies risks and potential downside scenarios</p>
                  </div>
                  <Switch checked={settings.pessimisticAgentEnabled} onCheckedChange={(c) => handleSettingChange('pessimisticAgentEnabled', c)} />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Risk Manager</Label>
                    <p className="text-sm text-muted-foreground">Provides position sizing and risk assessment</p>
                  </div>
                  <Switch checked={settings.riskManagerEnabled} onCheckedChange={(c) => handleSettingChange('riskManagerEnabled', c)} />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Analysis Frequency</Label>
                  <Select value={settings.analysisFrequency} onValueChange={(v) => handleSettingChange('analysisFrequency', v)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
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
                  <Input type="number" min="0" max="1" step="0.1" value={settings.confidenceThreshold}
                    onChange={(e) => handleSettingChange('confidenceThreshold', parseFloat(e.target.value))} />
                  <p className="text-sm text-muted-foreground">Minimum confidence level for recommendations (0.0 - 1.0)</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ===================== RISK ===================== */}
        <TabsContent value="risk" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2"><Shield className="h-5 w-5" /><span>Risk Management</span></CardTitle>
              <CardDescription>Configure risk parameters and position limits</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Max Position Size (%)</Label>
                  <Input type="number" min="1" max="50" value={settings.maxPositionSize}
                    onChange={(e) => handleSettingChange('maxPositionSize', parseInt(e.target.value))} />
                  <p className="text-sm text-muted-foreground">Maximum percentage of portfolio per position</p>
                </div>
                <div className="space-y-2">
                  <Label>Stop Loss (%)</Label>
                  <Input type="number" min="1" max="20" value={settings.stopLossPercentage}
                    onChange={(e) => handleSettingChange('stopLossPercentage', parseInt(e.target.value))} />
                  <p className="text-sm text-muted-foreground">Default stop loss percentage</p>
                </div>
                <div className="space-y-2">
                  <Label>Take Profit (%)</Label>
                  <Input type="number" min="5" max="100" value={settings.takeProfitPercentage}
                    onChange={(e) => handleSettingChange('takeProfitPercentage', parseInt(e.target.value))} />
                  <p className="text-sm text-muted-foreground">Default take profit percentage</p>
                </div>
              </div>
              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  Risk management settings help protect your portfolio. These are defaults that can be overridden per position.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ===================== NOTIFICATIONS ===================== */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2"><Bell className="h-5 w-5" /><span>Notification Settings</span></CardTitle>
              <CardDescription>Configure alerts and notification preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive analysis updates and alerts via email</p>
                  </div>
                  <Switch checked={settings.emailNotifications} onCheckedChange={(c) => handleSettingChange('emailNotifications', c)} />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">Real-time browser notifications for urgent alerts</p>
                  </div>
                  <Switch checked={settings.pushNotifications} onCheckedChange={(c) => handleSettingChange('pushNotifications', c)} />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Alert Threshold (%)</Label>
                <Input type="number" min="1" max="20" value={settings.alertThreshold}
                  onChange={(e) => handleSettingChange('alertThreshold', parseInt(e.target.value))} />
                <p className="text-sm text-muted-foreground">Send alerts when position changes exceed this percentage</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ===================== DATA ===================== */}
        <TabsContent value="data" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2"><Database className="h-5 w-5" /><span>Data & Storage</span></CardTitle>
              <CardDescription>Configure data retention and backup settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Cloud Backup</Label>
                    <p className="text-sm text-muted-foreground">Automatically backup analysis results to cloud storage</p>
                  </div>
                  <Switch checked={settings.cloudBackupEnabled} onCheckedChange={(c) => handleSettingChange('cloudBackupEnabled', c)} />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Local Storage</Label>
                    <p className="text-sm text-muted-foreground">Store data locally for faster access</p>
                  </div>
                  <Switch checked={settings.localStorageEnabled} onCheckedChange={(c) => handleSettingChange('localStorageEnabled', c)} />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Data Retention (Days)</Label>
                <Input type="number" min="7" max="365" value={settings.dataRetentionDays}
                  onChange={(e) => handleSettingChange('dataRetentionDays', parseInt(e.target.value))} />
                <p className="text-sm text-muted-foreground">How long to keep historical analysis data</p>
              </div>
              <Alert>
                <Cloud className="h-4 w-4" />
                <AlertDescription>Cloud backup preserves your analysis history. Local storage improves performance.</AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Settings
