#!/usr/bin/env python3
"""
제로월드 예약 모니터링 시스템 설정 도우미

텔레그램 봇 토큰과 채팅 ID를 쉽게 설정할 수 있도록 도와주는 스크립트
"""

import os
import sys
import platform
from pathlib import Path

def main():
    """메인 설정 프로세스"""
    print("🎯 제로월드 예약 모니터링 시스템 설정 도우미")
    print("=" * 50)
    
    # 1. 텔레그램 봇 토큰 입력
    print("\n📱 텔레그램 봇 설정")
    print("1. @BotFather에게 /newbot 명령어로 봇을 생성하세요.")
    print("2. 발급받은 토큰을 아래에 입력하세요.")
    
    while True:
        bot_token = input("\n🤖 봇 토큰을 입력하세요: ").strip()
        if bot_token and ':' in bot_token:
            break
        print("❌ 올바른 형식이 아닙니다. (예: 1234567890:ABC-DEF...)")
    
    # 2. 채팅 ID 입력
    print("\n💬 채팅 ID 설정")
    print("1. 생성한 봇과 대화를 시작하세요 (메시지 하나 전송)")
    print("2. @userinfobot에게 /start를 전송하여 Your user ID를 확인하세요.")
    
    while True:
        try:
            chat_id = input("\n👤 채팅 ID를 입력하세요: ").strip()
            int(chat_id)  # 숫자인지 확인
            break
        except ValueError:
            print("❌ 숫자만 입력해주세요.")
    
    # 3. 환경변수 설정
    print("\n🔧 환경변수 설정 중...")
    
    system = platform.system().lower()
    
    if system == "windows":
        setup_windows_env(bot_token, chat_id)
    else:
        setup_unix_env(bot_token, chat_id)
    
    # 4. 설정 확인
    print("\n✅ 설정 완료!")
    print("\n🧪 설정 테스트를 실행해보세요:")
    print("   python -m checker.main --test")
    print("\n🚀 모니터링을 시작하려면:")
    print("   python -m checker.main")

def setup_windows_env(bot_token: str, chat_id: str):
    """Windows 환경변수 설정"""
    try:
        # PowerShell 명령어 생성
        ps_commands = [
            f'[Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "{bot_token}", "User")',
            f'[Environment]::SetEnvironmentVariable("TELEGRAM_CHAT_ID", "{chat_id}", "User")'
        ]
        
        for cmd in ps_commands:
            os.system(f'powershell -Command "{cmd}"')
        
        # 현재 세션에도 설정
        os.environ["TELEGRAM_BOT_TOKEN"] = bot_token
        os.environ["TELEGRAM_CHAT_ID"] = chat_id
        
        print("✅ Windows 환경변수가 설정되었습니다.")
        print("💡 새 PowerShell 창에서는 자동으로 적용됩니다.")
        
    except Exception as e:
        print(f"❌ 자동 설정 실패: {e}")
        print("\n수동으로 PowerShell에서 실행하세요:")
        print(f'$env:TELEGRAM_BOT_TOKEN="{bot_token}"')
        print(f'$env:TELEGRAM_CHAT_ID="{chat_id}"')

def setup_unix_env(bot_token: str, chat_id: str):
    """Linux/Mac 환경변수 설정"""
    shell_files = ["~/.bashrc", "~/.zshrc", "~/.profile"]
    
    for shell_file in shell_files:
        file_path = Path(shell_file).expanduser()
        if file_path.exists():
            try:
                with open(file_path, 'a') as f:
                    f.write(f'\n# 제로월드 예약 모니터링 시스템\n')
                    f.write(f'export TELEGRAM_BOT_TOKEN="{bot_token}"\n')
                    f.write(f'export TELEGRAM_CHAT_ID="{chat_id}"\n')
                
                print(f"✅ {shell_file}에 환경변수가 추가되었습니다.")
                break
            except Exception as e:
                print(f"❌ {shell_file} 설정 실패: {e}")
    
    # 현재 세션에도 설정
    os.environ["TELEGRAM_BOT_TOKEN"] = bot_token
    os.environ["TELEGRAM_CHAT_ID"] = chat_id
    
    print("💡 새 터미널에서는 자동으로 적용됩니다.")
    print("📝 현재 터미널에서 즉시 적용하려면:")
    print(f'export TELEGRAM_BOT_TOKEN="{bot_token}"')
    print(f'export TELEGRAM_CHAT_ID="{chat_id}"')

if __name__ == "__main__":
    main() 