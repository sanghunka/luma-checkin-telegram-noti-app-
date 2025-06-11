### **제품 요구사항 명세서 (PRD): Luma 체크인 Telegram 알림 봇**

### **1. 개요 (Overview)**

#### **1.1. 배경 (Background)**

Luma를 사용하여 이벤트를 운영할 때, 현장 스태프나 운영진은 어떤 참석자가 언제 체크인했는지 신속하게 파악해야 합니다. 하지만 모든 스태프가 Luma 대시보드에 접근하기는 번거로우며, 실시간 현황을 즉각적으로 공유하기 어렵습니다. 대부분의 운영팀이 사용하는 Telegram을 통해 체크인 정보를 실시간으로 공유하면, 이벤트 운영 효율성을 크게 향상시킬 수 있습니다.

#### **1.2. 목표 (Goals)**

  * 현재 진행 중인 Luma 이벤트의 체크인 정보를 지정된 Telegram 그룹으로 자동 전송한다.
  * 운영진이 별도의 대시보드 확인 없이 Telegram을 통해 체크인 현황을 '거의 실시간'으로 파악하게 한다.
  * 5분 주기로 새로운 체크인 정보만 필터링하여 전송함으로써, 정보의 중복 및 피로도를 줄인다.

#### **1.3. 범위 (Scope)**

  * **In Scope (포함 범위):**
      * Luma API를 통해 현재 '라이브' 상태인 이벤트 정보 조회
      * 해당 이벤트의 참석자 중, 최근 5분 이내에 체크인한 사람의 정보 조회
      * 지정된 Telegram Bot을 통해 특정 그룹 채팅방으로 체크인 정보 발송
      * API Key 등 민감 정보의 안전한 관리
  * **Out of Scope (미포함 범위):**
      * 여러 개의 라이브 이벤트를 동시에 처리하는 기능 (초기 버전은 단일 라이브 이벤트 기준)
      * Telegram에서 Luma로 정보를 보내는 양방향 통신
      * 체크인 취소에 대한 알림
      * 과거 데이터 분석 및 리포팅 기능

### **2. 기능 요구사항 (Functional Requirements)**

| ID | 기능명 | 상세 설명 |
| :--- | :--- | :--- |
| **FR-1** | **라이브 이벤트 조회** | 시스템은 Luma API에 인증하고, 현재 `is_live` 상태인 이벤트의 `api_id`를 식별해야 한다. 만약 라이브 이벤트가 없다면, 프로세스를 조용히 종료한다. |
| **FR-2** | **최근 체크인 사용자 필터링** | **FR-1**에서 식별된 이벤트를 대상으로, Luma API의 `List guests for an event` 엔드포인트를 호출한다. \<br\> - 모든 참석자 정보를 가져온다.\<br\> - 각 참석자의 체크인 시간(`checkin_info.checked_in_at`)을 확인한다.\<br\> - 스크립트 실행 시점을 기준으로, **최근 5분 이내에 체크인한 사용자**만 필터링한다. |
| **FR-3** | **Telegram 메시지 포맷팅** | **FR-2**에서 필터링된 각 사용자의 정보를 바탕으로 Telegram 메시지를 생성한다. 메시지에는 다음 정보가 포함되어야 한다.\<br\> - **이름 (Name):** `name`\<br\> - **이메일 (Email):** `email`\<br\> - **티켓 종류 (Ticket Type):** `ticket_type`\<br\> - **체크인 시간 (Check-in Time):** `checkin_info.checked_in_at` (가독성 좋은 형식으로 변환) |
| **FR-4** | **Telegram 메시지 전송** | 생성된 메시지를 지정된 Telegram Bot API를 통해 특정 `CHAT_ID`를 가진 그룹으로 전송한다. 새로운 체크인 유저가 여러 명일 경우, 각 유저별로 메시지를 보내거나 하나의 요약 메시지로 묶어 보낼 수 있다. (초기 버전은 개별 메시지 발송) |
| **FR-5** | **주기적 실행 (스케줄링)** | 전체 프로세스(FR-1 \~ FR-4)는 **매 5분 간격**으로 자동으로 실행되어야 한다. (예: Cron Job, 스케줄링 라이브러리 등 사용) |

### **3. 비기능 요구사항 (Non-Functional Requirements)**

| ID | 요구사항 | 상세 설명 |
| :--- | :--- | :--- |
| **NFR-1**| **성능 (Performance)** | 전체 스크립트는 API 호출 및 데이터 처리를 포함하여 1분 이내에 완료되어야 다음 스케줄에 영향을 주지 않는다. |
| **NFR-2**| **안정성 (Reliability)** | Luma 또는 Telegram API 호출 실패 시, 스크립트가 비정상 종료되지 않아야 한다. 오류를 로그로 기록하고, 다음 실행 주기에 재시도해야 한다. |
| **NFR-3**| **보안 (Security)** | Luma API Key, Telegram Bot Token, Chat ID 등 민감한 정보는 소스 코드에 하드코딩하지 않고, 환경 변수(Environment Variables)나 별도의 설정 파일을 통해 안전하게 관리해야 한다. |

### **4. 기술 스택 및 구현 방안 (Tech Stack & Implementation Plan)**

  * **APIs:**
      * [Luma API](https://docs.lu.ma/reference/getting-started-with-your-api)
      * [Telegram Bot API](https://core.telegram.org/bots/api)
  * **실행 환경 (Execution Environment):**
      * Linux 서버의 `cron`을 사용하여 5분마다 스크립트 실행
  * **핵심 로직 (Core Logic - 5분 필터링):**
    1.  스크립트 시작 시 현재 시간(`now`)을 기록한다.
    2.  5분 전 시간(`five_minutes_ago`)을 계산한다.
    3.  Luma API를 통해 이벤트의 모든 체크인 정보를 가져온다.
    4.  각 체크인 정보의 `checked_in_at` 타임스탬프가 `five_minutes_ago`와 `now` 사이에 있는지 확인하여 필터링한다.
    5.  필터링된 결과가 있을 경우에만 Telegram 전송 로직을 실행한다.
