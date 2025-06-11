#!/usr/bin/env python3
"""
Luma Events Viewer - 테스트용

Luma API를 사용해서 진행중/예정된 이벤트를 조회하는 간단한 스크립트입니다.
코드 이해를 위한 학습용 파일입니다.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class LumaEventsViewer:
    """Luma 이벤트 조회 클래스"""
    
    def __init__(self):
        # 환경변수에서 API 키 가져오기
        self.api_key = os.getenv('LUMA_API_KEY')
        if not self.api_key:
            raise ValueError("LUMA_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
        # API 기본 설정
        self.base_url = "https://api.lu.ma"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_all_events(self):
        """모든 이벤트 조회"""
        try:
            print("📡 모든 이벤트 조회 중...")
            response = requests.get(
                f"{self.base_url}/public/v1/event",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            events = data.get('entries', [])
            print(f"✅ 총 {len(events)}개의 이벤트를 찾았습니다.\n")
            return events
            
        except requests.RequestException as e:
            print(f"❌ API 요청 실패: {e}")
            return []
    
    def get_live_events(self):
        """현재 진행중인 이벤트만 조회"""
        try:
            print("🔴 진행중인 이벤트 조회 중...")
            response = requests.get(
                f"{self.base_url}/public/v1/event",
                headers=self.headers,
                params={"is_live": True}  # 진행중인 이벤트만
            )
            response.raise_for_status()
            data = response.json()
            
            events = data.get('entries', [])
            print(f"✅ 현재 진행중인 이벤트: {len(events)}개\n")
            return events
            
        except requests.RequestException as e:
            print(f"❌ API 요청 실패: {e}")
            return []
    
    def get_upcoming_events(self):
        """예정된 이벤트 조회"""
        try:
            print("⏰ 예정된 이벤트 조회 중...")
            response = requests.get(
                f"{self.base_url}/public/v1/event",
                headers=self.headers,
                params={"is_upcoming": True}  # 예정된 이벤트만
            )
            response.raise_for_status()
            data = response.json()
            
            events = data.get('entries', [])
            print(f"✅ 예정된 이벤트: {len(events)}개\n")
            return events
            
        except requests.RequestException as e:
            print(f"❌ API 요청 실패: {e}")
            return []
    
    def print_event_summary(self, events, title):
        """이벤트 요약 정보 출력"""
        if not events:
            print(f"📝 {title}: 이벤트가 없습니다.\n")
            return
        
        print(f"📝 {title}:")
        print("=" * 60)
        
        for i, event in enumerate(events, 1):
            name = event.get('name', '이름 없음')
            api_id = event.get('api_id', 'ID 없음')
            start_at = event.get('start_at', '')
            end_at = event.get('end_at', '')
            is_live = event.get('is_live', False)
            
            # 시간 포맷팅
            start_time = self.format_datetime(start_at)
            end_time = self.format_datetime(end_at)
            
            # 상태 표시
            status = "🔴 LIVE" if is_live else "⏰ 예정"
            
            print(f"{i}. {status} {name}")
            print(f"   📋 ID: {api_id}")
            print(f"   🕐 시작: {start_time}")
            print(f"   🕐 종료: {end_time}")
            print()
        
        print("=" * 60 + "\n")
    
    def format_datetime(self, datetime_str):
        """날짜/시간 포맷팅"""
        if not datetime_str:
            return "시간 정보 없음"
        
        try:
            # ISO 8601 형식 파싱
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            # 한국 시간으로 변환 (UTC+9)
            kst_time = dt + timedelta(hours=9)
            return kst_time.strftime('%Y-%m-%d %H:%M:%S KST')
        except:
            return datetime_str
    
    def get_event_details(self, event_api_id):
        """특정 이벤트의 상세 정보 조회"""
        try:
            print(f"🔍 이벤트 상세 정보 조회 중: {event_api_id}")
            response = requests.get(
                f"{self.base_url}/public/v1/event/{event_api_id}",
                headers=self.headers
            )
            response.raise_for_status()
            event = response.json()
            
            print("✅ 상세 정보를 가져왔습니다:")
            print(json.dumps(event, indent=2, ensure_ascii=False))
            return event
            
        except requests.RequestException as e:
            print(f"❌ 상세 정보 조회 실패: {e}")
            return None


def main():
    """메인 함수"""
    print("🎫 Luma Events Viewer 시작!")
    print("=" * 60)
    
    try:
        # 뷰어 초기화
        viewer = LumaEventsViewer()
        
        # 1. 모든 이벤트 조회
        all_events = viewer.get_all_events()
        viewer.print_event_summary(all_events, "전체 이벤트")
        
        # 2. 진행중인 이벤트만 조회
        live_events = viewer.get_live_events()
        viewer.print_event_summary(live_events, "진행중인 이벤트")
        
        # 3. 예정된 이벤트만 조회
        upcoming_events = viewer.get_upcoming_events()
        viewer.print_event_summary(upcoming_events, "예정된 이벤트")
        
        # 4. 진행중인 이벤트가 있으면 첫 번째 이벤트의 상세 정보 출력
        if live_events:
            print("🔍 첫 번째 진행중인 이벤트의 상세 정보:")
            print("=" * 60)
            first_event = live_events[0]
            viewer.get_event_details(first_event.get('api_id'))
        
        print("🎉 조회 완료!")
        
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류: {e}")


if __name__ == "__main__":
    main() 