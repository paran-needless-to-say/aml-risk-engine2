# 최종 아키텍처: CEX용 리스크 스코어링 시스템

## 🎯 시스템 목적

**CEX(중앙화 거래소)를 위한 주소 추적 및 리스크 스코어링 시스템**

- 거래소 입금/출금 주소의 리스크 평가
- 실시간 모니터링 및 알림
- 수동 주소 분석

## 📋 역할 분담

### 리스크 스코어링 엔진 (우리 담당)

- 주소 기반 리스크 스코어링
- 룰 평가 및 점수 계산
- 시간 기반 집계 (윈도우 룰)

### 백엔드 (외부)

- 전체 API 설계 및 라우팅
- 프론트엔드와의 통신
- 데이터 수집 및 전처리
- 주소 거래 히스토리 수집

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      프론트엔드 (Trace-X)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 대시보드 │  │실시간탐지│  │ 수동탐지 │  │  보고서  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        백엔드 API                             │
│  - API 라우팅                                                │
│  - 인증/인가                                                 │
│  - 데이터 수집 (블록체인 노드)                                │
│  - 주소 거래 히스토리 수집                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              리스크 스코어링 엔진 (우리 담당)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  주소 기반 분석 API                                    │  │
│  │  POST /api/analyze/address                            │  │
│  │  - 주소 입력 → 거래 히스토리 분석 → 리스크 스코어     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  비동기 분석 큐                                        │  │
│  │  - 실시간 탐지용 주소들을 큐에 추가                    │  │
│  │  - 백그라운드에서 비동기 처리                          │  │
│  │  - 결과를 백엔드로 전달                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  룰 평가 엔진                                          │  │
│  │  - TRACE-X 룰북 기반 평가                              │  │
│  │  - 단일 트랜잭션 룰                                    │  │
│  │  - 시간 기반 집계 (윈도우 룰)                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 데이터 흐름

### 1. 수동 탐지 (Manual Detection)

```
사용자가 주소 입력
    ↓
[프론트엔드] → POST /api/manual/detect
    ↓
[백엔드] → 주소 거래 히스토리 수집 (블록체인 노드)
    ↓
[백엔드] → POST /api/analyze/address (리스크 엔진)
    ↓
[리스크 엔진]
  1. 거래 히스토리 받음
  2. 각 거래에 대해 룰 평가
  3. 시간 기반 집계 (윈도우 룰)
  4. 최종 리스크 스코어 계산
    ↓
[리스크 엔진] → Response (리스크 스코어, 발동된 룰 등)
    ↓
[백엔드] → 프론트엔드로 전달
    ↓
[프론트엔드] → 결과 표시
```

### 2. 실시간 탐지 (Real-time Detection)

```
거래소 입금/출금 발생
    ↓
[거래소] → 주소 목록 전송 (비동기)
    ↓
[백엔드] → 주소들을 분석 큐에 추가
    ↓
[리스크 엔진 - 비동기 큐]
  - 큐에서 주소 하나씩 처리
  - 백엔드에서 거래 히스토리 수집 요청
  - 주소 분석 수행
  - 결과를 백엔드로 전달
    ↓
[백엔드] → 결과 저장 및 알림 생성
    ↓
[프론트엔드]
  - 실시간 탐지 화면에 표시
  - 대시보드에 통계 반영
```

### 3. 대시보드 (Dashboard)

```
[프론트엔드] → GET /api/dashboard/stats
    ↓
[백엔드] → 저장된 분석 결과 집계
    ↓
[백엔드] → 통계 정보 반환
    ↓
[프론트엔드] → 차트 및 요약 표시
```

## 📡 리스크 스코어링 엔진 API

### 1. 주소 기반 분석 API (수동 탐지용)

```http
POST /api/analyze/address
Content-Type: application/json

Request:
{
  "address": "0xabc...",
  "chain": "ethereum",
  "transactions": [
    {
      "tx_hash": "0x...",
      "timestamp": "2024-01-01T00:00:00Z",
      "block_height": 12345,
      "from": "0x...",
      "to": "0xabc...",
      "amount_usd": 1000.0,
      "entity_type": "mixer",
      "is_sanctioned": false,
      "is_known_scam": false,
      "is_mixer": true,
      "is_bridge": false,
      "asset_contract": "0x..."
    },
    ...
  ],
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-12-31T23:59:59Z"
  }
}

Response:
{
  "address": "0xabc...",
  "chain": "ethereum",
  "risk_score": 78.0,
  "risk_level": "high",
  "analysis_summary": {
    "total_transactions": 150,
    "total_volume_usd": 50000.0,
    "time_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-12-31T23:59:59Z"
    }
  },
  "fired_rules": [
    {
      "rule_id": "C-001",
      "name": "Sanction Direct Touch",
      "score": 30,
      "axis": "C",
      "severity": "HIGH",
      "count": 1
    },
    {
      "rule_id": "C-004",
      "name": "High-Value Repeated Transfer (24h)",
      "score": 20,
      "axis": "C",
      "severity": "MEDIUM",
      "count": 3
    },
    ...
  ],
  "risk_tags": [
    "mixer_inflow",
    "sanction_exposure",
    "high_value_transfer"
  ],
  "transaction_patterns": {
    "mixer_exposure_count": 3,
    "sanctioned_exposure_count": 1,
    "high_value_count": 10,
    "burst_patterns": 2
  },
  "timeline": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "risk_score": 30.0,
      "fired_rules": ["C-001"]
    },
    ...
  ]
}
```

### 2. 비동기 분석 큐 (실시간 탐지용)

```http
POST /api/analyze/address/async
Content-Type: application/json

Request:
{
  "address": "0xabc...",
  "chain": "ethereum",
  "callback_url": "https://backend/api/callbacks/analysis"  // 백엔드 콜백 URL
}

Response:
{
  "job_id": "job_12345",
  "status": "queued",
  "estimated_time": 30  // 초
}
```

```http
GET /api/analyze/address/async/{job_id}

Response:
{
  "job_id": "job_12345",
  "status": "completed",  // queued | processing | completed | failed
  "result": {
    "address": "0xabc...",
    "risk_score": 78.0,
    ...
  }
}
```

## 🔧 구현 구조

### 핵심 모듈

```
core/
├── scoring/
│   └── engine.py              # 주소 기반 스코어링 엔진
├── rules/
│   ├── evaluator.py           # 룰 평가기
│   └── loader.py              # 룰북 로더
├── aggregation/
│   └── window.py              # 시간 기반 집계
└── data/
    └── lists.py               # 블랙리스트/화이트리스트

api/
├── routes/
│   ├── address_analysis.py    # 주소 분석 API
│   └── async_queue.py         # 비동기 큐 API
└── app.py
```

### 주소 분석 엔진

```python
class AddressAnalyzer:
    """주소 기반 리스크 분석기"""

    def analyze_address(
        self,
        address: str,
        transactions: List[Dict],
        time_range: Optional[Dict] = None
    ) -> AddressAnalysisResult:
        """
        1. 트랜잭션을 시간순 정렬
        2. 각 트랜잭션에 대해 룰 평가
        3. 시간 기반 집계 (윈도우 룰)
        4. 최종 리스크 스코어 계산
        5. 패턴 분석
        """
```

## 🧪 시연용 구조

실제 거래소 연동이 없으므로, 시연용 구조:

### 시연 시나리오

1. **수동 탐지 시연**

   - 미리 준비된 주소 목록
   - 각 주소의 거래 히스토리 (CSV 또는 JSON)
   - 프론트엔드에서 주소 선택 → 분석

2. **실시간 탐지 시연**
   - 시뮬레이션: 주소 목록을 주기적으로 큐에 추가
   - 실제로는 거래소가 보내는 주소들을 처리

### 시연용 데이터

```
demo/
├── addresses.json          # 시연용 주소 목록
├── transactions/           # 각 주소의 거래 히스토리
│   ├── 0xabc..._txs.json
│   └── 0xdef..._txs.json
└── scenarios/             # 시나리오별 데이터
    ├── high_risk.json
    ├── medium_risk.json
    └── low_risk.json
```

## 📊 리스크 스코어 계산 로직

### 1. 단일 트랜잭션 룰 평가

- 각 거래에 대해 룰 평가
- 발동된 룰의 점수 합산

### 2. 시간 기반 집계 (윈도우 룰)

- 24시간, 1시간 등 윈도우 내 거래 집계
- sum_gte, count_gte, every_gte 등 조건 평가

### 3. 최종 스코어 계산

```python
# 방법 1: 최대 점수 (가장 위험한 거래 기준)
final_score = max(tx_scores)

# 방법 2: 가중 평균 (최근 거래가 더 중요)
final_score = weighted_average(tx_scores, time_weights)

# 방법 3: 누적 점수 (모든 룰 점수 합산, 최대 100)
final_score = min(100, sum(all_rule_scores))
```

### 4. Risk Level 결정

- 0-29: low
- 30-59: medium
- 60-79: high
- 80-100: critical

## 🚀 구현 우선순위

1. **주소 기반 분석 API** (수동 탐지)

   - 주소 입력 → 거래 히스토리 분석 → 리스크 스코어
   - 가장 중요

2. **비동기 분석 큐** (실시간 탐지)

   - 큐 기반 비동기 처리
   - 결과 콜백

3. **시연용 데이터 및 시나리오**
   - 미리 준비된 주소 및 거래 데이터

## 💡 주요 고려사항

1. **성능**

   - 많은 거래를 가진 주소는 분석 시간이 오래 걸림
   - 비동기 처리 필수
   - 캐싱 고려 (같은 주소 재분석 시)

2. **확장성**

   - 큐 시스템 (Redis, RabbitMQ 등)
   - 워커 프로세스 분산 처리

3. **시연**
   - 실제 거래소 연동 없이도 동작
   - 미리 준비된 데이터로 시연 가능
