# Luma Check-in Telegram Notification Bot

Luma 이벤트의 새로운 체크인 정보를 Telegram으로 실시간 알림하는 봇입니다.

## 기능

- Luma API를 통해 현재 라이브 상태인 이벤트 조회
- 최근 5분 내 체크인한 참석자 정보 필터링
- Telegram Bot을 통해 체크인 알림 전송
- 5분 주기 자동 실행

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.template` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값들을 입력하세요:

```bash
cp .env.template .env
```

`.env` 파일에서 다음 값들을 설정해주세요:

- `LUMA_API_KEY`: Luma API 키
- `TELEGRAM_BOT_TOKEN`: Telegram Bot 토큰
- `TELEGRAM_CHAT_ID`: 알림을 받을 Telegram 그룹 채팅방 ID
- `VIP_GUESTS`: VIP 참석자 명단 (선택사항, 쉼표로 구분)
- `MENTION_USERS`: VIP 체크인 시 멘션할 사용자들 (선택사항, @username 형태)

### 3. API 키 발급 방법

#### Luma API Key
1. [Luma 개발자 문서](https://docs.lu.ma/reference/getting-started-with-your-api)에서 API 키 발급
2. 발급받은 키를 `.env` 파일의 `LUMA_API_KEY`에 입력

#### Telegram Bot Token
1. Telegram에서 [@BotFather](https://t.me/BotFather)와 대화
2. `/newbot` 명령어로 새 봇 생성
3. 발급받은 토큰을 `.env` 파일의 `TELEGRAM_BOT_TOKEN`에 입력

#### Telegram Group Chat ID (그룹 채팅방)
1. Telegram에서 **새 그룹** 생성 (예: "Luma 체크인 알림")
2. **운영진들을 그룹에 초대**
3. **봇을 그룹에 추가** (봇 username으로 검색하여 추가)
4. 그룹에서 아무 메시지나 전송 후, 다음 URL로 Chat ID 확인:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
5. 응답에서 `chat.id` 값을 `.env` 파일의 `TELEGRAM_CHAT_ID`에 입력
   - 그룹 Chat ID는 음수로 시작됩니다 (예: `-987654321`)

## 사용법

### 단발성 실행

```bash
python luma_checkin_bot.py
```

### 스케줄러를 통한 자동 실행

```bash
python scheduler.py
```

스케줄러는 5분마다 봇을 자동으로 실행합니다.

### Cron을 사용한 실행 (Linux/macOS)

```bash
# crontab 편집
crontab -e

# 5분마다 실행하도록 추가
*/5 * * * * cd /path/to/project && python luma_checkin_bot.py
```

## 로그

- `luma_checkin_bot.log`: 봇 실행 로그
- `scheduler.log`: 스케줄러 로그

## 메시지 형식

### 일반 체크인 알림:
```
🎫 새로운 체크인 알림

📅 이벤트: [이벤트명]
👤 이름: [참석자명]
📧 이메일: [이메일]
🏷️ 티켓 종류: [티켓 타입]
⏰ 체크인 시간: [체크인 시간 (KST)]
```

### VIP 체크인 알림:
```
🎫 🌟 VIP 새로운 체크인 알림

📅 이벤트: [이벤트명]
👤 이름: [VIP 참석자명]
📧 이메일: [이메일]
🏷️ 티켓 종류: [티켓 타입]
⏰ 체크인 시간: [체크인 시간 (KST)]

🚨 VIP 참석자 체크인! @manager1 @event_staff
```

## 문제 해결

### 일반적인 문제

1. **API 인증 실패**: `.env` 파일의 API 키가 올바른지 확인
2. **Telegram 메시지 전송 실패**: Bot 토큰과 Chat ID가 올바른지 확인
3. **라이브 이벤트 없음**: Luma에서 현재 라이브 상태인 이벤트가 있는지 확인

### 로그 확인

상세한 로그는 `luma_checkin_bot.log` 파일에서 확인할 수 있습니다.

## 주의사항

- 이 봇은 단일 라이브 이벤트만 처리합니다
- API 호출 제한을 고려하여 5분 주기로 실행됩니다
- 네트워크 오류 시 다음 주기에 재시도됩니다 