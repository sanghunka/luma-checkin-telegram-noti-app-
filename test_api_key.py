#!/usr/bin/env python3
"""
Luma API Key 검증 및 엔드포인트 테스트

API 키가 유효한지 확인하고 올바른 엔드포인트를 찾는 스크립트입니다.
"""

import os
import requests
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_api_key():
    """API 키 검증"""
    api_key = os.getenv('LUMA_API_KEY')
    
    if not api_key:
        print("❌ LUMA_API_KEY가 .env 파일에 설정되지 않았습니다.")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}..." if len(api_key) > 10 else f"🔑 API Key: {api_key}")
    
    # Luma API 문서에 따른 올바른 엔드포인트 시도
    base_urls = [
        "https://api.lu.ma",
    ]
    
    endpoints = [
        "/public/v1/event/get",      # 문서에서 확인된 올바른 엔드포인트
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("\n🔍 API 엔드포인트 테스트 중...\n")
    
    for base_url in base_urls:
        print(f"📡 베이스 URL 테스트: {base_url}")
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                print(f"   ➡️  {url}")
                response = requests.get(url, headers=headers, timeout=10)
                
                print(f"   📊 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ 성공!")
                    try:
                        data = response.json()
                        print(f"   📄 응답 구조: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        
                        # 이벤트 데이터가 있는지 확인
                        if isinstance(data, dict):
                            if 'entries' in data:
                                events = data.get('entries', [])
                                print(f"   🎫 이벤트 수: {len(events)}개")
                            elif 'events' in data:
                                events = data.get('events', [])
                                print(f"   🎫 이벤트 수: {len(events)}개")
                            elif 'data' in data:
                                events = data.get('data', [])
                                print(f"   🎫 이벤트 수: {len(events)}개")
                        
                        return True, url, data
                        
                    except json.JSONDecodeError:
                        print("   ⚠️  JSON 파싱 실패")
                        print(f"   📝 응답 내용: {response.text[:200]}...")
                        
                elif response.status_code == 401:
                    print("   🔐 인증 실패 (API 키 문제)")
                elif response.status_code == 403:
                    print("   🚫 권한 없음")
                elif response.status_code == 404:
                    print("   ❌ 엔드포인트 없음")
                else:
                    print(f"   ⚠️  기타 오류: {response.status_code}")
                    if response.text:
                        print(f"   📝 응답: {response.text[:200]}...")
                
            except requests.RequestException as e:
                print(f"   💥 요청 실패: {e}")
            
            print()
    
    return False, None, None


def test_alternative_methods():
    """다른 방법으로 API 테스트"""
    api_key = os.getenv('LUMA_API_KEY')
    
    print("🔄 다른 인증 방법 테스트...\n")
    
    # 1. API Key를 query parameter로
    test_urls = [
        f"https://api.lu.ma/public/v1/event/get?api_key={api_key}",
    ]
    
    for url in test_urls:
        try:
            print(f"🔗 테스트: {url.replace(api_key, 'API_KEY')}")
            response = requests.get(url, timeout=10)
            print(f"📊 상태: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 성공!")
                return True, url, response.json()
            else:
                print(f"❌ 실패: {response.text[:100]}...")
            print()
            
        except Exception as e:
            print(f"💥 오류: {e}\n")
    
    # 2. 다른 헤더 형식들
    headers_variations = [
        {"Authorization": f"Token {api_key}"},
        {"Authorization": f"API-Key {api_key}"},
        {"X-API-Key": api_key},
        {"API-Key": api_key}
    ]
    
    base_url = "https://public-api.lu.ma/public/v1/event/get"
    
    for headers in headers_variations:
        try:
            print(f"🔐 헤더 테스트: {list(headers.keys())}")
            response = requests.get(base_url, headers=headers, timeout=10)
            print(f"📊 상태: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 성공!")
                return True, base_url, response.json()
            else:
                print(f"❌ 실패: {response.text[:100]}...")
            print()
            
        except Exception as e:
            print(f"💥 오류: {e}\n")
    
    return False, None, None


def main():
    """메인 함수"""
    print("🧪 Luma API 테스트 시작!")
    print("=" * 60)
    
    # 1. 기본 API 키 테스트
    success, working_url, data = test_api_key()
    
    if success:
        print("🎉 작동하는 API 엔드포인트를 찾았습니다!")
        print(f"✅ URL: {working_url}")
        print("\n📄 응답 샘플:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
        return
    
    # 2. 대안 방법 테스트
    print("\n" + "=" * 60)
    success, working_url, data = test_alternative_methods()
    
    if success:
        print("🎉 대안 방법으로 성공!")
        print(f"✅ URL: {working_url}")
        return
    
    # 3. API 키 확인 제안
    print("\n" + "=" * 60)
    print("💡 API 키 확인 방법:")
    print("1. Luma 계정에 로그인")
    print("2. 개발자 설정에서 API 키 재확인")
    print("3. API 키 권한 확인 (이벤트 읽기 권한)")
    print("4. Luma 문서에서 최신 API 엔드포인트 확인")
    
    api_key = os.getenv('LUMA_API_KEY', '')
    if api_key:
        print(f"\n현재 설정된 API 키: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else api_key}")
    else:
        print("\n❌ API 키가 설정되지 않았습니다!")


if __name__ == "__main__":
    main() 