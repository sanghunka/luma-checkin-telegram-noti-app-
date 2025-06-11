#!/usr/bin/env python3
"""
Luma API 실제 작동 테스트

성공한 API 엔드포인트를 사용해서 이벤트와 체크인 정보를 테스트합니다.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class LumaAPITester:
    """Luma API 테스터 클래스"""
    
    def __init__(self):
        self.api_key = os.getenv('LUMA_API_KEY')
        if not self.api_key:
            raise ValueError("LUMA_API_KEY가 설정되지 않았습니다.")
        
        self.base_url = "https://api.lu.ma"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_all_events(self):
        """모든 이벤트 목록 조회"""
        try:
            print("🔍 모든 이벤트 조회 중...")
            url = f"{self.base_url}/public/v1/calendar/list-events"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            entries = data.get('entries', [])
            
            print(f"✅ 총 {len(entries)}개의 이벤트를 찾았습니다.")
            return entries
            
        except requests.RequestException as e:
            print(f"❌ 이벤트 조회 실패: {e}")
            return []
    
    def get_event_guests(self, event_api_id):
        """특정 이벤트의 참석자 목록 조회"""
        try:
            print(f"👥 이벤트 {event_api_id}의 참석자 조회 중...")
            url = f"{self.base_url}/public/v1/event/get-guests"
            
            # 다양한 방법으로 시도
            methods = [
                {"params": {"api_id": event_api_id}},
                {"params": {"event_id": event_api_id}},
                {"json": {"api_id": event_api_id}},
            ]
            
            for method in methods:
                try:
                    if 'params' in method:
                        response = requests.get(url, headers=self.headers, params=method['params'])
                    else:
                        response = requests.post(url, headers=self.headers, json=method['json'])
                    
                    if response.status_code == 200:
                        data = response.json()
                        guests = data.get('entries', [])
                        print(f"✅ {len(guests)}명의 참석자를 찾았습니다.")
                        return guests
                    else:
                        print(f"⚠️  방법 실패 ({response.status_code}): {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"⚠️  방법 오류: {e}")
                    continue
            
            print("❌ 모든 방법이 실패했습니다.")
            return []
            
        except Exception as e:
            print(f"❌ 참석자 조회 실패: {e}")
            return []
    
    def print_event_details(self, events):
        """이벤트 상세 정보 출력"""
        if not events:
            print("📝 출력할 이벤트가 없습니다.")
            return
        
        print("\n" + "=" * 80)
        print("📅 이벤트 목록")
        print("=" * 80)
        
        for i, entry in enumerate(events, 1):
            event = entry.get('event', {})
            
            name = event.get('name', '이름 없음')
            api_id = event.get('api_id', 'ID 없음')
            start_at = event.get('start_at', '')
            end_at = event.get('end_at', '')
            description = event.get('description', '')
            cover_url = event.get('cover_url', '')
            
            # 시간 포맷팅
            start_time = self.format_datetime(start_at)
            end_time = self.format_datetime(end_at)
            
            # 현재 상태 판단
            status = self.get_event_status(start_at, end_at)
            
            print(f"{i}. {status} {name}")
            print(f"   📋 ID: {api_id}")
            print(f"   🕐 시작: {start_time}")
            print(f"   🕐 종료: {end_time}")
            
            if description:
                desc_short = description[:100] + "..." if len(description) > 100 else description
                print(f"   📝 설명: {desc_short}")
            
            if cover_url:
                print(f"   🖼️  커버: {cover_url}")
            
            print()
    
    def get_event_status(self, start_at, end_at):
        """이벤트 상태 판단"""
        if not start_at or not end_at:
            return "❓ 시간미정"
        
        try:
            now = datetime.utcnow()
            start_time = datetime.fromisoformat(start_at.replace('Z', '+00:00')).replace(tzinfo=None)
            end_time = datetime.fromisoformat(end_at.replace('Z', '+00:00')).replace(tzinfo=None)
            
            if now < start_time:
                return "⏰ 예정"
            elif start_time <= now <= end_time:
                return "🔴 진행중"
            else:
                return "✅ 종료"
                
        except:
            return "❓ 알수없음"
    
    def format_datetime(self, datetime_str):
        """날짜/시간 포맷팅"""
        if not datetime_str:
            return "시간 정보 없음"
        
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            # 한국 시간으로 변환 (UTC+9)
            kst_time = dt + timedelta(hours=9)
            return kst_time.strftime('%Y-%m-%d %H:%M:%S KST')
        except:
            return datetime_str
    
    def filter_live_events(self, events):
        """진행중인 이벤트만 필터링"""
        live_events = []
        
        for entry in events:
            event = entry.get('event', {})
            start_at = event.get('start_at', '')
            end_at = event.get('end_at', '')
            
            if self.get_event_status(start_at, end_at) == "🔴 진행중":
                live_events.append(entry)
        
        return live_events
    
    def filter_upcoming_events(self, events):
        """예정된 이벤트만 필터링"""
        upcoming_events = []
        
        for entry in events:
            event = entry.get('event', {})
            start_at = event.get('start_at', '')
            end_at = event.get('end_at', '')
            
            if self.get_event_status(start_at, end_at) == "⏰ 예정":
                upcoming_events.append(entry)
        
        return upcoming_events
    
    def test_checkin_workflow(self, event_api_id):
        """체크인 워크플로우 테스트"""
        print(f"\n🔄 이벤트 {event_api_id}의 체크인 워크플로우 테스트")
        print("-" * 60)
        
        # 1. 참석자 목록 조회
        guests = self.get_event_guests(event_api_id)
        
        if not guests:
            print("❌ 참석자 정보를 가져올 수 없습니다.")
            return
        
        # 2. 체크인 정보 분석
        checked_in_guests = []
        pending_guests = []
        
        for guest in guests:
            checkin_info = guest.get('checkin_info', {})
            checked_in_at = checkin_info.get('checked_in_at')
            
            if checked_in_at:
                checked_in_guests.append(guest)
            else:
                pending_guests.append(guest)
        
        print(f"✅ 체크인 완료: {len(checked_in_guests)}명")
        print(f"⏳ 체크인 대기: {len(pending_guests)}명")
        
        # 3. 최근 체크인 분석
        recent_checkins = self.get_recent_checkins(checked_in_guests, minutes_ago=5)
        print(f"🕐 최근 5분 내 체크인: {len(recent_checkins)}명")
        
        # 4. 체크인 정보 출력
        if recent_checkins:
            print("\n📋 최근 체크인 사용자:")
            for guest in recent_checkins:
                name = guest.get('name', '알 수 없음')
                email = guest.get('email', '이메일 없음')
                checkin_time = guest.get('checkin_info', {}).get('checked_in_at', '')
                formatted_time = self.format_datetime(checkin_time)
                
                print(f"   👤 {name} ({email}) - {formatted_time}")
    
    def get_recent_checkins(self, guests, minutes_ago=5):
        """최근 N분 내 체크인한 사용자 필터링"""
        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=minutes_ago)
        
        recent_checkins = []
        
        for guest in guests:
            checkin_info = guest.get('checkin_info', {})
            checked_in_at_str = checkin_info.get('checked_in_at')
            
            if not checked_in_at_str:
                continue
            
            try:
                checked_in_at = datetime.fromisoformat(checked_in_at_str.replace('Z', '+00:00'))
                if checked_in_at.tzinfo:
                    checked_in_at = checked_in_at.replace(tzinfo=None)
                
                if checked_in_at >= cutoff_time:
                    recent_checkins.append(guest)
                    
            except (ValueError, TypeError):
                continue
        
        return recent_checkins


def main():
    """메인 함수"""
    print("🧪 Luma API 실제 작동 테스트")
    print("=" * 60)
    
    try:
        tester = LumaAPITester()
        
        # 1. 모든 이벤트 조회
        all_events = tester.get_all_events()
        tester.print_event_details(all_events)
        
        # 2. 진행중인 이벤트 필터링
        live_events = tester.filter_live_events(all_events)
        print(f"\n🔴 현재 진행중인 이벤트: {len(live_events)}개")
        
        if live_events:
            print("\n진행중인 이벤트 목록:")
            tester.print_event_details(live_events)
            
            # 첫 번째 진행중인 이벤트로 체크인 테스트
            first_live_event = live_events[0]
            event_api_id = first_live_event.get('event', {}).get('api_id')
            
            if event_api_id:
                tester.test_checkin_workflow(event_api_id)
        
        # 3. 예정된 이벤트 필터링
        upcoming_events = tester.filter_upcoming_events(all_events)
        print(f"\n⏰ 예정된 이벤트: {len(upcoming_events)}개")
        
        if upcoming_events:
            print("\n예정된 이벤트 목록:")
            tester.print_event_details(upcoming_events[:3])  # 상위 3개만
        
        print("\n🎉 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")


if __name__ == "__main__":
    main() 