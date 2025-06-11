#!/usr/bin/env python3
"""
Luma Check-in Telegram Notification Bot

이 스크립트는 Luma 이벤트의 새로운 체크인 정보를 Telegram으로 전송합니다.
매 5분마다 실행되어 최근 5분 내 체크인한 사용자들을 찾아 알림을 보냅니다.
"""

import os
import sys
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('luma_checkin_bot.log')
    ]
)
logger = logging.getLogger(__name__)

class LumaAPI:
    """Luma API 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.lu.ma"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_live_events(self) -> List[Dict]:
        """현재 라이브 상태인 이벤트 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/public/v1/event",
                headers=self.headers,
                params={"is_live": True}
            )
            response.raise_for_status()
            data = response.json()
            return data.get('entries', [])
        except requests.RequestException as e:
            logger.error(f"라이브 이벤트 조회 실패: {e}")
            return []
    
    def get_event_guests(self, event_api_id: str) -> List[Dict]:
        """특정 이벤트의 참석자 목록 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/public/v1/event/{event_api_id}/guests",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get('entries', [])
        except requests.RequestException as e:
            logger.error(f"이벤트 {event_api_id}의 참석자 조회 실패: {e}")
            return []


class TelegramBot:
    """Telegram Bot API 클라이언트"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str) -> bool:
        """메시지 전송"""
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
            )
            response.raise_for_status()
            logger.info("Telegram 메시지 전송 성공")
            return True
        except requests.RequestException as e:
            logger.error(f"Telegram 메시지 전송 실패: {e}")
            return False


class LumaCheckinBot:
    """Luma 체크인 알림 봇 메인 클래스"""
    
    def __init__(self):
        # 환경 변수 검증
        self.luma_api_key = os.getenv('LUMA_API_KEY')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not all([self.luma_api_key, self.telegram_bot_token, self.telegram_chat_id]):
            raise ValueError("필수 환경 변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # VIP 설정 (선택사항)
        vip_guests_str = os.getenv('VIP_GUESTS', '')
        self.vip_guests = [name.strip() for name in vip_guests_str.split(',') if name.strip()]
        
        mention_users_str = os.getenv('MENTION_USERS', '')
        self.mention_users = [user.strip() for user in mention_users_str.split(',') if user.strip()]
        
        # API 클라이언트 초기화
        self.luma_api = LumaAPI(self.luma_api_key)
        self.telegram_bot = TelegramBot(self.telegram_bot_token, self.telegram_chat_id)
    
    def get_recent_checkins(self, guests: List[Dict], minutes_ago: int = 5) -> List[Dict]:
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
                # ISO 8601 형식의 시간 문자열을 파싱
                checked_in_at = datetime.fromisoformat(checked_in_at_str.replace('Z', '+00:00'))
                
                # UTC로 변환
                if checked_in_at.tzinfo:
                    checked_in_at = checked_in_at.replace(tzinfo=None)
                
                if checked_in_at >= cutoff_time:
                    recent_checkins.append(guest)
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"체크인 시간 파싱 실패: {checked_in_at_str}, 오류: {e}")
                continue
        
        return recent_checkins
    
    def format_checkin_message(self, guest: Dict, event_name: str) -> str:
        """체크인 메시지 포맷팅"""
        name = guest.get('name', '알 수 없음')
        email = guest.get('email', '이메일 없음')
        ticket_type = guest.get('ticket_type', '일반')
        
        checkin_info = guest.get('checkin_info', {})
        checked_in_at_str = checkin_info.get('checked_in_at', '')
        
        # 시간 포맷팅
        try:
            checked_in_at = datetime.fromisoformat(checked_in_at_str.replace('Z', '+00:00'))
            # 한국 시간으로 변환 (UTC+9)
            kst_time = checked_in_at + timedelta(hours=9)
            formatted_time = kst_time.strftime('%Y-%m-%d %H:%M:%S KST')
        except:
            formatted_time = checked_in_at_str
        
        # VIP 체크 및 멘션 추가
        is_vip = name in self.vip_guests
        vip_indicator = "🌟 VIP " if is_vip else ""
        
        message = f"""
🎫 <b>{vip_indicator}새로운 체크인 알림</b>

📅 <b>이벤트:</b> {event_name}
👤 <b>이름:</b> {name}
📧 <b>이메일:</b> {email}
🏷️ <b>티켓 종류:</b> {ticket_type}
⏰ <b>체크인 시간:</b> {formatted_time}
        """.strip()
        
        # VIP인 경우 멘션 추가
        if is_vip and self.mention_users:
            mentions = " ".join(self.mention_users)
            message += f"\n\n🚨 <b>VIP 참석자 체크인!</b> {mentions}"
            logger.info(f"VIP 참석자 {name} 체크인 - 멘션 전송: {mentions}")
        
        return message
    
    def run_check(self):
        """메인 체크 로직 실행"""
        try:
            logger.info("Luma 체크인 봇 실행 시작")
            
            # 1. 라이브 이벤트 조회
            live_events = self.luma_api.get_live_events()
            
            if not live_events:
                logger.info("현재 라이브 상태인 이벤트가 없습니다.")
                return
            
            # 첫 번째 라이브 이벤트 선택 (PRD에 따라 단일 이벤트만 처리)
            event = live_events[0]
            event_api_id = event.get('api_id')
            event_name = event.get('name', '알 수 없는 이벤트')
            
            logger.info(f"라이브 이벤트 발견: {event_name} (ID: {event_api_id})")
            
            # 2. 이벤트 참석자 조회
            guests = self.luma_api.get_event_guests(event_api_id)
            logger.info(f"총 {len(guests)}명의 참석자 정보를 조회했습니다.")
            
            # 3. 최근 5분 내 체크인한 사용자 필터링
            recent_checkins = self.get_recent_checkins(guests, minutes_ago=5)
            
            if not recent_checkins:
                logger.info("최근 5분 내 새로운 체크인이 없습니다.")
                return
            
            logger.info(f"최근 5분 내 {len(recent_checkins)}명이 체크인했습니다.")
            
            # 4. Telegram 메시지 전송
            for guest in recent_checkins:
                message = self.format_checkin_message(guest, event_name)
                success = self.telegram_bot.send_message(message)
                
                if success:
                    guest_name = guest.get('name', '알 수 없음')
                    logger.info(f"{guest_name}의 체크인 알림을 전송했습니다.")
                else:
                    logger.error(f"메시지 전송 실패: {guest.get('name', '알 수 없음')}")
            
            logger.info("Luma 체크인 봇 실행 완료")
            
        except Exception as e:
            logger.error(f"봇 실행 중 오류 발생: {e}", exc_info=True)


def main():
    """메인 함수"""
    try:
        bot = LumaCheckinBot()
        bot.run_check()
    except Exception as e:
        logger.error(f"봇 초기화 실패: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 