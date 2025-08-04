#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTF-8 인코딩 설정 스크립트
Git, Railway, 프로젝트 전체에서 한글이 올바르게 표시되도록 설정
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_git_utf8():
    """Git UTF-8 설정"""
    print("🔧 Git UTF-8 설정 중...")
    
    git_commands = [
        ["git", "config", "--global", "core.quotepath", "false"],
        ["git", "config", "--global", "i18n.commitencoding", "utf-8"],
        ["git", "config", "--global", "i18n.logoutputencoding", "utf-8"],
        ["git", "config", "--global", "gui.encoding", "utf-8"],
        ["git", "config", "--global", "core.precomposeunicode", "true"]
    ]
    
    for cmd in git_commands:
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ {' '.join(cmd[2:])}")
        except subprocess.CalledProcessError as e:
            print(f"❌ {' '.join(cmd)}: {e}")

def setup_python_utf8():
    """Python 파일들 UTF-8 인코딩 확인"""
    print("\n📝 Python 파일 UTF-8 헤더 확인 중...")
    
    python_files = list(Path(".").rglob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # UTF-8 BOM 제거 (있다면)
            if content.startswith('\ufeff'):
                content = content[1:]
                
            # UTF-8 인코딩 헤더 추가 (없다면)
            lines = content.split('\n')
            has_encoding = any('coding' in line or 'encoding' in line for line in lines[:3])
            
            if not has_encoding and not py_file.name.startswith('__'):
                # 첫 번째 줄이 shebang이면 두 번째에, 아니면 첫 번째에 추가
                if lines[0].startswith('#!'):
                    lines.insert(1, '# -*- coding: utf-8 -*-')
                else:
                    lines.insert(0, '# -*- coding: utf-8 -*-')
                
                new_content = '\n'.join(lines)
                
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ {py_file}: UTF-8 헤더 추가")
            else:
                print(f"✅ {py_file}: UTF-8 인코딩 확인")
                
        except Exception as e:
            print(f"❌ {py_file}: {e}")

def setup_railway_utf8():
    """Railway 환경변수 UTF-8 설정"""
    print("\n🚂 Railway UTF-8 환경변수 확인...")
    
    env_vars = {
        'LANG': 'ko_KR.UTF-8',
        'LC_ALL': 'ko_KR.UTF-8',
        'PYTHONIOENCODING': 'utf-8'
    }
    
    print("Railway 대시보드 → Variables에 다음 환경변수 추가 권장:")
    for key, value in env_vars.items():
        print(f"  {key}={value}")

def setup_windows_utf8():
    """Windows 콘솔 UTF-8 설정"""
    if os.name == 'nt':  # Windows
        print("\n🪟 Windows UTF-8 설정 중...")
        try:
            # Windows 콘솔 코드페이지를 UTF-8로 설정
            subprocess.run(['chcp', '65001'], shell=True, check=True)
            print("✅ Windows 콘솔 UTF-8 설정 완료")
        except:
            print("⚠️ Windows 콘솔 UTF-8 설정 실패 (관리자 권한 필요할 수 있음)")

def main():
    """메인 실행 함수"""
    print("🌍 UTF-8 인코딩 설정 시작")
    print("=" * 50)
    
    setup_git_utf8()
    setup_python_utf8()
    setup_railway_utf8()
    setup_windows_utf8()
    
    print("\n" + "=" * 50)
    print("✅ UTF-8 설정 완료!")
    print("\n💡 다음 단계:")
    print("1. git add . && git commit -m '한글 UTF-8 인코딩 설정'")
    print("2. Railway Variables에 환경변수 추가")
    print("3. 터미널 재시작 후 한글 표시 확인")

if __name__ == "__main__":
    main()