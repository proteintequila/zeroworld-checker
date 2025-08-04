#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main 브랜치 설정 스크립트 (층간소음 테마)
"""

import os
import re

def update_config_for_main():
    """main 브랜치용 config.py 설정"""
    config_path = "checker/config.py"
    
    try:
        # config.py 파일 읽기
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 테마 이름을 층간소음으로 변경
        pattern = r'THEME_NAME = ".*?"'
        replacement = 'THEME_NAME = "층간소음"'
        
        updated_content = re.sub(pattern, replacement, content)
        
        # 파일에 다시 쓰기
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ main 브랜치: 층간소음 테마로 설정 완료")
        
    except Exception as e:
        print(f"❌ config.py 업데이트 실패: {e}")

if __name__ == "__main__":
    print("🎯 main 브랜치 설정 (층간소음 테마)")
    update_config_for_main()