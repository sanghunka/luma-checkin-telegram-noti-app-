#!/usr/bin/env python3
"""
Luma Calendar Events 테스트

Calendar API를 사용해서 이벤트 목록을 조회하는 스크립트입니다.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_calendar_api():
    """Calendar API로 이벤트 목록 조회 테스트"""
    api_key = os.getenv('LUMA_API_KEY')
    
    if not api_key:
        print("❌ LUMA_API_KEY가 .env 파일에 설정되지 않았습니다.")
        return False
    
    print(f"🔑 API Key: {api_key}")
    
    # 다양한 Calendar API 엔드포인트 시도
    base_url = "https://api.lu.ma"
    
    endpoints = [
        "/public/v1/calendar/list-events",  # Calendar의 List Events
        "/public/v1/calendar/events",
        "/public/v1/event",                 # 기본 이벤트 목록
        "/v1/calendar/list-events",
        "/v1/calendar/events",
        "/v1/events",
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("\n🔍 Calendar API 엔드포인트 테스트 중...\n")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"➡️  {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📊 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 성공!")
                try:
                    data = response.json()
                    print(f"📄 응답 구조: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    
                    # 이벤트 데이터 확인
                    if isinstance(data, dict):
                        if 'entries' in data:
                            events = data.get('entries', [])
                            print(f"🎫 이벤트 수: {len(events)}개")
                        elif 'events' in data:
                            events = data.get('events', [])
                            print(f"🎫 이벤트 수: {len(events)}개")
                        elif 'data' in data:
                            events = data.get('data', [])
                            print(f"🎫 이벤트 수: {len(events)}개")
                        
                        # 응답 샘플 출력
                        print("📄 응답 샘플:")
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
                    
                    return True, url, data
                    
                except json.JSONDecodeError:
                    print("⚠️  JSON 파싱 실패")
                    print(f"📝 응답 내용: {response.text[:200]}...")
                    
            elif response.status_code == 401:
                print("🔐 인증 실패 (API 키 문제)")
                print(f"📝 응답: {response.text[:200]}...")
            elif response.status_code == 403:
                print("🚫 권한 없음")
                print(f"📝 응답: {response.text[:200]}...")
            elif response.status_code == 404:
                print("❌ 엔드포인트 없음")
            else:
                print(f"⚠️  기타 오류: {response.status_code}")
                print(f"📝 응답: {response.text[:200]}...")
            
        except requests.RequestException as e:
            print(f"💥 요청 실패: {e}")
        
        print()
    
    return False, None, None


def test_specific_event():
    """특정 이벤트 ID로 테스트 (만약 이벤트 ID를 안다면)"""
    api_key = os.getenv('LUMA_API_KEY')
    
    # 임시 이벤트 ID들 (실제로는 본인의 이벤트 ID를 사용해야 함)
    test_event_ids = [
        "evt-test123",
        "event-test",
        # 실제 이벤트 ID가 있다면 여기에 추가
    ]
    
    base_url = "https://api.lu.ma"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 특정 이벤트 조회 테스트...\n")
    
    for event_id in test_event_ids:
        url = f"{base_url}/public/v1/event/get"
        params = {"api_id": event_id}
        
        try:
            print(f"➡️  {url}?api_id={event_id}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            print(f"📊 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 성공!")
                data = response.json()
                print("📄 이벤트 정보:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
                return True, url, data
            else:
                print(f"❌ 실패: {response.text[:100]}...")
            
        except Exception as e:
            print(f"💥 오류: {e}")
        
        print()
    
    return False, None, None


def test_with_params():
    """다양한 파라미터로 테스트"""
    api_key = os.getenv('LUMA_API_KEY')
    
    base_url = "https://api.lu.ma"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 파라미터 포함 테스트...\n")
    
    # 다양한 파라미터 조합
    test_cases = [
        ("/public/v1/event", {}),
        ("/public/v1/event", {"limit": 10}),
        ("/public/v1/event", {"is_live": "true"}),
        ("/public/v1/event", {"is_upcoming": "true"}),
        ("/public/v1/calendar/list-events", {}),
        ("/public/v1/calendar/list-events", {"limit": 10}),
    ]
    
    for endpoint, params in test_cases:
        url = f"{base_url}{endpoint}"
        
        try:
            params_str = "&".join([f"{k}={v}" for k, v in params.items()])
            print(f"➡️  {url}{'?' + params_str if params_str else ''}")
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"📊 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 성공!")
                data = response.json()
                print(f"📄 응답 구조: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                return True, url, data
            else:
                print(f"❌ 실패: {response.text[:100]}...")
            
        except Exception as e:
            print(f"💥 오류: {e}")
        
        print()
    
    return False, None, None


def main():
    """메인 함수"""
    print("🧪 Luma Calendar API 테스트 시작!")
    print("=" * 60)
    
    # 1. Calendar API 테스트
    success, working_url, data = test_calendar_api()
    
    if success:
        print("🎉 작동하는 API 엔드포인트를 찾았습니다!")
        print(f"✅ URL: {working_url}")
        return
    
    # 2. 파라미터 포함 테스트
    print("\n" + "=" * 60)
    success, working_url, data = test_with_params()
    
    if success:
        print("🎉 파라미터로 성공!")
        print(f"✅ URL: {working_url}")
        return
    
    # 3. 특정 이벤트 테스트
    print("\n" + "=" * 60)
    success, working_url, data = test_specific_event()
    
    if success:
        print("🎉 특정 이벤트로 성공!")
        print(f"✅ URL: {working_url}")
        return
    
    # API 키 재확인 제안
    print("\n" + "=" * 60)
    print("💡 다음 단계:")
    print("1. Luma 계정에서 API 키 재발급")
    print("2. API 키 권한 확인 (읽기 권한)")
    print("3. 실제 이벤트 ID 확인")
    print("4. Luma 고객지원 문의")


if __name__ == "__main__":
    main() 