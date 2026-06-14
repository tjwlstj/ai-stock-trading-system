# 국내(KRX) 실거래 지향 아키텍처 설계

> **상태**: 설계 문서 (2026-06-14 작성). 코드는 아직 이 설계를 따라가는 중이며, 본 문서는 "목표 구조"를 정의합니다.
> **안전 원칙**: 이 시스템은 실제 돈을 다룰 수 있습니다. **LLM은 절대 직접 주문하지 않으며**, 기본 동작은 모의/시뮬레이션입니다.

---

## 1. 방향 재정의

기존 레포는 **미국주식 분석 데모**(Yahoo Finance + OpenAI 단일 호출, 주문 실행 없음)였습니다.
새 목표는 **국내 KRX 시장 기준의, 실거래까지 연결 가능한 AI 보조 트레이딩 시스템**입니다.

| 구분 | 기존 (AS-IS) | 목표 (TO-BE) |
|------|-------------|-------------|
| 시장 | 미국 (US, USD) | 국내 KRX (KOSPI/KOSDAQ, KRW) |
| 시세 | Yahoo Finance (15~20분 지연) | 브로커 실시간 API + FDR/pykrx 과거데이터 |
| 심볼 | `AAPL` | 6자리 코드 `005930` (삼성전자) |
| 주문 | 없음 (분석만) | 브로커 어댑터 (모의 → 실주문, 수동 게이트) |
| 에이전트 | API에 미연결 + 가짜값 | 실제 멀티에이전트 분석 연결 |
| 스택 | pip/venv, black 가정 | uv + ruff + pydantic v2 + FastAPI |

---

## 2. 증권사 거래 API 비교 (2026 조사)

국내에서 REST 기반으로 **주문 실행 + 모의투자**가 가능한 3개 후보:

| 항목 | 토스증권 Open API | 한국투자 KIS | 키움 REST API |
|------|------------------|--------------|---------------|
| 출시/성숙도 | 신규(2026), 사전신청 | 성숙, 대형 커뮤니티 | 2025 REST 개편 |
| 인증 | OAuth2 Client Credentials | appkey/secret → access_token | appkey/secret → token |
| **모의투자(샌드박스)** | ❌ **미공개** (실계좌 소액 권장) | ✅ 무료 모의투자 | ✅ 무료 모의투자 |
| 국내주식 주문 | ✅ | ✅ | ✅ (국내 ETF/ETN 포함) |
| 해외주식 | ✅ (US) | ✅ | ❌ (현재 국내만) |
| 실시간 | REST 폴링 (WebSocket 미공개) | REST + WebSocket | REST + WebSocket(19종) |
| 파이썬 라이브러리 | (OpenAPI 스펙 → SDK 생성) | `python-kis` 등 풍부 | `kiwoom-rest-api` 래퍼 |
| 수수료 | 국내 ~2026.6 면제 | 일반 수수료 | 일반 수수료 |

### 핵심 판단
- **토스는 사용자의 목표 브로커**지만 **공개 모의투자가 없어** 개발/테스트 단계에서 실계좌 위험이 큼.
- **KIS는 무료 모의투자 + 성숙한 라이브러리**라 개발·검증에 가장 안전.
- → **결론: 브로커를 추상화**하고, **개발은 PaperBroker(로컬 시뮬) + KIS 모의투자**로, **실거래 타깃은 토스**로 둔다. 코드 변경 없이 브로커만 교체.

> ⚠️ 토스 엔드포인트 상세(아래 4절)는 3자 가이드 기반 정리이므로 **공식 `developers.tossinvest.com` 스펙으로 반드시 재검증**할 것.

---

## 3. 시스템 구조

```
┌─────────────┐     ┌──────────────────────────────────────┐
│  React UI    │◄───►│            FastAPI (async)           │
│ 대시보드/주문 │     │  /analysis  /market  /orders  /paper │
└─────────────┘     └───────────────┬──────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
┌───────────────┐         ┌────────────────────┐      ┌────────────────────┐
│ 분석 엔진      │         │  데이터 계층        │      │  브로커 계층        │
│ (멀티에이전트) │         │  MarketDataProvider │      │  BrokerAdapter (IF) │
│ Optimistic     │         │  ├ 실시간: 브로커   │      │  ├ PaperBroker(기본)│
│ Pessimistic    │         │  └ 과거: FDR/pykrx  │      │  ├ KISBroker(모의)  │
│ RiskManager    │         └────────────────────┘      │  └ TossBroker(실거래)│
│ Coordinator    │                                      └─────────┬──────────┘
└──────┬─────────┘                                                │
       │   신호(BUY/SELL/conf, 목표가, 손절)                       │ 주문
       ▼                                                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  RiskGuard (주문 안전 게이트)                                       │
│  · 포지션 한도/일일 손실 한도/종목 집중도  · kill-switch           │
│  · 모의=자동 / 실거래=수동 확인 필수  · 호가단위·거래시간 검증      │
└──────────────────────────────────────────────────────────────────┘
```

**핵심 불변식**: 분석 엔진(LLM)의 출력은 *제안*일 뿐이며, 주문은 반드시 `RiskGuard`와 브로커 어댑터를 통과한다. LLM이 브로커 어댑터를 직접 호출하는 경로는 존재하지 않는다.

---

## 4. 브로커 어댑터 인터페이스 (초안)

```python
class BrokerAdapter(Protocol):
    # 인증/계좌
    def authenticate(self) -> None: ...
    def get_accounts(self) -> list[Account]: ...
    def get_holdings(self, account: str) -> list[Position]: ...
    def get_buying_power(self, account: str) -> Money: ...
    # 시세
    def get_price(self, code: str) -> Quote: ...
    def get_orderbook(self, code: str) -> OrderBook: ...
    # 주문
    def place_order(self, req: OrderRequest) -> OrderResult: ...   # 매수/매도
    def cancel_order(self, order_id: str) -> OrderResult: ...
    def amend_order(self, order_id: str, req: OrderAmend) -> OrderResult: ...
    def get_orders(self, account: str) -> list[Order]: ...
```

### 토스 매핑 (검증 필요)
- Base URL: `https://openapi.tossinvest.com`
- 인증: `POST /oauth2/token` (Basic `id:secret` base64, `grant_type=client_credentials`, 토큰 ~1h)
- 계좌 호출 시 `X-Tossinvest-Account` 헤더
- 시세: `GET /v1/market/price`, `/orderbook`, `/candles` (REST 폴링)
- 주문: `POST /v1/orders`, `PATCH/DELETE /v1/orders/{id}`, 사전검증 `GET /v1/orders/{buying-power,sellable,commission}`
- 잔고: `GET /v1/accounts/holdings`
- 심볼: 6자리 코드(`stockCode=005930`)

### KIS 매핑 (모의투자)
- 모의 도메인/실전 도메인 분리, `appkey`/`appsecret` → `access_token`
- 국내주식 현재가/주문/잔고 REST + 실시간 WebSocket
- 개발 단계 기본 권장 (무료·안전)

---

## 5. 데이터 계층

| 용도 | 소스 | 비고 |
|------|------|------|
| 종목 유니버스/상장목록 | FinanceDataReader `StockListing('KRX')` | 코드·이름·시장·섹터 |
| 과거 일봉/수정주가 | FinanceDataReader / pykrx | 백테스트·기술분석 |
| 지수/공매도/재무 | pykrx | KOSPI/KOSDAQ/KRX 분류 |
| 장중 실시간 시세·호가 | 브로커 API (토스/KIS) | 주문 직전 가격 |
| 환율·휴장일·거래시간 | 브로커 calendar API + 자체 KRX 캘린더 | |

**국내 시장 특수사항(반드시 반영)**:
- 거래시간 09:00–15:30 KST (+ 시간외 단일가/장전·장후). 기존 `market_time` 유틸은 US 기준 → KRX로 교체.
- **호가단위(tick size)**: 가격대별 차등(예: ~2,000원 1원, ~5,000원 5원 …). 지정가 주문 시 호가단위 정규화 필수.
- 상·하한가(±30%), VI(변동성완화장치), 거래정지/관리·환기종목 필터.
- 통화 KRW, 소수점 없는 주식 수량.

---

## 6. 안전 설계 (RiskGuard)

실거래 시스템에서 가장 중요한 부분입니다.

1. **기본값은 모의/시뮬**: `BROKER=paper` 가 디폴트. 실거래는 명시적 `BROKER=toss` + 환경 플래그 `ALLOW_LIVE_TRADING=true` 동시 충족 시에만.
2. **수동 확인 게이트**: 실거래 주문은 자동 실행 금지 → UI/CLI에서 사람이 확인.
3. **한도**: 1회 주문 금액·종목별 비중·일일 최대 손실·일일 주문 횟수 상한.
4. **Kill-switch**: 일일 손실 한도 초과 시 신규 주문 전면 차단.
5. **검증 체인**: 호가단위·거래시간·매수가능금액·매도가능수량을 주문 전 확인.
6. **감사 로그**: 모든 신호→결정→주문→체결을 추적 ID로 기록.
7. **LLM 격리**: 분석 출력은 구조화 JSON(스키마 검증)만 수용, 임의 코드/주문 실행 불가.

---

## 7. 최신 기반기술 채택 (2026 조사)

| 영역 | 기존 | 채택 |
|------|------|------|
| 패키지/가상환경 | pip + venv | **uv** (수십 배 빠른 설치·잠금) |
| 린트/포맷 | (black/isort/flake8 가정) | **ruff** (Rust, 통합·초고속) |
| 타입체크 | - | **mypy** (점진 도입) |
| 검증/설정 | pydantic v2 | 유지·강화 (pydantic-settings) |
| 웹 프레임워크 | FastAPI | 유지 (ASGI async) |
| 프론트 | React 19 + Vite + Tailwind4 | 유지 |
| AI | OpenAI 단일 | 멀티프로바이더(OpenAI/Gemini) + 구조화 출력 |

→ 즉시 큰 마이그레이션 대신 **신규 코드부터 uv/ruff 기준** 적용, 기존 `requirements.txt`는 `pyproject.toml`로 점진 이전.

---

## 8. 단계별 로드맵

- **Phase 0 — 기반 정리** ✅ (죽은코드/리포트 정리, docs 재배치, 환경 세팅)
- **Phase 1 — 분석 정상화**: 멀티에이전트를 API에 연결, 가짜 하드코딩값 제거, async/sync 이중구조 통합.
- **Phase 2 — 국내 데이터 전환**: FDR/pykrx 연동, 심볼·통화·거래시간·호가단위 KRX화, 캐싱.
- **Phase 3 — 브로커 추상화 + PaperBroker**: 인터페이스 정의, 로컬 시뮬레이터로 전 주문 흐름 검증.
- **Phase 4 — KIS 모의투자 어댑터**: 실제 브로커 API를 모의계좌로 연결·검증.
- **Phase 5 — RiskGuard + 수동 게이트**: 한도/kill-switch/감사로그/확인 UI.
- **Phase 6 — 토스 실거래 어댑터**: 공식 스펙 검증 후 소액 실거래, 단계적 한도 상향.

각 Phase 종료 시 모의계좌 회귀 테스트 통과를 게이트로 둔다.

---

## 부록 — 출처 (2026-06 조사)

- 토스증권 Open API: https://corp.tossinvest.com/ko/open-api , https://www.pulse-know.com/toss-invest-open-api-guide-2026/
- 한국투자 KIS Developers: https://apiportal.koreainvestment.com/apiservice , https://github.com/Soju06/python-kis
- 키움 REST API: https://openapi.kiwoom.com/ , https://github.com/younghwan91/kiwoom-rest-api
- KRX 데이터: https://github.com/sharebook-kr/pykrx , https://pypi.org/project/pykrx/ , FinanceDataReader
- 최신 스택: https://dev.to/devasservice/a-modern-python-toolkit-pydantic-ruff-mypy-and-uv-4b2f
