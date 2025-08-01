#!/usr/bin/env python3
"""로직 테스트"""

from checker.fetch import ZeroworldFetcher

def test_19_slot():
    fetcher = ZeroworldFetcher()
    result = fetcher.get_theme_data('2025-08-02')
    
    if not result:
        print("❌ 데이터 없음")
        return
    
    api_data, hidden_data = result
    
    # 층간소음 테마 정보
    theme_pk = 61
    time_str = "19:00:00"
    date_str = "2025-08-02"
    api_reservation = False  # API에서 온 값
    
    print("=== 🔍 19:00 슬롯 로직 테스트 ===")
    print(f"테마 PK: {theme_pk}")
    print(f"시간: {time_str}")
    print(f"날짜: {date_str}")
    print(f"API reservation: {api_reservation}")
    
    # 우리 로직 실행
    is_available = fetcher._is_really_available(
        theme_pk, time_str, date_str, 
        hidden_data, api_reservation
    )
    
    print(f"\n💡 우리 로직 결과: {is_available}")
    print(f"상태: {'예약가능' if is_available else '매진'}")
    
    # 디버깅 정보
    timestamp = fetcher._time_to_timestamp(date_str, time_str)
    theme_reservations = hidden_data.get('other', {}).get(str(theme_pk), {})
    
    print(f"\n🔧 디버깅 정보:")
    print(f"타임스탬프: {timestamp}")
    print(f"숨겨진 데이터 키들: {list(theme_reservations.keys())}")
    print(f"타임스탬프 문자열: '{str(timestamp)}'")
    print(f"숨겨진 데이터에 존재: {str(timestamp) in theme_reservations}")
    
    if str(timestamp) in theme_reservations:
        value = theme_reservations[str(timestamp)]
        print(f"해당 값: {value} (타입: {type(value)})")

if __name__ == "__main__":
    test_19_slot()