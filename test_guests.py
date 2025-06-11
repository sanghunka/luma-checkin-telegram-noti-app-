#!/usr/bin/env python3
"""
Luma 이벤트 참석자 조회 테스트
"""

import os
import requests
import json
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# API 설정
api_key = os.getenv('LUMA_API_KEY')
url = "https://api.lu.ma/public/v1/event/get-guests"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 이벤트 ID와 파라미터 설정
event_id = "evt-tP03iqkZlwNKzBh"
params = {
    "event_api_id": event_id,
    "approval_status": "approved",
    "sort_column": "checked_in_at"
}

print("🔍 이벤트 참석자 조회 중...")
print(f"URL: {url}")
print(f"Event ID: {event_id}")
print(f"API Key: {api_key[:10]}...")

# API 호출
try:
    response = requests.get(url, headers=headers, params=params)
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        guests = data.get('entries', [])
        print(f"✅ 성공! {len(guests)}명의 참석자 발견")
        
        # 모든 참석자 정보 출력
        if guests:
            print(f"\n=== 참석자 목록 ===")
            for i, guest in enumerate(guests, 1):
                name = guest.get('name', '이름 없음')
                email = guest.get('email', '이메일 없음')
                ticket_type = guest.get('ticket_type', '일반')
                
                # 체크인 정보
                checkin_info = guest.get('checkin_info', {})
                checked_in_at = checkin_info.get('checked_in_at')
                checkin_status = "✅ 체크인 완료" if checked_in_at else "⏳ 체크인 대기"
                
                print(f"{i}. {name} ({email})")
                print(f"   티켓: {ticket_type}")
                print(f"   상태: {checkin_status}")
                if checked_in_at:
                    print(f"   체크인 시간: {checked_in_at}")
                print()
                
        else:
            print("참석자가 없습니다.")
            
    else:
        print(f"❌ 실패: {response.text}")
        
except Exception as e:
    print(f"💥 오류: {e}")

print("\n테스트 완료!") 