# 🚀 Railway 배포 가이드

제로월드 예약 모니터링 시스템을 Railway에서 24시간 무료 호스팅하는 방법입니다.

## 📋 사전 준비

1. **GitHub 계정** (프로젝트 업로드용)
2. **Railway 계정** (GitHub로 가입 권장)
3. **텔레그램 봇 토큰** 및 **채팅 ID**

## 🔧 배포 단계

### 1단계: GitHub 저장소 생성

1. [GitHub](https://github.com)에서 새 저장소 생성
2. 프로젝트 파일들을 저장소에 업로드

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 2단계: Railway 계정 생성 및 프로젝트 연결

1. [Railway](https://railway.app) 접속
2. **"Login with GitHub"**로 가입
3. **"New Project"** 클릭
4. **"Deploy from GitHub repo"** 선택
5. 방금 만든 저장소 선택

### 3단계: 환경변수 설정 ⚠️ **매우 중요!**

Railway 대시보드에서 환경변수를 설정해야 합니다:

#### 필수 환경변수:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
RAILWAY_ENVIRONMENT_NAME=production
```

#### 텔레그램 봇 토큰 얻는 방법:
1. 텔레그램에서 `@BotFather` 검색
2. `/newbot` 명령어 입력
3. 봇 이름과 사용자명 설정
4. 받은 토큰을 `TELEGRAM_BOT_TOKEN`에 입력

#### 채팅 ID 얻는 방법:
1. 봇과 대화 시작 (아무 메시지나 전송)
2. 브라우저에서 아래 URL 방문:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```
3. 결과에서 `"chat":{"id":숫자}` 부분의 숫자가 채팅 ID

### 4단계: 배포 확인

1. Railway에서 자동 배포 시작
2. **Deployments** 탭에서 로그 확인
3. 성공하면 텔레그램으로 시작 알림 수신

## 📊 모니터링 및 관리

### 로그 확인
- Railway 대시보드 → **Deployments** → 최신 배포 클릭 → **View Logs**

### 텔레그램 명령어
- `/status` - 현재 상태 확인
- `/help` - 도움말

### 재시작
- Railway 대시보드에서 **Redeploy** 클릭

## 💰 비용 정보

- **무료 한도**: 월 500시간 (충분함)
- **사용량 확인**: Railway 대시보드에서 실시간 확인 가능
- **업그레이드**: 필요시 월 $5 플랜으로 업그레이드

## ⚠️ 주의사항

1. **환경변수를 반드시 설정**하세요 (봇이 작동하지 않습니다)
2. **GitHub 저장소는 Public**으로 설정해도 됩니다 (민감한 정보는 환경변수로 분리됨)
3. **Railway는 30일 비활성화시 프로젝트 삭제**하므로 정기적으로 확인하세요

## 🆘 문제 해결

### 1. 배포 실패시
- Railway 로그에서 오류 메시지 확인
- requirements.txt 의존성 문제인 경우가 많음

### 2. 텔레그램 알림이 안 올 때
- 환경변수 설정 확인
- 봇 토큰과 채팅 ID 재확인

### 3. 모니터링이 중단될 때
- Railway 대시보드에서 "Restart" 클릭
- 로그를 확인하여 원인 파악

## 📞 지원

문제가 생기면 Railway 로그를 확인하고, 필요시 GitHub Issues를 통해 문의하세요.