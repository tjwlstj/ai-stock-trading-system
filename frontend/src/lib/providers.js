// API provider catalog rendered by the Settings page.
// Pure presentational content: which company provides each API, how to issue a
// key, hover tooltips, and links. Actual secret values are handled by the backend.

export const RUN_MODES = [
  { value: 'paper', label: 'PaperBroker (시뮬레이션)', hint: '실제 주문 없이 로컬 모의 체결. 기본값 — 가장 안전.' },
  { value: 'kis', label: '한국투자 KIS 모의투자', hint: '무료 모의계좌로 실제 API 흐름 검증.' },
  { value: 'toss', label: '토스증권 (실거래)', hint: '실제 주문이 나갈 수 있음. 아래 실거래 허용 + 키 필요.' },
]

export const PROVIDERS = [
  {
    id: 'openai',
    name: 'OpenAI',
    company: 'OpenAI',
    category: 'AI 분석 (LLM)',
    badge: '필수',
    badgeTone: 'default',
    summary: 'AI 에이전트 분석에 사용하는 언어모델. 분석 기능을 쓰려면 필요합니다.',
    fields: [
      {
        key: 'OPENAI_API_KEY',
        label: 'API Key',
        type: 'password',
        placeholder: 'sk-...',
        required: true,
        tooltip:
          'platform.openai.com에서 발급한 비밀 키. "sk-"로 시작합니다. 한 번만 표시되니 복사해 두세요. 절대 공유/커밋 금지.',
      },
    ],
    howTo: [
      'platform.openai.com 로그인 → 우상단 프로필 → "API keys"',
      '"Create new secret key" 클릭 → 생성된 키 복사 (다시 못 봄)',
      'Billing에서 결제수단 등록 또는 크레딧 충전 (사용량 과금)',
      '아래에 붙여넣고 저장 → "테스트"로 연결 확인',
    ],
    issueUrl: 'https://platform.openai.com/api-keys',
    docUrl: 'https://platform.openai.com/docs/quickstart',
    testable: true,
  },
  {
    id: 'kis',
    name: '한국투자증권 KIS Developers',
    company: '한국투자증권',
    category: '국내·해외 주식 시세/주문 · 모의투자',
    badge: '개발 권장',
    badgeTone: 'success',
    summary:
      '무료 모의투자 + 성숙한 문서/라이브러리. 개발과 검증 단계에 가장 권장하는 브로커입니다.',
    fields: [
      { key: 'KIS_APP_KEY', label: 'App Key', type: 'password', placeholder: 'PS...', required: true,
        tooltip: 'KIS Developers 포털에서 앱 등록 시 발급되는 App Key.' },
      { key: 'KIS_APP_SECRET', label: 'App Secret', type: 'password', placeholder: '••••••', required: true,
        tooltip: '앱 등록 시 함께 발급되는 비밀값. access_token 발급에 사용됩니다.' },
      { key: 'KIS_ACCOUNT_NO', label: '계좌번호 (8-2)', type: 'text', placeholder: '50000000-01', required: false,
        tooltip: '주문/잔고 조회에 쓰는 계좌번호. 모의투자 계좌도 동일 형식입니다.' },
    ],
    howTo: [
      'KIS Developers(apiportal.koreainvestment.com) 로그인 → "KIS Developers 신청"',
      '국내주식 등 사용할 서비스 신청 → App Key / App Secret 발급',
      '모의투자 계좌 개설(무료) 후 .env의 KIS_PAPER=true 유지 권장',
      '아래에 키 입력 후 저장',
    ],
    issueUrl: 'https://apiportal.koreainvestment.com/',
    docUrl: 'https://apiportal.koreainvestment.com/apiservice',
    testable: true,
  },
  {
    id: 'toss',
    name: '토스증권 Open API',
    company: '토스증권',
    category: '국내·미국 주식 시세/주문 (실거래)',
    badge: '실거래 타깃',
    badgeTone: 'warning',
    summary:
      'OAuth2 기반 REST API로 시세·잔고·주문 지원. 실거래 연결 대상입니다.',
    warning:
      '공개 모의투자(샌드박스)가 없습니다. 개발·검증은 PaperBroker나 KIS 모의투자로 하고, 토스는 실거래 단계에서만 연결하세요.',
    fields: [
      { key: 'TOSS_CLIENT_ID', label: 'Client ID', type: 'text', placeholder: 'client id', required: true,
        tooltip: '토스증권 PC 웹 > Open API에서 발급한 Client ID. OAuth2 토큰 발급에 사용.' },
      { key: 'TOSS_CLIENT_SECRET', label: 'Client Secret', type: 'password', placeholder: '••••••', required: true,
        tooltip: 'Client ID와 짝을 이루는 비밀값. Basic 인증으로 access_token을 발급합니다.' },
      { key: 'TOSS_ACCOUNT_NO', label: '계좌번호', type: 'text', placeholder: '계좌번호', required: false,
        tooltip: '계좌 관련 호출 시 X-Tossinvest-Account 헤더로 사용됩니다.' },
    ],
    howTo: [
      '토스증권 계좌 보유 상태에서 PC 웹 > Open API 사전신청',
      '승인 후 PC 웹에서 Client ID / Client Secret 발급',
      'developers.tossinvest.com에서 OpenAPI 스펙 확인 (엔드포인트는 공식 문서 기준 검증 필요)',
      '아래에 키 입력 후 저장',
    ],
    issueUrl: 'https://corp.tossinvest.com/ko/open-api',
    docUrl: 'https://developers.tossinvest.com',
    testable: true,
  },
]

// Info-only alternatives (no key fields here yet) — links for further reading.
export const ALTERNATIVES = [
  { name: '키움증권 REST API', company: '키움증권', note: '2025 REST 개편, 무료 모의투자. 현재 국내주식 위주.', url: 'https://openapi.kiwoom.com/' },
  { name: 'FinanceDataReader / pykrx', company: '오픈소스', note: 'KRX 과거 시세·유니버스·지수 데이터 (백테스트용).', url: 'https://github.com/sharebook-kr/pykrx' },
]

// Deep-dive docs kept out of the UI to avoid clutter.
export const ADVANCED_LINKS = [
  { label: '국내(KRX) 아키텍처 설계 문서', href: 'https://github.com/tjwlstj/ai-stock-trading-system/blob/main/docs/ARCHITECTURE_KRX.md' },
  { label: '보안 가이드', href: 'https://github.com/tjwlstj/ai-stock-trading-system/blob/main/docs/SECURITY_GUIDE.md' },
]
