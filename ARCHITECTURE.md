# 🏗️ 제로월드 예약 모니터링 시스템 아키텍처

## 📋 목차
- [시스템 개요](#-시스템-개요)
- [프로젝트 구조](#-프로젝트-구조)
- [모듈 아키텍처](#-모듈-아키텍처)
- [데이터 플로우](#-데이터-플로우)
- [배포 아키텍처](#-배포-아키텍처)
- [확장성 및 유지보수](#-확장성-및-유지보수)

## 🎯 시스템 개요

### 핵심 기능
제로월드 홍대점의 예약 테마("층간소음", "사랑하는감?" 등)를 **24시간 1분 간격**으로 모니터링하여 예약 가능한 슬롯을 발견하면 **텔레그램으로 즉시 알림**을 전송하는 자동화 시스템

### 기술 스택
- **언어**: Python 3.9+
- **스케줄링**: APScheduler (비동기 작업 관리)
- **웹 스크래핑**: requests, BeautifulSoup4, lxml
- **알림**: python-telegram-bot (비동기 봇)
- **로깅**: loguru (구조화된 로깅)
- **배포**: Railway (무료 24시간 호스팅)
- **상태 관리**: JSON 파일 기반 로컬 스토리지

### 운영 특징
- 🕐 **24시간 무제한 모니터링** (기존 09:00-21:00에서 확장)
- 📱 **실시간 텔레그램 알림** (예약 가능 슬롯 발견 시)
- 🤖 **봇 명령어 지원** (`/status`, `/help`, `/branch` 등)
- 🔄 **브랜치 전환** (다른 테마 모니터링 가능)
- 📊 **정각마다 상태 보고**

## 📁 프로젝트 구조

```
zeroworld-checker/
├── checker/                 # 📦 메인 패키지
│   ├── __init__.py         # 패키지 초기화
│   ├── main.py             # 🚀 애플리케이션 진입점 및 스케줄러
│   ├── config.py           # ⚙️ 환경설정 및 상수 관리
│   ├── fetch.py            # 🕷️ 웹 스크래핑 및 데이터 수집
│   ├── notifier.py         # 📱 텔레그램 알림 및 봇 관리
│   ├── state.py            # 💾 상태 저장 및 변경 감지
│   └── railway_api.py      # 🚂 Railway API 클라이언트
├── setup.py                # 🔧 환경설정 도우미 스크립트
├── requirements.txt        # 📋 Python 의존성
├── Procfile               # ⚡ Railway 배포 설정
├── railway.json           # 🚂 Railway 프로젝트 설정
├── Dockerfile             # 🐳 컨테이너 설정 (예비)
└── README.md              # 📖 사용자 가이드
```

## 🧩 모듈 아키텍처

### 1. 🚀 main.py - 메인 엔진
**책임**: 전체 시스템 오케스트레이션 및 스케줄링

```python
class ZeroworldChecker:
    - 스케줄러 관리 (APScheduler)
    - 텔레그램 봇 polling (별도 스레드)
    - 시스템 상태 모니터링
    - 에러 처리 및 복구
```

**핵심 기능**:
- ⏰ **1분 간격 슬롯 체크** (`check_slots()`)
- 📊 **매 정각 상태 메시지** (`send_status_message()`)
- 🧪 **시스템 테스트** (`test_system()`)
- 🛑 **우아한 종료 처리** (signal handling)

### 2. ⚙️ config.py - 설정 관리자
**책임**: 환경변수 및 설정 중앙화

```python
# 환경별 설정 자동 감지
IS_CLOUD = Railway/Render 환경 자동 감지
LOG_FILE = 클라우드에서는 stdout, 로컬에서는 파일

# 모니터링 설정
THEME_NAME = "사랑하는감?"  # 브랜치별로 다름
RUN_HOURS = range(0, 24)   # 24시간 모니터링
CHECK_INTERVAL_MINUTES = 1  # 1분 간격
```

### 3. 🕷️ fetch.py - 데이터 수집 엔진
**책임**: 제로월드 웹사이트에서 예약 정보 수집

```python
class ZeroworldFetcher:
    - CSRF 토큰 기반 세션 관리
    - HTML + API 데이터 조합 분석
    - 숨겨진 예약 데이터 추출
    - 시간 필터링 (과거 슬롯 제외)
```

**고급 기능**:
- 🔐 **CSRF 토큰 자동 획득**
- 🕵️ **숨겨진 JSON 데이터 파싱** (`reservationHiddenData`)
- 🎯 **실제 예약 상태 검증** (API + 숨겨진 데이터 교차 확인)
- ⏰ **과거 슬롯 자동 필터링**

### 4. 📱 notifier.py - 통신 허브
**책임**: 텔레그램 알림 및 봇 명령어 처리

```python
class TelegramNotifier:
    - 비동기 메시지 전송
    - 쿨타임 기반 스팸 방지
    - 메시지 포맷팅

class TelegramBotHandler:
    - 명령어 처리 (/status, /help, /branch)
    - Railway 브랜치 전환
    - 사용자 상호작용
```

**지원 명령어**:
- 📊 `/status` - 모니터링 상태 확인
- 🌿 `/branch main|test` - 브랜치 전환 (테마 변경)
- 🧪 `/test` - 봇 연결 테스트
- ❓ `/help` - 도움말

### 5. 💾 state.py - 상태 관리자
**책임**: 슬롯 상태 저장 및 변경 감지

```python
class StateManager:
    - JSON 파일 기반 저장
    - 스레드 안전성 보장
    - 손상된 파일 자동 복구
    - 새로운 예약 가능 슬롯 감지
```

**데이터 구조**:
```json
{
  "slots": {
    "2025-01-29 18:30:00": "예약가능",
    "2025-01-29 20:00:00": "매진"
  },
  "last_updated": "2025-01-29 15:30:00"
}
```

### 6. 🚂 railway_api.py - 배포 관리자
**책임**: Railway GraphQL API를 통한 브랜치 전환

```python
class RailwayAPI:
    - GraphQL 쿼리 실행
    - 서비스 브랜치 변경
    - 자동 재배포 트리거
```

**브랜치별 테마 매핑**:
- `main` → "층간소음"
- `test` → "사랑하는감?"

## 🔄 데이터 플로우

위의 시스템 아키텍처 다이어그램에서 전체적인 구조를 확인할 수 있고, 아래 시퀀스 다이어그램에서 상세한 데이터 흐름을 볼 수 있습니다.

### 메인 모니터링 플로우
```
1. 스케줄러 트리거 (1분마다)
   ↓
2. fetch.py: 웹사이트 스크래핑
   ├── CSRF 토큰 획득
   ├── HTML 페이지 파싱 (숨겨진 데이터)
   ├── API 호출 (공개 데이터)
   └── 실제 예약 상태 교차 검증
   ↓
3. state.py: 상태 비교
   ├── 이전 상태 로드
   ├── 새로운 예약 가능 슬롯 감지
   └── 현재 상태 저장
   ↓
4. notifier.py: 알림 전송 (새 슬롯 발견 시)
   ├── 메시지 포맷팅
   ├── 쿨타임 체크
   └── 텔레그램 전송
```

### 봇 명령어 플로우
```
텔레그램 메시지 수신
   ↓
notifier.py: 명령어 파싱
   ├── /status → 현재 상태 반환
   ├── /branch → railway_api.py 호출
   └── /help → 도움말 전송
```

### 브랜치 전환 플로우
```
/branch 명령어 수신
   ↓
railway_api.py: Railway API 호출
   ├── GraphQL 뮤테이션 실행
   ├── 브랜치 변경
   ├── 자동 재배포 트리거
   └── 성공/실패 알림
```

## 🌐 배포 아키텍처

### Railway 배포 환경
```
GitHub Repository
├── main 브랜치 (층간소음 테마)
└── test 브랜치 (사랑하는감? 테마)
   ↓
Railway Service
├── 자동 빌드 & 배포
├── 환경변수 관리
├── 24시간 무료 실행
└── 로그 수집
   ↓
Telegram Bot API
├── 실시간 알림 전송
├── 명령어 처리
└── 사용자 상호작용
```

### 환경변수 구성
```bash
# 필수 환경변수
TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
RAILWAY_ENVIRONMENT_NAME=production

# 선택적 환경변수 (브랜치 전환용)
RAILWAY_API_TOKEN=your_api_token
RAILWAY_PROJECT_ID=your_project_id
RAILWAY_SERVICE_ID=your_service_id
```

### 로그 및 모니터링
- **Railway 로그**: 모든 시스템 로그 수집
- **텔레그램 상태 메시지**: 매 정각 자동 전송
- **에러 알림**: 중요한 오류 발생 시 텔레그램 알림

## 🚀 확장성 및 유지보수

### 새로운 테마 추가
1. `config.py`에서 `THEME_NAME` 변경
2. 새 브랜치 생성 및 Railway 연결
3. `railway_api.py`의 `BRANCH_THEME_MAPPING`에 추가

### 모니터링 주기 변경
- `config.py`의 `CHECK_INTERVAL_MINUTES` 수정
- `RUN_HOURS` 범위 조정 (24시간 vs 특정 시간대)

### 알림 채널 추가
- `notifier.py`에 새로운 알림 클래스 추가
- Discord, Slack, 이메일 등 확장 가능

### 다중 테마 동시 모니터링
```python
# 예시: 여러 테마 동시 모니터링
THEMES = ["층간소음", "사랑하는감?", "다른테마"]
for theme in THEMES:
    schedule_monitoring(theme)
```

### 에러 복구 메커니즘
- **자동 재시작**: Railway의 자동 재시작 기능
- **상태 파일 복구**: 손상된 state.json 자동 백업 및 복구
- **네트워크 오류 처리**: 지수 백오프 재시도 로직

### 성능 최적화
- **메모리 사용량**: 상태 파일 크기 모니터링
- **API 호출 제한**: 쿨타임 및 요청 제한 준수
- **로그 크기 관리**: 로그 순환 및 압축

---

## 🔧 개발자 가이드

### 로컬 개발 환경 설정
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정 (Windows)
python setup.py

# 3. 테스트 실행
python -m checker.main --test

# 4. 단일 실행
python -m checker.main --once
```

### 디버깅 모드
```bash
# 설정 확인
python -m checker.main --config-test

# 봇 테스트
python -m checker.main --bot-test

# 디버그 로그 레벨 (config.py)
LOG_LEVEL = "DEBUG"
```

이 아키텍처 문서를 통해 새로운 팀원도 프로젝트의 전체 구조를 빠르게 파악할 수 있고, 리팩터링 시 큰 그림을 놓치지 않을 수 있습니다! 🎯