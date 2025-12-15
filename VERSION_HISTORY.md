# AI Stock Trading System - 버전 히스토리

이 문서는 AI Stock Trading System의 베타 버전 및 안정 버전의 히스토리를 추적합니다.

---

## 버전 관리 정책

### 버전 명명 규칙

프로젝트는 [Semantic Versioning 2.0.0](https://semver.org/)을 따릅니다:

- **MAJOR.MINOR.PATCH** (예: 1.2.3)
- **MAJOR.MINOR.PATCH-beta** (베타 버전, 예: 1.2.3-beta)

### 베타 버전 정책

- **목적**: 정기 점검 및 보수적 업데이트 테스트
- **증가 규칙**: 0.0.01씩 증가 (예: 1.2.5-beta → 1.2.6-beta)
- **안정화**: 충분한 테스트 후 베타 태그 제거하여 안정 버전으로 전환

---

## 최신 버전

### 안정 버전 (Stable)
- **버전**: v1.3.0
- **출시일**: 2025-12-11
- **주요 변경사항**: 14개 패키지 업데이트, 4+ 보안 취약점 해결, 베타 버전 안정화

### 베타 버전 (Beta)
- **버전**: v1.3.1-beta
- **출시일**: 2025-12-15
- **주요 변경사항**: FastAPI 0.124.4, SQLAlchemy 2.0.45 패치 업데이트
- **상태**: 테스트 중

---

## 베타 버전 히스토리

### v1.3.1-beta (2025-12-15)
**유형**: 정기 점검 및 보수적 패치 업데이트

**변경사항**:
- FastAPI 0.124.0 → 0.124.4 업데이트
  - Parameter aliases 버그 수정 (0.124.4)
  - Tagged union with discriminator 지원 개선 (0.124.3)
  - TYPE_CHECKING 지원 수정 (0.124.2)
  - Arbitrary types 처리 개선 (0.124.1)
  - 2025-12-12 최종 릴리스
- SQLAlchemy 2.0.44 → 2.0.45 업데이트
  - 2.1 시리즈 개선사항 백포트
  - Python 3.14 호환성 지속 개선
  - 안정성 및 성능 향상
  - 2025-12-09 릴리스

**패키지 현황**:
- 전체 패키지: 15개
- 업데이트된 패키지: 2개 (FastAPI, SQLAlchemy)
- 최신 버전 유지: 13개
- 보안 취약점: 0개 (프론트엔드 감사 깨끗함)

**파일 변경**:
- `backend/requirements.txt`: fastapi==0.124.4, sqlalchemy==2.0.45
- `VERSION`: 1.3.1-beta
- `CHANGELOG.md`: v1.3.1-beta 항목 추가
- `VERSION_HISTORY.md`: 베타 버전 히스토리 업데이트

**테스트 결과**:
- ✅ FastAPI 0.124.4 import 및 기능 테스트 통과
- ✅ SQLAlchemy 2.0.45 import 및 기능 테스트 통과
- ✅ Pydantic 2.12.5 호환성 확인
- ✅ FastAPI + SQLAlchemy + Pydantic 통합 테스트 통과

**Git 정보**:
- Commit: (예정)
- Tag: `v1.3.1-beta`

**참고 문서**:
- [완전한 패키지 분석](./complete_package_analysis.md)
- [패키지 업데이트 요약](./package_updates.md)
- [FastAPI 릴리스 정보](./fastapi_releases.md)

---

### v1.2.8-beta (2025-12-08)
**유형**: 정기 점검 및 보수적 업데이트 + 보안 패치

**변경사항**:
- FastAPI 0.123.0 → 0.124.0 업데이트
  - Traceback 개선: 엔드포인트 메타데이터 추가
  - 디버깅 경험 향상
  - 2025-12-06 릴리스
- 프론트엔드 보안 취약점 해결
  - @modelcontextprotocol/sdk (GHSA-w48q-cv73-mx4w): DNS rebinding protection 취약점 패치
  - 심각도: High (높음)
  - `pnpm audit --fix`로 자동 패치 적용

**파일 변경**:
- `backend/requirements.txt`: fastapi==0.124.0
- `frontend/package.json`: 보안 overrides 추가 (@modelcontextprotocol/sdk)
- `VERSION`: 1.2.8-beta
- `CHANGELOG.md`: v1.2.8-beta 항목 추가
- `VERSION_HISTORY.md`: 베타 버전 히스토리 업데이트

**Git 정보**:
- Commit: (예정)
- Tag: `v1.2.8-beta`

**참고 문서**:
- [점검 결과](./inspection_findings_2025-12-08.md)

---

### v1.2.7-beta (2025-12-01)
**유형**: 정기 점검 및 보수적 업데이트 + 보안 패치

**변경사항**:
- FastAPI 0.121.3 → 0.123.0 업데이트
  - 의존성 캠싱 개선
  - 2025-11-30 릴리스
- Pydantic 2.12.4 → 2.12.5 업데이트
  - MISSING sentinel 이슈 수정
  - 문서 개선
  - 2025-11-26 릴리스
- 프론트엔드 보안 취약점 해결
  - js-yaml (CVE-2025-64718): Prototype pollution 취약점 패치
  - body-parser (CVE-2025-13466): DoS 취약점 패치
  - `pnpm audit --fix`로 자동 패치 적용

**파일 변경**:
- `backend/requirements.txt`: fastapi==0.123.0, pydantic==2.12.5
- `frontend/package.json`: 보안 overrides 추가
- `VERSION`: 1.2.7-beta
- `CHANGELOG.md`: v1.2.7-beta 항목 추가
- `VERSION_HISTORY.md`: 베타 버전 히스토리 업데이트

**Git 정보**:
- Commit: (예정)
- Tag: `v1.2.7-beta`

**참고 문서**:
- [점검 중간 결과](./inspection_findings_2025-12-01.md)
- [기술 동향 조사](./tech_research_2025-12-01.md)

---

### v1.2.6-beta (2025-11-24)
**유형**: 정기 점검 및 보수적 패치 업데이트

**변경사항**:
- FastAPI 0.121.2 → 0.121.3 업데이트
  - 내부 리팩토링 및 Starlette 의존성 범위 조정
  - 2025-11-19 릴리스

**파일 변경**:
- `backend/requirements.txt`: fastapi==0.121.3
- `VERSION`: 1.2.6-beta
- `CHANGELOG.md`: v1.2.6-beta 항목 추가
- `VERSION_HISTORY.md`: 베타 버전 히스토리 업데이트

**Git 정보**:
- Commit: (예정)
- Tag: `v1.2.6-beta`

**참고 문서**:
- [의존성 점검 보고서](./dependency_check_2025-11-24.md)

---

### v1.2.5-beta (2025-11-17)
**유형**: 정기 점검 및 보수적 패치 업데이트

**변경사항**:
- FastAPI 0.121.1 → 0.121.2 업데이트
  - 버그 수정 및 안정성 개선
  - 2025-11-13 릴리스

**파일 변경**:
- `backend/requirements.txt`: fastapi==0.121.2
- `VERSION`: 1.2.5-beta
- `CHANGELOG.md`: v1.2.5-beta 항목 추가
- `VERSION_HISTORY.md`: 베타 버전 히스토리 업데이트

**Git 정보**:
- Commit: (예정)
- Tag: `v1.2.5-beta`

**참고 문서**:
- [점검 분석 보고서](./inspection_analysis_2025-11-17.md)
- [의존성 분석 보고서](./dependency_analysis_final_2025-11-17.md)
- [기술 동향 보고서](./tech_trends_2025-11-17.md)

---

### v1.2.4-beta (2025-11-10)
**유형**: 정기 점검 및 보수적 마이너/패치 업데이트

**변경사항**:
- FastAPI 0.120.4 → 0.121.1 업데이트
- Pydantic 2.12.3 → 2.12.4 업데이트
- HTTPX 0.27.2 → 0.28.1 업데이트
- aiofiles 24.1.0 → 25.1.0 업데이트
- aiosqlite 0.20.0 → 0.21.0 업데이트
- python-dotenv 1.0.1 → 1.2.1 업데이트
- pytz 2024.2 → 2025.2 업데이트
- tenacity 9.0.0 → 9.1.2 업데이트
- tiktoken 0.8.0 → 0.12.0 업데이트

**파일 변경**:
- `backend/requirements.txt`: 9개 패키지 버전 업데이트
- `VERSION`: 1.2.4-beta
- `CHANGELOG.md`: v1.2.4-beta 항목 추가
- `VERSION_HISTORY.md`: 베타 버전 히스토리 업데이트

**Git 정보**:
- Commit: (예정)
- Tag: `v1.2.4-beta`

**참고 문서**:
- [점검 분석 보고서](./inspection_analysis_2025-11-10.md)
- [업데이트 계획서](./update_plan_2025-11-10.md)
- [점검 보고서](./INSPECTION_REPORT_2025-11-10.md)

---

### v1.2.3-beta (2025-11-03)
**유형**: 정기 점검 및 보수적 패치 업데이트

**변경사항**:
- FastAPI 0.120.0 → 0.120.4 업데이트

**파일 변경**:
- `backend/requirements.txt`: fastapi==0.120.4
- `VERSION`: 1.2.3-beta
- `CHANGELOG.md`: v1.2.3-beta 항목 추가

**Git 정보**:
- Commit: `9877a16`
- Tag: `v1.2.3-beta`

**참고 문서**:
- [점검 분석 보고서](./inspection_analysis_2025-11-03.md)
- [업데이트 계획서](./update_plan_2025-11-03.md)
- [점검 보고서](./INSPECTION_REPORT_2025-11-03.md)

---

### v1.2.2-beta (2025-10-27)
**유형**: 정기 점검 및 보수적 업데이트

**변경사항**:
- FastAPI 0.119.0 → 0.120.0
- SQLAlchemy 2.0.43 → 2.0.44
- Pandas 2.2.3 → 2.3.3
- yfinance 0.2.44 → 0.2.66
- uvicorn 0.30.6 → 0.38.0
- pydantic 2.9.2 → 2.12.3
- 프론트엔드 보안 취약점 수정 (pnpm audit --fix)

**Git 정보**:
- Commit: `ee9745f`
- Tag: `v1.2.2-beta`

---

### v1.2.1-beta (2025-10-20)
**유형**: 정기 점검 및 보수적 보안 업데이트

**변경사항**:
- FastAPI 0.115.0 → 0.119.0 (보안 개선)
- SQLAlchemy 2.0.35 → 2.0.43 (보안 권장사항)
- Vite 6.3.5 → 6.4.0 (버그 수정 및 성능 개선)

**Git 정보**:
- Commit: `daeed91`
- Tag: `v1.2.1-beta`

---

## 안정 버전 히스토리

### v1.3.0 (2025-12-11)
**유형**: 안정 버전 출시 (베타에서 승격)

**주요 변경사항**:
- v1.2.1-beta ~ v1.2.8-beta의 모든 변경사항 통합
- 14개 백엔드 패키지 업데이트
  - FastAPI 0.115.0 → 0.124.0 (9단계 마이너 업데이트)
  - Pydantic 2.9.2 → 2.12.5 (회귀 버그 수정)
  - SQLAlchemy 2.0.35 → 2.0.44 (Python 3.14 호환성)
  - 기타 11개 패키지 업데이트
- 4+ 프론트엔드 보안 취약점 해결
  - @modelcontextprotocol/sdk (High 심각도)
  - js-yaml, body-parser 취약점
- 다수의 버그 수정 및 안정성 개선

**베타 기간**:
- 시작: 2025-10-20 (v1.2.1-beta)
- 종료: 2025-12-08 (v1.2.8-beta)
- 기간: 약 7주 (8개 베타 버전)

**테스트 결과**:
- 통과: 16개
- 실패: 0개
- 건너뛀: 9개 (비동기 테스트 설정 문제)

**파일 변경**:
- `VERSION`: 1.3.0
- `CHANGELOG.md`: v1.3.0 항목 추가
- `VERSION_HISTORY.md`: 안정 버전 히스토리 업데이트
- `TEST_RESULTS_2025-12-11.md`: 테스트 결과 문서화

**Git 정보**:
- Commit: (예정)
- Tag: `v1.3.0`

**참고 문서**:
- [테스트 결과](./TEST_RESULTS_2025-12-11.md)
- [종합 분석 보고서](./comprehensive_analysis_report.md)
- [버전 업데이트 타당성 평가](./version_update_feasibility.md)
- [베타 버전 분석](./beta_version_analysis.md)

---

### v1.2.0 (2025-10-13)
**유형**: 메이저 기능 업데이트

**주요 변경사항**:
- Redis 클라이언트를 동기에서 비동기로 마이그레이션
- 시장 시간 계산 버그 수정 (날짜 롤오버 문제)

**Git 정보**:
- Commit: `fafec81`
- Tag: `v1.2.0`

---

### v1.1.0 (2025-09-27)
**유형**: 초기 프로덕션 릴리스

**주요 변경사항**:
- Flask 기반 백엔드 서버 생성
- OpenAI 래퍼 추가

**Git 정보**:
- Tag: `v1.1.0`

---

### v1.0.0 (초기 릴리스)
**유형**: 초기 버전

**주요 기능**:
- Multi-agent AI 분석 시스템
- React + Tailwind CSS 프론트엔드
- SQLite 데이터베이스 통합
- Yahoo Finance 데이터 수집
- OpenAI API 통합
- 기본 포트폴리오 관리 기능

---

## 버전 비교표

| 버전 | 출시일 | 유형 | FastAPI | SQLAlchemy | OpenAI SDK | 주요 기능 |
|---|---|---|---|---|---|---|
| v1.3.0 | 2025-12-11 | 안정 | 0.124.0 | 2.0.44 | 1.54.4 | 14개 패키지 업데이트, 4+ 보안 패치 |
| v1.2.8-beta | 2025-12-08 | 베타 | 0.124.0 | 2.0.44 | 1.54.4 | FastAPI 업데이트, 고위험 보안 패치 |
| v1.2.7-beta | 2025-12-01 | 베타 | 0.123.0 | 2.0.44 | 1.54.4 | FastAPI/Pydantic 업데이트, 보안 패치 |
| v1.2.6-beta | 2025-11-24 | 베타 | 0.121.3 | 2.0.44 | 1.54.4 | FastAPI 패치 업데이트 |
| v1.2.5-beta | 2025-11-17 | 베타 | 0.121.2 | 2.0.44 | 1.54.4 | FastAPI 패치 업데이트 |
| v1.2.4-beta | 2025-11-10 | 베타 | 0.121.1 | 2.0.44 | 1.54.4 | 9개 패키지 보수적 업데이트 |
| v1.2.3-beta | 2025-11-03 | 베타 | 0.120.4 | 2.0.44 | 1.54.4 | FastAPI 패치 업데이트 |
| v1.2.2-beta | 2025-10-27 | 베타 | 0.120.0 | 2.0.44 | 1.54.4 | 의존성 업데이트, 보안 패치 |
| v1.2.1-beta | 2025-10-20 | 베타 | 0.119.0 | 2.0.43 | 1.54.4 | 보안 업데이트 |
| v1.2.0 | 2025-10-13 | 안정 | 0.115.0 | 2.0.35 | 1.54.4 | Redis 비동기, 버그 수정 |
| v1.1.0 | 2025-09-27 | 안정 | - | - | - | 백엔드 서버, CI/CD |
| v1.0.0 | - | 안정 | - | - | - | 초기 릴리스 |

---

## 다음 버전 계획

### v1.2.6 (안정 버전)
- **예상 출시일**: v1.2.6-beta 검증 후
- **변경사항**: v1.2.6-beta와 동일 (베타 태그 제거)

### v1.3.0 (향후 계획)
- **예상 출시일**: 미정
- **주요 기능**:
  - OpenAI SDK v2.x 마이그레이션
  - 새로운 AI 모델 지원 (GPT-5 등)
  - 성능 최적화

---

## 참고 사항

### 베타 버전 사용 시 주의사항

베타 버전은 테스트 및 검증 목적으로 사용되며, 프로덕션 환경에서는 안정 버전 사용을 권장합니다.

### 버전 선택 가이드

- **프로덕션 환경**: 최신 안정 버전 (v1.2.0) 사용
- **개발/테스트 환경**: 최신 베타 버전 (v1.2.6-beta) 사용 가능
- **보수적 접근**: 이전 안정 버전 (v1.1.0) 사용

### 업그레이드 경로

```
v1.0.0 → v1.1.0 → v1.2.0 → v1.2.6 (예정)
```

베타 버전은 선택적이며, 안정 버전 간 직접 업그레이드 가능합니다.

---

**문서 버전**: 1.2
**최종 업데이트**: 2025-12-08
**작성자**: Manus AI
