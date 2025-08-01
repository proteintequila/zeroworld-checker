"""
제로월드 예약 모니터링 시스템 설정 파일
"""

from pathlib import Path
import os
from datetime import datetime, timedelta

# 텔레그램 봇 설정 (환경변수에서 읽기)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID_STR = os.getenv("TELEGRAM_CHAT_ID", "0")
try:
    CHAT_ID = int(CHAT_ID_STR)
except ValueError:
    CHAT_ID = 0  # 기본값 (설정 필요함을 알림)

# 모니터링 대상 설정
THEME_NAME = "층간소음"

# 날짜 범위 설정 (현재 날짜 기준으로 동적 설정)
today = datetime.now().date()
DATE_START = today.strftime("%Y-%m-%d")  # 오늘부터
DATE_END = "2025-08-13"    # 홈페이지 확인된 마지막 날짜

# 시간 설정
TIMEZONE = "Asia/Seoul"
RUN_HOURS = range(0, 24)  # 24시간 무제한 모니터링
CHECK_INTERVAL_MINUTES = 1

# 파일 경로
# 클라우드 환경 감지
IS_CLOUD = os.getenv("RAILWAY_ENVIRONMENT_NAME") is not None or os.getenv("RENDER") is not None

if IS_CLOUD:
    # 클라우드 환경에서는 로그를 stdout으로 출력
    LOG_FILE = None  # stdout 사용
    # 상태 파일도 메모리 기반으로 변경 (옵션)
    STATE_FILE = Path("/tmp/state.json") if os.path.exists("/tmp") else Path("state.json")
else:
    # 로컬 환경
    STATE_FILE = Path("state.json")
    LOG_FILE = "checker.log"

# HTTP 요청 설정
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_TIMEOUT = 10

# 제로월드 URL 설정
BASE_URL = "https://zerohongdae.com"
RESERVATION_URL = f"{BASE_URL}/reservation"

# 로그 설정
LOG_LEVEL = "DEBUG"  # 디버깅을 위해 DEBUG 레벨로 변경
LOG_ROTATION = "1 MB"
LOG_RETENTION = "5 days"

# 알림 설정
MAX_NOTIFICATION_SLOTS = 10  # 한 번에 최대 알림 개수
NOTIFICATION_COOLDOWN = 300  # 연속 알림 방지 쿨타임 (초) 