"""
로컬 상태 관리 모듈

이전 예약 슬롯 상태를 state.json 파일에 저장하고 읽어와서
변경 사항을 감지하는 기능 제공
"""

import json
import threading
from typing import Dict, Any, List
from pathlib import Path
from loguru import logger

from .config import STATE_FILE


class StateManager:
    """상태 관리 클래스"""
    
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = Path(state_file)
        self._lock = threading.Lock()
        self._ensure_state_file_exists()
    
    def _ensure_state_file_exists(self):
        """상태 파일이 없으면 빈 파일 생성"""
        if not self.state_file.exists():
            self.save({})
            logger.info(f"새로운 상태 파일 생성: {self.state_file}")
    
    def load(self) -> Dict[str, Any]:
        """
        상태 파일에서 데이터 로드
        
        Returns:
            dict: 저장된 상태 데이터
        """
        with self._lock:
            try:
                if not self.state_file.exists():
                    logger.warning(f"상태 파일이 존재하지 않음: {self.state_file}")
                    return {}
                
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                logger.debug(f"상태 파일 로드 완료: {len(data)}개 항목")
                return data
                
            except json.JSONDecodeError as e:
                logger.error(f"상태 파일 JSON 파싱 오류: {e}")
                # 백업 파일 생성 후 초기화
                self._backup_corrupted_file()
                return {}
            except Exception as e:
                logger.error(f"상태 파일 로드 오류: {e}")
                return {}
    
    def save(self, state: Dict[str, Any]) -> bool:
        """
        상태 데이터를 파일에 저장
        
        Args:
            state: 저장할 상태 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        with self._lock:
            try:
                # 임시 파일에 먼저 저장 후 원자적 이동
                temp_file = self.state_file.with_suffix('.tmp')
                
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                
                # 원자적 이동 (Windows에서는 기존 파일 삭제 후 이동)
                if self.state_file.exists():
                    self.state_file.unlink()
                temp_file.replace(self.state_file)
                
                logger.debug(f"상태 파일 저장 완료: {len(state)}개 항목")
                return True
                
            except Exception as e:
                logger.error(f"상태 파일 저장 오류: {e}")
                return False
    
    def _backup_corrupted_file(self):
        """손상된 상태 파일 백업"""
        try:
            if self.state_file.exists():
                backup_file = self.state_file.with_suffix('.backup')
                self.state_file.replace(backup_file)
                logger.info(f"손상된 상태 파일을 백업: {backup_file}")
        except Exception as e:
            logger.error(f"상태 파일 백업 실패: {e}")
    
    def get_previous_slots(self) -> Dict[str, str]:
        """
        이전에 저장된 슬롯 상태 가져오기
        
        Returns:
            dict: 이전 슬롯 상태
        """
        state = self.load()
        return state.get('slots', {})
    
    def update_slots(self, new_slots: Dict[str, str]) -> bool:
        """
        슬롯 상태 업데이트
        
        Args:
            new_slots: 새로운 슬롯 상태
            
        Returns:
            bool: 업데이트 성공 여부
        """
        state = self.load()
        state['slots'] = new_slots
        state['last_updated'] = str(pd_timestamp_now())
        return self.save(state)
    
    def find_new_available_slots(self, current_slots: Dict[str, str]) -> List[str]:
        """
        새로 예약 가능해진 슬롯 찾기
        
        Args:
            current_slots: 현재 슬롯 상태
            
        Returns:
            list: 새로 예약 가능해진 슬롯 시간 리스트
        """
        previous_slots = self.get_previous_slots()
        new_available = []
        
        for slot_time, current_status in current_slots.items():
            # 현재 예약 가능한 슬롯 중에서
            if current_status == "예약가능":
                previous_status = previous_slots.get(slot_time)
                
                # 이전에 없었거나 이전에 매진이었던 슬롯
                if previous_status != "예약가능":
                    new_available.append(slot_time)
        
        logger.info(f"새로 예약 가능한 슬롯: {len(new_available)}개")
        return new_available
    
    def get_stats(self) -> Dict[str, Any]:
        """
        상태 파일 통계 정보
        
        Returns:
            dict: 통계 정보
        """
        state = self.load()
        slots = state.get('slots', {})
        
        stats = {
            'total_slots': len(slots),
            'available_slots': len([s for s in slots.values() if s == "예약가능"]),
            'reserved_slots': len([s for s in slots.values() if s == "매진"]),
            'last_updated': state.get('last_updated', 'N/A'),
            'file_size': self.state_file.stat().st_size if self.state_file.exists() else 0
        }
        
        return stats


def pd_timestamp_now():
    """현재 시간 문자열 반환 (datetime 대신 사용)"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# 전역 상태 관리자
_state_manager = None


def get_state_manager() -> StateManager:
    """전역 상태 관리자 반환"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


# 편의 함수들
def load_state() -> Dict[str, Any]:
    """상태 로드 (편의 함수)"""
    return get_state_manager().load()


def save_state(state: Dict[str, Any]) -> bool:
    """상태 저장 (편의 함수)"""
    return get_state_manager().save(state)


def get_previous_slots() -> Dict[str, str]:
    """이전 슬롯 상태 가져오기 (편의 함수)"""
    return get_state_manager().get_previous_slots()


def update_slots(new_slots: Dict[str, str]) -> bool:
    """슬롯 상태 업데이트 (편의 함수)"""
    return get_state_manager().update_slots(new_slots)


def find_new_available_slots(current_slots: Dict[str, str]) -> List[str]:
    """새로 예약 가능한 슬롯 찾기 (편의 함수)"""
    return get_state_manager().find_new_available_slots(current_slots)


if __name__ == "__main__":
    # 테스트 실행
    logger.info("상태 관리 모듈 테스트 시작")
    
    # 1. 상태 관리자 생성
    print("=== 상태 관리자 테스트 ===")
    manager = StateManager()
    
    # 2. 초기 상태 확인
    initial_state = manager.load()
    print(f"초기 상태: {initial_state}")
    
    # 3. 테스트 슬롯 데이터
    test_slots_1 = {
        "2025-01-30 18:30:00": "매진",
        "2025-01-30 20:00:00": "예약가능",
        "2025-01-31 14:20:00": "매진"
    }
    
    test_slots_2 = {
        "2025-01-30 18:30:00": "예약가능",  # 매진 -> 예약가능
        "2025-01-30 20:00:00": "예약가능",  # 계속 예약가능
        "2025-01-31 14:20:00": "매진",      # 계속 매진
        "2025-01-31 16:00:00": "예약가능"   # 새로운 슬롯
    }
    
    # 4. 첫 번째 상태 저장
    print("\n=== 첫 번째 상태 저장 ===")
    if manager.update_slots(test_slots_1):
        print("✅ 첫 번째 상태 저장 성공")
        print(f"저장된 슬롯: {len(test_slots_1)}개")
    else:
        print("❌ 첫 번째 상태 저장 실패")
    
    # 5. 두 번째 상태에서 새로운 슬롯 찾기
    print("\n=== 새로운 슬롯 감지 테스트 ===")
    new_slots = manager.find_new_available_slots(test_slots_2)
    print(f"새로 예약 가능한 슬롯: {len(new_slots)}개")
    for slot in new_slots:
        print(f"  - {slot}")
    
    # 예상 결과: "2025-01-30 18:30:00"와 "2025-01-31 16:00:00"
    expected = ["2025-01-30 18:30:00", "2025-01-31 16:00:00"]
    if set(new_slots) == set(expected):
        print("✅ 새로운 슬롯 감지 정확")
    else:
        print(f"❌ 새로운 슬롯 감지 오류. 예상: {expected}, 실제: {new_slots}")
    
    # 6. 두 번째 상태 저장
    print("\n=== 두 번째 상태 저장 ===")
    if manager.update_slots(test_slots_2):
        print("✅ 두 번째 상태 저장 성공")
    
    # 7. 통계 정보 확인
    print("\n=== 통계 정보 ===")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n=== 테스트 완료 ===") 