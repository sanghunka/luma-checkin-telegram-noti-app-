#!/usr/bin/env python3
"""
Luma Check-in Bot Scheduler

이 스크립트는 luma_checkin_bot.py를 5분마다 실행하는 스케줄러입니다.
첫 실행 시에는 20분 전 체크인을 검색하고, 이후로는 5분마다 최근 5분 체크인을 검색합니다.
"""

import schedule
import time
import subprocess
import logging
import sys
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scheduler.log')
    ]
)
logger = logging.getLogger(__name__)


def run_bot(minutes_ago=None):
    """봇 실행 함수"""
    try:
        cmd = [sys.executable, 'luma_checkin_bot.py']
        if minutes_ago:
            # 임시로 환경 변수로 minutes_ago 전달
            import os
            env = os.environ.copy()
            env['FORCE_MINUTES_AGO'] = str(minutes_ago)
            logger.info(f"Luma 체크인 봇 실행 중... (최근 {minutes_ago}분 체크인 검색)")
        else:
            env = None
            logger.info("Luma 체크인 봇 실행 중...")
            
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60,
            env=env
        )
        
        if result.returncode == 0:
            logger.info("봇 실행 성공")
            if result.stdout:
                logger.debug(f"출력: {result.stdout}")
        else:
            logger.error(f"봇 실행 실패 (exit code: {result.returncode})")
            if result.stderr:
                logger.error(f"에러: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        logger.error("봇 실행 시간 초과 (60초)")
    except Exception as e:
        logger.error(f"봇 실행 중 예외 발생: {e}")


def run_bot_regular():
    """일반적인 5분 주기 봇 실행"""
    run_bot()


def main():
    """메인 함수"""
    logger.info("Luma 체크인 봇 스케줄러 시작")
    logger.info("첫 실행은 20분 전 체크인을 검색하고, 이후 5분마다 실행됩니다...")
    
    # 5분마다 실행되도록 스케줄 설정 (일반 실행)
    schedule.every(5).minutes.do(run_bot_regular)
    
    # 시작 시 첫 번째 실행 - 20분 전 체크인 검색
    logger.info("초기 실행 (20분 전 체크인 검색)...")
    run_bot(minutes_ago=20)
    
    # 스케줄 실행
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("스케줄러 중지됨")
    except Exception as e:
        logger.error(f"스케줄러 오류: {e}")


if __name__ == "__main__":
    main() 