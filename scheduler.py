#!/usr/bin/env python3
"""
Luma Check-in Bot Scheduler

이 스크립트는 luma_checkin_bot.py를 5분마다 실행하는 스케줄러입니다.
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


def run_bot():
    """봇 실행 함수"""
    try:
        logger.info("Luma 체크인 봇 실행 중...")
        result = subprocess.run([
            sys.executable, 'luma_checkin_bot.py'
        ], capture_output=True, text=True, timeout=60)
        
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


def main():
    """메인 함수"""
    logger.info("Luma 체크인 봇 스케줄러 시작")
    logger.info("5분마다 봇이 실행됩니다...")
    
    # 5분마다 실행되도록 스케줄 설정
    schedule.every(5).minutes.do(run_bot)
    
    # 시작 시 한 번 실행
    logger.info("초기 실행...")
    run_bot()
    
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