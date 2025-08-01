# 🎯 제로월드 예약 모니터링 시스템

제로월드 홍대점의 '층간소음' 테마 예약 가능 여부를 실시간으로 모니터링하고 텔레그램으로 알림을 보내는 시스템입니다.

## ✨ 주요 기능

- 🔄 **24시간 무제한 모니터링**: 1분 간격으로 예약 상태 체크
- 📱 **텔레그램 알림**: 예약 가능한 슬롯 발견 시 즉시 알림
- 🤖 **봇 명령어**: `/status`, `/help` 명령어로 상태 확인
- 📊 **실시간 상태 보고**: 매 정각 모니터링 상태 전송
- 🛡️ **안정성**: 에러 처리 및 자동 재시작 기능

## 🚀 Railway 배포

이 프로젝트는 Railway에서 24시간 무료로 호스팅할 수 있습니다.

### 환경변수 설정 (필수)

Railway 대시보드에서 다음 환경변수를 설정하세요:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
RAILWAY_ENVIRONMENT_NAME=production
```

### 텔레그램 봇 설정

1. 텔레그램에서 `@BotFather` 검색
2. `/newbot` 명령어로 새 봇 생성
3. 받은 토큰을 `TELEGRAM_BOT_TOKEN`에 설정
4. 봇과 대화 후 `https://api.telegram.org/bot<TOKEN>/getUpdates`에서 채팅 ID 확인

## 💻 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (Windows)
set TELEGRAM_BOT_TOKEN=your_token
set TELEGRAM_CHAT_ID=your_chat_id

# 실행
python -m checker.main
```

## 📊 모니터링

- **운영 시간**: 24시간 무제한
- **체크 간격**: 1분
- **대상 테마**: 층간소음
- **알림 방식**: 텔레그램 메시지

## 🔧 명령어

- `--test`: 시스템 테스트
- `--once`: 한 번만 체크
- `--config-test`: 설정 확인
- `--bot-test`: 봇 연결 테스트

## 📞 지원

문제가 발생하면 Railway 로그를 확인하고 GitHub Issues를 통해 문의하세요.