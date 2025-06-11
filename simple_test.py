#!/usr/bin/env python3
"""
Luma API 체크인 모니터링 스크립트
5분마다 실행되어 최근 5분 내 체크인한 참가자를 확인하고 텔레그램으로 알림
"""

import os
import requests
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# API 설정
api_key = os.getenv('LUMA_API_KEY')
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

base_url = "https://api.lu.ma/public/v1/calendar/list-events"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def send_telegram_message(message: str) -> bool:
    """텔레그램 메시지 전송"""
    if not telegram_bot_token or not telegram_chat_id:
        print("❌ 텔레그램 설정이 없어 메시지 전송을 건너뜁니다.")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        data = {
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("✅ 텔레그램 메시지 전송 성공")
        return True
    except requests.RequestException as e:
        print(f"❌ 텔레그램 메시지 전송 실패: {e}")
        return False

def is_recent_checkin(checked_in_at_str: str, minutes_ago: int = 5) -> bool:
    """최근 N분 내 체크인인지 확인"""
    if not checked_in_at_str:
        return False
    
    try:
        # ISO 8601 형식의 시간 문자열을 파싱
        checked_in_at = datetime.fromisoformat(checked_in_at_str.replace('Z', '+00:00'))
        
        # UTC로 변환
        if checked_in_at.tzinfo:
            checked_in_at = checked_in_at.replace(tzinfo=None)
        
        # 현재 시간과 비교
        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=minutes_ago)
        
        return checked_in_at >= cutoff_time
        
    except (ValueError, TypeError) as e:
        print(f"⚠️ 체크인 시간 파싱 실패: {checked_in_at_str}, 오류: {e}")
        return False

def format_telegram_message(guest: dict, event_name: str) -> str:
    """텔레그램 메시지 포맷팅"""
    name = guest.get('name', guest.get('user_name', 'Unknown'))
    email = guest.get('email', guest.get('user_email', 'Unknown'))
    checked_in_time = guest.get('checked_in_at')
    
    # 한국 시간으로 변환
    try:
        checked_in_at = datetime.fromisoformat(checked_in_time.replace('Z', '+00:00'))
        kst_time = checked_in_at + timedelta(hours=9)
        formatted_time = kst_time.strftime('%Y-%m-%d %H:%M:%S KST')
    except:
        formatted_time = checked_in_time
    
    # 등록 정보 포맷팅
    registration_info = ""
    registration_answers = guest.get('registration_answers', [])
    if registration_answers:
        registration_info = "\n\n📝 <b>등록 정보:</b>\n"
        for answer in registration_answers:
            label = answer.get('label', 'Unknown')
            answer_text = answer.get('answer', 'No answer')
            registration_info += f"• <b>{label}:</b> {answer_text}\n"
    
    message = f"""
🎫 <b>새로운 체크인 알림</b>

📅 <b>이벤트:</b> {event_name}
👤 <b>이름:</b> {name}
📧 <b>이메일:</b> {email}
⏰ <b>체크인 시간:</b> {formatted_time}{registration_info}
    """.strip()
    
    return message

def get_event_guests(event_id):
    """특정 이벤트의 참석자 목록 조회"""
    guests_url = "https://api.lu.ma/public/v1/event/get-guests"
    params = {
        "event_api_id": event_id,
        "approval_status": "approved",
        "sort_direction": "asc nulls last",
        "sort_column": "checked_in_at"
    }
    
    try:
        response = requests.get(guests_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('entries', [])
        else:
            print(f"      ❌ 참석자 조회 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"      💥 참석자 조회 오류: {e}")
        return []

def main():
    """메인 실행 함수"""
    print(f"🔍 Luma API 체크인 모니터링 실행 중... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"URL: {base_url}")
    print(f"API Key: {api_key[:10]}...")

    # 현재 시각 기준 앞뒤 7일 계산
    now = datetime.now(timezone.utc)
    before_date = now + timedelta(days=7)
    after_date = now - timedelta(days=7)

    # ISO 8601 형식으로 변환
    before_iso = before_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
    after_iso = after_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'

    # 쿼리 파라미터 설정
    params = {
        "before": before_iso,
        "after": after_iso
    }

    # API 호출
    try:
        response = requests.get(base_url, headers=headers, params=params)
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('entries', [])
            print(f"✅ 성공! {len(events)}개 이벤트 발견")
            
            recent_checkins_found = False
            
            # 모든 이벤트 정보와 참석자 확인
            if events:
                print(f"\n=== 이벤트 체크인 모니터링 ===")
                for i, entry in enumerate(events, 1):
                    event = entry.get('event', {})
                    event_id = event.get('api_id')
                    event_name = event.get('name')
                    
                    print(f"\n{i}. 이벤트: {event_name}")
                    print(f"   ID: {event_id}")
                    
                    # 각 이벤트의 참석자 조회
                    all_guests = get_event_guests(event_id)
                    
                    if all_guests:
                        # checked_in_at이 None이 아닌 참가자만 필터링
                        checked_in_guests = []
                        recent_checkin_guests = []
                        
                        for guest_entry in all_guests:
                            guest = guest_entry.get('guest', {})
                            checked_in_at = guest.get('checked_in_at')
                            
                            if checked_in_at is not None:
                                checked_in_guests.append(guest)
                                
                                # 최근 5분 내 체크인인지 확인
                                if is_recent_checkin(checked_in_at, 5):
                                    recent_checkin_guests.append(guest)
                        
                        print(f"   전체 참가자 수: {len(all_guests)}명")
                        print(f"   체크인 완료: {len(checked_in_guests)}명")
                        print(f"   최근 5분 내 체크인: {len(recent_checkin_guests)}명")
                        
                        # 최근 5분 내 체크인이 있으면 텔레그램 전송
                        if recent_checkin_guests:
                            recent_checkins_found = True
                            print("\n   🚨 최근 체크인 발견! 텔레그램 알림 전송 중...")
                            
                            for j, guest in enumerate(recent_checkin_guests, 1):
                                name = guest.get('name', guest.get('user_name', 'Unknown'))
                                email = guest.get('email', guest.get('user_email', 'Unknown'))
                                checked_in_time = guest.get('checked_in_at')
                                
                                print(f"\n      [최근 체크인 {j}] {name}")
                                print(f"          📧 이메일: {email}")
                                print(f"          ⏰ 체크인: {checked_in_time}")
                                
                                # Registration answers 출력
                                registration_answers = guest.get('registration_answers', [])
                                if registration_answers:
                                    print(f"          📝 등록 정보:")
                                    for answer in registration_answers:
                                        label = answer.get('label', 'Unknown')
                                        answer_text = answer.get('answer', 'No answer')
                                        print(f"             • {label}: {answer_text}")
                                
                                # 텔레그램 메시지 전송
                                telegram_message = format_telegram_message(guest, event_name)
                                send_telegram_message(telegram_message)
                        
                        # 전체 체크인한 참가자 정보 (최근이 아닌 경우 콘솔에만 출력)
                        elif checked_in_guests:
                            print("\n   체크인한 참가자 (최근 5분 외):")
                            for j, guest in enumerate(checked_in_guests, 1):
                                name = guest.get('name', guest.get('user_name', 'Unknown'))
                                email = guest.get('email', guest.get('user_email', 'Unknown'))
                                checked_in_time = guest.get('checked_in_at')
                                
                                print(f"\n      [{j}] {name}")
                                print(f"          📧 이메일: {email}")
                                print(f"          ⏰ 체크인: {checked_in_time}")
                                
                                # Registration answers 출력
                                registration_answers = guest.get('registration_answers', [])
                                if registration_answers:
                                    print(f"          📝 등록 정보:")
                                    for answer in registration_answers:
                                        label = answer.get('label', 'Unknown')
                                        answer_text = answer.get('answer', 'No answer')
                                        print(f"             • {label}: {answer_text}")
                        else:
                            print("   참석자 정보 없음")
                    else:
                        print("   참석자 정보 없음")
            
            if not recent_checkins_found:
                print("\n💤 최근 5분 내 새로운 체크인이 없습니다. 콘솔 출력만 진행.")
                
        else:
            print(f"❌ 실패: {response.text}")
            
    except Exception as e:
        print(f"💥 오류: {e}")

    print(f"\n모니터링 완료! ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

if __name__ == "__main__":
    main() 