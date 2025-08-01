#!/usr/bin/env python3
"""임시 디버깅 스크립트"""

from checker.fetch import ZeroworldFetcher
import json

def main():
    fetcher = ZeroworldFetcher()
    result = fetcher.get_theme_data('2025-08-02')
    
    if not result:
        print("❌ 데이터를 가져올 수 없습니다")
        return
    
    api_data, hidden_data = result
    
    # 1. 테마 목록 확인
    print("=== 📋 전체 테마 목록 ===")
    for theme in api_data.get('data', []):
        title = theme.get('title', '')
        pk = theme.get('PK')
        print(f"- {title}: PK={pk}")
        if '층간' in title or '소음' in title:
            print(f"  🎯 타겟 테마 발견!")
    
    # 2. 층간소음 테마 시간 슬롯 확인
    print("\n=== ⏰ 층간소음 테마 시간 슬롯 ===")
    found_theme = False
    
    for theme_pk, times in api_data.get('times', {}).items():
        theme_info = next((t for t in api_data.get('data', []) if str(t.get('PK')) == theme_pk), None)
        if theme_info:
            title = theme_info.get('title', '')
            if '층간' in title or '소음' in title:
                found_theme = True
                print(f"테마 PK {theme_pk}: {title}")
                print(f"총 {len(times)}개 슬롯:")
                
                for i, slot in enumerate(times, 1):
                    time_str = slot.get('time')
                    reservation = slot.get('reservation')
                    status = "매진" if reservation else "예약가능"
                    print(f"  {i}. {time_str}: reservation={reservation} → {status}")
                    
                    # 19:00 슬롯 특별 체크
                    if time_str and "19:00" in time_str:
                        print(f"    🚨 19:00 슬롯 발견! reservation={reservation}")
    
    if not found_theme:
        print("❌ 층간소음 테마를 찾을 수 없습니다")
    
    # 3. 숨겨진 데이터에서 층간소음 관련 확인
    print("\n=== 🔍 숨겨진 예약 데이터 ===")
    other_data = hidden_data.get('other', {})
    
    if other_data:
        print(f"숨겨진 데이터 테마 개수: {len(other_data)}")
        for theme_pk, reservations in other_data.items():
            theme_info = next((t for t in api_data.get('data', []) if str(t.get('PK')) == theme_pk), None)
            if theme_info:
                title = theme_info.get('title', '')
                if '층간' in title or '소음' in title:
                    print(f"테마 PK {theme_pk} ({title}): {len(reservations)}개 예약")
                    for timestamp, reserved in reservations.items():
                        print(f"  - {timestamp}: {reserved}")
    else:
        print("숨겨진 예약 데이터가 없습니다")

if __name__ == "__main__":
    main()