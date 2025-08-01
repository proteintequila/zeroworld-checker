"""
제로월드 예약 정보 스크래핑 모듈

HTML 전체 파싱으로 숨겨진 예약 데이터와 API 데이터를 조합하여 정확한 예약 상태 확인
"""

import requests
import json
import datetime as dt
import time
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from loguru import logger

from .config import (
    BASE_URL, RESERVATION_URL, THEME_NAME,
    DATE_START, DATE_END, USER_AGENT, REQUEST_TIMEOUT
)


class ZeroworldFetcher:
    """제로월드 예약 정보 가져오기 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': BASE_URL,
            'Referer': RESERVATION_URL
        })
        
        # CSRF 토큰과 초기 HTML 가져오기
        self.csrf_token = None
        self._initialize_session()
    
    def _time_to_timestamp(self, date_str: str, time_str: str) -> int:
        """날짜와 시간을 타임스탬프로 변환"""
        try:
            datetime_str = f"{date_str} {time_str}"
            dt_obj = dt.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return int(dt_obj.timestamp())
        except Exception as e:
            logger.error(f"타임스탬프 변환 실패: {e}")
            return 0
    
    def _extract_hidden_data(self, html_content: str) -> Dict:
        """HTML에서 숨겨진 예약 데이터 추출"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            hidden_div = soup.find('div', id='reservationHiddenData')
            
            if hidden_div:
                hidden_text = hidden_div.get_text().strip()
                hidden_data = json.loads(hidden_text)
                logger.info(f"숨겨진 예약 데이터 추출 성공: {len(str(hidden_data))} 문자")
                return hidden_data
            else:
                logger.warning("reservationHiddenData를 찾을 수 없습니다")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"숨겨진 데이터 JSON 파싱 실패: {e}")
            return {}
        except Exception as e:
            logger.error(f"숨겨진 데이터 추출 실패: {e}")
            return {}
    
    def _is_really_available(self, theme_pk: int, time_str: str, date_str: str, 
                           hidden_data: Dict, api_reservation: bool) -> bool:
        """실제 예약 가능 여부 확인 (API + 숨겨진 데이터 조합)"""
        try:
            # 1. API에서 기본적으로 매진이라고 하면 매진
            if api_reservation:
                logger.debug(f"API에서 매진 처리: {date_str} {time_str}")
                return False
            
            # 2. 숨겨진 데이터에서 실제 예약 여부 확인
            timestamp = self._time_to_timestamp(date_str, time_str)
            theme_reservations = hidden_data.get('other', {}).get(str(theme_pk), {})
            
            # 숨겨진 데이터에 해당 타임스탬프가 있으면 예약됨
            is_really_reserved = str(timestamp) in theme_reservations
            
            # ⚠️ 추가 검증: 현재 시간보다 과거인 슬롯은 무조건 매진 처리
            from datetime import datetime
            try:
                slot_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                if slot_datetime < datetime.now():
                    logger.debug(f"과거 시간대로 매진 처리: {date_str} {time_str}")
                    return False
            except:
                pass
            
            # ⚠️ 거짓 양성 방지: 숨겨진 데이터가 없으면 API 결과만 사용
            if not hidden_data or not theme_reservations:
                logger.warning(f"숨겨진 데이터 없음 - API 결과만 사용: {date_str} {time_str}")
                return not api_reservation
            
            logger.debug(f"예약 상태 확인: {date_str} {time_str}")
            logger.debug(f"  - API reservation: {api_reservation}")
            logger.debug(f"  - 타임스탬프: {timestamp}")
            logger.debug(f"  - 숨겨진 데이터에서 예약됨: {is_really_reserved}")
            
            return not is_really_reserved
            
        except Exception as e:
            logger.error(f"예약 상태 확인 실패: {e}")
            # 오류 시 API 결과 사용 (보수적 접근)
            return not api_reservation
    
    def _initialize_session(self):
        """세션 초기화 및 CSRF 토큰 획득"""
        try:
            response = self.session.get(RESERVATION_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            csrf_input = soup.find('input', {'name': '_token'})
            
            if csrf_meta:
                self.csrf_token = csrf_meta.get('content')
                logger.info(f"CSRF 토큰 획득 성공 (meta): {self.csrf_token[:10]}...")
            elif csrf_input:
                self.csrf_token = csrf_input.get('value')
                logger.info(f"CSRF 토큰 획득 성공 (input): {self.csrf_token[:10]}...")
            else:
                logger.warning("CSRF 토큰을 찾을 수 없습니다")
                self.csrf_token = None
                
        except Exception as e:
            logger.error(f"세션 초기화 실패: {e}")
            self.csrf_token = None
    
    def get_theme_data(self, date: str) -> Optional[Tuple[Dict, Dict]]:
        """
        특정 날짜의 테마 정보와 숨겨진 예약 데이터 가져오기
        
        Args:
            date: YYYY-MM-DD 형식의 날짜
            
        Returns:
            (API 데이터, 숨겨진 데이터) 튜플 또는 None
        """
        try:
            if not self.csrf_token:
                logger.error("CSRF 토큰이 없습니다. 세션 재초기화...")
                self._initialize_session()
                if not self.csrf_token:
                    logger.error("CSRF 토큰을 가져올 수 없습니다")
                    return None
            
            # 1. HTML 페이지 전체 가져오기 (숨겨진 데이터 포함)
            logger.info(f"날짜 {date}의 HTML 페이지 가져오는 중...")
            
            # 예약 페이지에 날짜 파라미터 추가해서 접근
            page_url = f"{RESERVATION_URL}?date={date}"
            page_response = self.session.get(page_url, timeout=REQUEST_TIMEOUT)
            
            if page_response.status_code != 200:
                logger.error(f"HTML 페이지 가져오기 실패: {page_response.status_code}")
                return None
            
            # 2. 숨겨진 데이터 추출
            hidden_data = self._extract_hidden_data(page_response.text)
            
            # 3. API 데이터 가져오기
            logger.info(f"날짜 {date}의 API 데이터 가져오는 중...")
            
            api_url = f"{BASE_URL}/reservation/theme"
            
            # Ajax 요청용 헤더 설정
            ajax_headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-TOKEN': self.csrf_token,
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            }
            
            data = {
                'reservationDate': date,
                'name': '',
                'phone': '',
                'paymentType': '1'
            }
            
            api_response = self.session.post(
                api_url, 
                data=data, 
                headers=ajax_headers,
                timeout=REQUEST_TIMEOUT
            )
            
            logger.info(f"API 요청: {api_url}, 날짜: {date}")
            logger.info(f"API 응답 상태: {api_response.status_code}")
            
            if api_response.status_code == 200:
                try:
                    api_data = api_response.json()
                    logger.info(f"API 응답 성공: {len(str(api_data))} 문자")
                    
                    # API 데이터와 숨겨진 데이터 모두 반환
                    return (api_data, hidden_data)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"API JSON 파싱 오류: {e}")
                    logger.debug(f"API 응답 내용: {api_response.text[:500]}")
                    return None
            else:
                logger.error(f"API 호출 실패: {api_response.status_code}")
                logger.debug(f"API 응답 내용: {api_response.text[:500]}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return None
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            return None
    
    def extract_slots_from_data(self, api_data: Dict, hidden_data: Dict, 
                               target_date: str) -> Dict[str, str]:
        """
        API 응답과 숨겨진 데이터를 조합하여 실제 슬롯 정보 추출
        
        Args:
            api_data: API 응답 데이터
            hidden_data: HTML에서 추출한 숨겨진 예약 데이터
            target_date: 대상 날짜
            
        Returns:
            슬롯 정보 딕셔너리 {"2025-01-29 18:30": "예약가능"}
        """
        slots = {}
        
        try:
            # API 응답 구조 분석
            if 'data' in api_data:
                # 테마 목록에서 지정된 테마 찾기
                theme_pk = None
                for theme in api_data.get('data', []):
                    if THEME_NAME in theme.get('title', ''):
                        theme_pk = theme.get('PK')
                        logger.info(f"'{THEME_NAME}' 테마 발견: PK={theme_pk}")
                        break
                
                if theme_pk and 'times' in api_data:
                    # 해당 테마의 시간 슬롯 정보 가져오기
                    theme_times = api_data['times'].get(str(theme_pk), [])
                    
                    logger.debug(f"=== {target_date} {THEME_NAME} 테마 슬롯 처리 ===")
                    logger.debug(f"총 슬롯 수: {len(theme_times)}")
                    logger.debug(f"숨겨진 데이터 키: {list(hidden_data.keys())}")
                    
                    for i, time_slot in enumerate(theme_times):
                        time_str = time_slot.get('time', '')
                        api_reservation = time_slot.get('reservation', False)
                        
                        if time_str:
                            slot_key = f"{target_date} {time_str}"
                            
                            # **핵심 로직**: API 데이터와 숨겨진 데이터 조합
                            is_available = self._is_really_available(
                                theme_pk, time_str, target_date, 
                                hidden_data, api_reservation
                            )
                            
                            slot_status = "예약가능" if is_available else "매진"
                            slots[slot_key] = slot_status
                            
                            logger.debug(f"  슬롯 {i+1}: {time_str} = {slot_status}")
                            
                    logger.info(f"'{THEME_NAME}' 슬롯 {len(slots)}개 추출 완료")
                else:
                    logger.warning(f"'{THEME_NAME}' 테마를 찾을 수 없습니다")
            
        except Exception as e:
            logger.error(f"슬롯 추출 중 오류: {e}")
            
        return slots


def get_slots(exclude_past_slots: bool = True) -> Dict[str, str]:
    """
    날짜 범위 내 지정된 테마의 모든 슬롯 상태 반환 (숨겨진 데이터 포함)
    
    Args:
        exclude_past_slots: True면 현재 시간보다 과거인 슬롯 제외
    
    Returns:
        dict: {"2025-01-29 18:30": "예약가능", ...}
    """
    fetcher = ZeroworldFetcher()
    all_slots = {}
    
    # 현재 시간 (시간 필터링용)
    now = dt.datetime.now()
    logger.info(f"현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 날짜 범위 생성
    start_date = dt.datetime.strptime(DATE_START, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(DATE_END, "%Y-%m-%d").date()
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        logger.info(f"날짜 {date_str} 처리 중...")
        
        # 해당 날짜의 테마 데이터와 숨겨진 데이터 가져오기
        result = fetcher.get_theme_data(date_str)
        
        if result:
            api_data, hidden_data = result
            # 슬롯 정보 추출 (API + 숨겨진 데이터 조합)
            date_slots = fetcher.extract_slots_from_data(api_data, hidden_data, date_str)
            
            # 시간 필터링 적용
            if exclude_past_slots:
                filtered_slots = {}
                filtered_count = 0
                
                for slot_key, slot_status in date_slots.items():
                    try:
                        # 슬롯 시간 파싱
                        slot_datetime = dt.datetime.strptime(slot_key, "%Y-%m-%d %H:%M:%S")
                        
                        # 현재 시간보다 미래인 슬롯만 포함
                        if slot_datetime > now:
                            filtered_slots[slot_key] = slot_status
                        else:
                            filtered_count += 1
                            logger.debug(f"과거 슬롯 제외: {slot_key}")
                            
                    except ValueError as e:
                        logger.warning(f"슬롯 시간 파싱 실패: {slot_key}, 오류: {e}")
                        # 파싱 실패시 포함 (안전장치)
                        filtered_slots[slot_key] = slot_status
                
                if filtered_count > 0:
                    logger.info(f"날짜 {date_str}: {filtered_count}개 과거 슬롯 제외됨")
                
                all_slots.update(filtered_slots)
            else:
                all_slots.update(date_slots)
        else:
            logger.warning(f"날짜 {date_str}의 데이터를 가져올 수 없습니다")
        
        current_date += dt.timedelta(days=1)
    
    total_slots = len(all_slots)
    available_slots = len([s for s in all_slots.values() if s == "예약가능"])
    
    logger.info(f"총 {total_slots}개 슬롯 정보 수집 완료 (예약가능: {available_slots}개)")
    if exclude_past_slots:
        logger.info("⏰ 과거 슬롯 제외 필터링 적용됨")
    
    return all_slots


if __name__ == "__main__":
    # 테스트 실행
    logger.info("제로월드 예약 정보 스크래핑 테스트 시작 (숨겨진 데이터 포함)")
    
    # 테스트 날짜 (NOX 문제가 있던 7월 31일)
    test_date = "2025-07-31"
    fetcher = ZeroworldFetcher()
    
    # 1. 단일 날짜 테스트
    logger.info(f"=== {test_date} 날짜 테스트 ===")
    result = fetcher.get_theme_data(test_date)
    
    if result:
        api_data, hidden_data = result
        print(f"✅ 데이터 가져오기 성공!")
        print(f"API 응답 키: {list(api_data.keys())}")
        print(f"숨겨진 데이터 키: {list(hidden_data.keys())}")
        
        # API 데이터 구조 확인
        if 'data' in api_data:
            print(f"테마 개수: {len(api_data['data'])}")
            for theme in api_data['data'][:3]:  # 처음 3개만 출력
                print(f"  - {theme.get('title', 'N/A')} (PK: {theme.get('PK', 'N/A')})")
        
        if 'times' in api_data:
            print(f"시간 슬롯 테마 개수: {len(api_data['times'])}")
        
        # 숨겨진 데이터 구조 확인
        if 'other' in hidden_data:
            print(f"숨겨진 예약 데이터 테마 개수: {len(hidden_data['other'])}")
            for theme_pk, reservations in hidden_data['other'].items():
                print(f"  - 테마 PK {theme_pk}: {len(reservations)}개 예약")
        
        # 테마 슬롯 추출 테스트 (실제 예약 상태 포함)
        slots = fetcher.extract_slots_from_data(api_data, hidden_data, test_date)
        print(f"\n'{THEME_NAME}' 슬롯: {len(slots)}개")
        
        available_count = 0
        for slot_time, status in slots.items():
            print(f"  - {slot_time}: {status}")
            if status == "예약가능":
                available_count += 1
        
        print(f"예약 가능한 슬롯: {available_count}개")
        
    else:
        print("❌ 데이터 가져오기 실패")
    
    # 2. 전체 범위 테스트 (간단히)
    print("\n=== 전체 범위 테스트 ===")
    all_slots = get_slots()
    print(f"전체 수집된 슬롯: {len(all_slots)}개")
    
    # 예약 가능한 슬롯만 출력
    available_slots = {k: v for k, v in all_slots.items() if v == "예약가능"}
    print(f"예약 가능한 슬롯: {len(available_slots)}개")
    
    for slot_time in list(available_slots.keys())[:5]:  # 처음 5개만 출력
        print(f"  - {slot_time}") 