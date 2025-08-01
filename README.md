# 제로월드 홍대점 예약 모니터링 시스템

집 PC에서 09:00 ~ 21:00(한국시간) 동안 5분 간격으로 제로월드 홍대 '층간소음' 예약 페이지를 스크래핑해 빈 슬롯이 생기면 텔레그램으로 즉시 알림을 보내는 파이썬 스크립트입니다.

## 🎯 주요 기능

- **자동 모니터링**: 매일 09:00~21:00 시간대에 5분 간격으로 자동 체크
- **실시간 알림**: 새로 예약 가능해진 슬롯 발견 시 텔레그램 즉시 알림
- **스마트 스크래핑**: Ajax API 우선 호출, 실패 시 HTML 파싱 fallback
- **상태 캐싱**: 이전 상태를 로컬 파일에 저장하여 변경사항만 감지
- **안정적 운영**: 로그 관리, 오류 처리, 재시도 로직 포함

## 📋 시스템 요구사항

- **OS**: Windows 10/11 또는 Ubuntu (WSL 지원)
- **Python**: 3.11 이상
- **인터넷 연결**: 제로월드 사이트 및 텔레그램 API 접근 필요

## 🚀 설치 및 설정

### 1. 프로젝트 클론 및 패키지 설치

```bash
# 가상환경 생성 (권장)
python -m venv env

# 가상환경 활성화
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 텔레그램 봇 설정

#### 2.1 봇 생성
1. 텔레그램에서 [@BotFather](https://t.me/BotFather) 검색
2. `/newbot` 명령어 입력
3. 봇 이름과 사용자명 설정
4. 발급받은 **토큰** 복사해두기

#### 2.2 채팅 ID 확인
1. 봇과 대화 시작 (메시지 하나 전송)
2. [@userinfobot](https://t.me/userinfobot)에게 `/start` 전송
3. 표시된 **Your user ID**를 복사해두기

#### 2.3 환경변수 설정

##### Windows (PowerShell):
```powershell
# 임시 설정 (현재 세션만)
$env:TELEGRAM_BOT_TOKEN="1234567890:ABC-DEF..."
$env:TELEGRAM_CHAT_ID="987654321"

# 영구 설정
[Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "1234567890:ABC-DEF...", "User")
[Environment]::SetEnvironmentVariable("TELEGRAM_CHAT_ID", "987654321", "User")
```

##### Linux/Mac:
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export TELEGRAM_BOT_TOKEN="1234567890:ABC-DEF..."
export TELEGRAM_CHAT_ID="987654321"

# 현재 세션에 즉시 적용
source ~/.bashrc
```

#### 2.4 설정 확인
```bash
python -m checker.main --config-test
```

### 3. 시스템 테스트

#### 3.1 전체 시스템 테스트
```bash
python -m checker.main --test
```

#### 3.2 개별 모듈 테스트
```bash
# API 연결 테스트
python -m checker.fetch

# 텔레그램 연결 테스트
python -m checker.notifier

# 상태 관리 테스트
python -m checker.state
```

## 🎮 사용법

### 일반 모니터링 모드
```bash
python -m checker.main
```

### 한 번만 체크 (테스트)
```bash
python -m checker.main --once
```

### 백그라운드 실행 (Linux/Mac)
```bash
nohup python -m checker.main > monitoring.log 2>&1 &
```

### Windows 서비스로 실행
1. `startup.bat` 파일 생성:
```batch
@echo off
cd /d "C:\Cursor\zeroworld-checker"
python -m checker.main
```

2. 작업 스케줄러에 등록

## 📊 모니터링 정보

### 로그 파일 위치
- `checker.log` - 메인 로그 파일
- `state.json` - 슬롯 상태 저장 파일

### 체크 주기
- **운영 시간**: 매일 09:00 ~ 20:59
- **체크 간격**: 5분마다
- **대상 테마**: 층간소음

### 알림 조건
- 이전에 매진이었다가 예약 가능으로 변경된 슬롯
- 새로 추가된 예약 가능 슬롯

## ⚙️ 고급 설정

### config.py 수정
```python
# 모니터링 기간 변경
DATE_START = "2025-02-01"
DATE_END = "2025-02-28"

# 체크 간격 변경 (분)
CHECK_INTERVAL_MINUTES = 3

# 운영 시간 변경
RUN_HOURS = range(8, 22)  # 08:00 ~ 21:59
```

### 다른 테마 모니터링
```python
# config.py에서 테마명 변경
THEME_NAME = "다른테마명"
```

## 🐛 문제해결

### 자주 발생하는 오류

#### 1. "텔레그램 봇 토큰이 설정되지 않았습니다"
**해결책**: 환경변수 `TELEGRAM_BOT_TOKEN` 설정 확인

#### 2. "채팅 ID를 찾을 수 없습니다"
**해결책**: 
- 봇에게 먼저 메시지 전송
- 채팅 ID 값 재확인

#### 3. "API 호출 실패"
**해결책**:
- 인터넷 연결 확인
- 제로월드 사이트 접속 상태 확인
- 너무 빈번한 요청으로 인한 차단 가능성 체크

#### 4. "python-telegram-bot가 설치되지 않았습니다"
**해결책**:
```bash
pip install python-telegram-bot
```

### 로그 확인
```bash
# 실시간 로그 확인 (Linux/Mac)
tail -f checker.log

# Windows에서는 메모장으로 열기
notepad checker.log
```

## 🔧 개발자 정보

### 프로젝트 구조
```
zeroworld-checker/
├── checker/
│   ├── __init__.py          # 패키지 초기화
│   ├── config.py            # 설정 파일
│   ├── fetch.py             # API 스크래핑
│   ├── state.py             # 상태 관리
│   ├── notifier.py          # 텔레그램 알림
│   └── main.py              # 메인 스케줄러
├── requirements.txt         # 패키지 의존성
├── state.json              # 상태 저장 파일 (자동 생성)
├── checker.log             # 로그 파일 (자동 생성)
└── README.md               # 이 파일
```

### 기여 방법
1. 이슈 등록
2. Fork 후 수정
3. Pull Request 제출

---

## ⚠️ 주의사항

1. **과도한 요청 금지**: 5분 간격을 유지하여 서버에 부담을 주지 마세요
2. **개인 정보 보호**: 텔레그램 토큰과 채팅 ID를 공개하지 마세요
3. **사용 목적**: 개인 사용 목적으로만 사용하세요
4. **법적 책임**: 이 도구 사용으로 인한 문제는 사용자 책임입니다

---

**Happy Booking! 🎉**
1. 생성한 봇을 개인 채팅 또는 그룹에 초대
2. 봇에게 아무 메시지나 전송
3. 브라우저에서 아래 URL 접속 (토큰 부분 교체)
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. 응답에서 `chat.id` 값 확인 및 복사

### 3. 환경변수 설정

#### Windows (PowerShell):
```powershell
$env:TELEGRAM_BOT_TOKEN="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
$env:TELEGRAM_CHAT_ID="-1001234567890"
```

#### Linux/Mac:
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
export TELEGRAM_CHAT_ID="-1001234567890"
```

#### 영구 설정 (Windows):
1. 시스템 환경변수 편집에서 사용자 변수 추가:
   - `TELEGRAM_BOT_TOKEN`: 봇 토큰
   - `TELEGRAM_CHAT_ID`: 채팅 ID

### 4. 설정 파일 수정

`checker/config.py` 파일에서 필요한 설정 수정:

```python
# 모니터링 날짜 범위 (실제 이용 예정 날짜로 수정)
DATE_START = "2025-07-29"
DATE_END = "2025-08-12"

# 기타 설정은 기본값 사용 권장
```

## 🔧 사용법

### 연결 테스트
```bash
# 텔레그램 연결 및 기능 테스트
python -m checker.main --test
```

### 한 번만 체크
```bash
# 현재 상태 확인 (스케줄러 없이)
python -m checker.main --once
```

### 정상 모니터링 시작
```bash
# 백그라운드 모니터링 시작
python -m checker.main
```

### 개별 모듈 테스트
```bash
# 스크래핑 모듈 테스트
python -m checker.fetch

# 상태 관리 모듈 테스트  
python -m checker.state

# 텔레그램 알림 모듈 테스트
python -m checker.notifier
```

## 🏃‍♂️ 영구 실행 설정

### Windows (작업 스케줄러)

1. **작업 스케줄러** 실행 (`taskschd.msc`)
2. **기본 작업 만들기** 클릭
3. 설정:
   - 이름: `제로월드 예약 모니터링`
   - 트리거: `컴퓨터를 시작할 때`
   - 작업: `프로그램 시작`
   - 프로그램: `python`
   - 인수: `-m checker.main`
   - 시작 위치: `C:\Cursor\zeroworld-checker`

### Linux/Ubuntu (systemd)

1. 서비스 파일 생성:
```bash
sudo nano /etc/systemd/user/zeroworld-checker.service
```

2. 서비스 파일 내용:
```ini
[Unit]
Description=Zeroworld Reservation Checker
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/zeroworld-checker
Environment=TELEGRAM_BOT_TOKEN=your_token
Environment=TELEGRAM_CHAT_ID=your_chat_id
ExecStart=/path/to/python -m checker.main
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
```

3. 서비스 활성화:
```bash
systemctl --user enable zeroworld-checker.service
systemctl --user start zeroworld-checker.service
```

## 📁 프로젝트 구조

```
zeroworld-checker/
├─ checker/
│  ├─ __init__.py          # 패키지 초기화
│  ├─ config.py            # 설정 (토큰, 날짜, 시간대 등)
│  ├─ fetch.py             # 스크래핑 (Ajax/HTML)
│  ├─ notifier.py          # 텔레그램 알림
│  ├─ state.py             # 로컬 상태 캐싱
│  └─ main.py              # 메인 스케줄러
├─ requirements.txt        # 필요 패키지
├─ README.md              # 이 파일
├─ state.json             # 상태 캐시 (자동 생성)
└─ checker.log            # 로그 파일 (자동 생성)
```

## 📝 로그 및 상태 파일

- **`checker.log`**: 시스템 실행 로그 (1MB 단위로 순환, 최대 5개 보관)
- **`state.json`**: 이전 예약 상태 캐시 (변경사항 감지용)

## 🔍 문제 해결

### 1. 텔레그램 알림이 오지 않는 경우
- 환경변수 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` 확인
- 봇이 채팅방에 정상 초대되었는지 확인
- `python -m checker.main --test`로 연결 테스트

### 2. 슬롯 정보를 가져올 수 없는 경우
- 제로월드 사이트 접속 가능 여부 확인
- User-Agent 변경 (config.py에서 수정)
- 네트워크 연결 상태 확인

### 3. IP 차단 의심
- `config.py`에서 `REQUEST_TIMEOUT` 증가
- `CHECK_INTERVAL_MINUTES`를 10분 이상으로 증가
- `USER_AGENT` 변경

### 4. 로그 확인
```bash
# 실시간 로그 확인
tail -f checker.log

# Windows에서 로그 확인
Get-Content checker.log -Wait
```

## ⚠️ 주의사항

1. **과도한 요청 금지**: 기본 5분 간격을 권장하며, 너무 자주 요청하지 마세요
2. **개인 정보 보호**: 텔레그램 토큰과 채팅 ID를 안전하게 관리하세요
3. **합법적 사용**: 개인 사용 목적으로만 사용하고, 사이트 이용약관을 준수하세요
4. **책임 한계**: 본 스크립트 사용으로 인한 예약 실패나 기타 문제에 대해 개발자는 책임지지 않습니다

## 🔚 종료 및 정리

### 즉시 종료
- 실행 중인 터미널에서 `Ctrl+C` 입력

### 완전 정리 (2주 후)
```bash
# 작업 스케줄러에서 작업 삭제 (Windows)
# 또는 systemd 서비스 비활성화 (Linux)

# 프로젝트 폴더 삭제
rm -rf zeroworld-checker/

# 환경변수 제거 (필요시)
```

---

**Happy Booking! 🎮🎉** 