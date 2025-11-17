# 시스템 개요: CEX용 주소 추적 및 리스크 스코어링

## 🎯 시스템 목적

**CEX(중앙화 거래소)를 위한 주소 추적 및 리스크 스코어링 시스템**

- 주소의 거래 히스토리를 분석하여 리스크 평가
- 실시간 거래 모니터링 및 알림
- 의심 거래 탐지 및 보고서 생성

## 📱 프론트엔드 기능

### 1. 대시보드 (Dashboard)

- 전체 통계 및 요약
- 최근 알림
- 리스크 분포 차트

### 2. 실시간 탐지 (Real-time Detection)

- 실시간으로 들어오는 거래 모니터링
- 자동 스코어링 및 알림
- 위험 거래 즉시 탐지

### 3. 수동 탐지 (Manual Detection) ⭐ 현재 선택

- 사용자가 주소를 입력하여 분석
- 주소의 거래 히스토리 전체 분석
- 리스크 스코어 및 상세 정보 제공

### 4. 의심거래 보고서 (Suspicious Transaction Report)

- 의심 거래 목록
- 필터링 및 검색
- 상세 분석 결과

### 5. 사건 관리 (Case Management)

- 사건 생성 및 추적
- 조사 이력 관리
- 리포트 생성

## 🔄 현재 구현 상태 vs 필요한 기능

### ✅ 현재 구현된 것

1. **단일 트랜잭션 스코어링 API**
   - `POST /api/score/transaction`
   - 백엔드에서 받은 단일 트랜잭션 JSON을 스코어링
   - 룰 평가 및 점수 계산

### ❌ 필요한 기능

1. **주소 기반 분석 API** (수동 탐지용)

   - `POST /api/analyze/address`
   - 주소를 입력받아 해당 주소의 모든 거래 분석
   - 거래 히스토리 수집 및 집계
   - 최종 리스크 스코어 계산

2. **실시간 탐지 API**

   - `POST /api/detect/realtime` 또는 WebSocket
   - 지속적으로 들어오는 거래 모니터링
   - 위험 거래 자동 알림

3. **대시보드 API**

   - `GET /api/dashboard/stats`
   - 전체 통계 및 요약 정보

4. **의심거래 보고서 API**
   - `GET /api/reports/suspicious`
   - 의심 거래 목록 조회

## 📊 데이터 흐름

### 수동 탐지 (Manual Detection)

```
사용자가 주소 입력
    ↓
[주소 기반 분석 API]
    ↓
1. 주소의 모든 거래 히스토리 수집 (백엔드 또는 블록체인)
    ↓
2. 각 거래에 대해 룰 평가
    ↓
3. 시간 기반 집계 (윈도우 룰)
    ↓
4. 최종 리스크 스코어 계산
    ↓
5. 상세 정보 반환 (발동된 룰, 거래 패턴 등)
```

### 실시간 탐지 (Real-time Detection)

```
새 거래 발생
    ↓
[실시간 탐지 API]
    ↓
1. 단일 트랜잭션 스코어링
    ↓
2. 위험도가 높으면 알림 생성
    ↓
3. 주소 히스토리 업데이트
    ↓
4. 윈도우 룰 재평가 (필요시)
```

## 🔧 필요한 API 엔드포인트

### 1. 주소 분석 (수동 탐지)

```http
POST /api/analyze/address
Content-Type: application/json

{
  "address": "0x...",
  "chain": "ethereum",
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-12-31T23:59:59Z"
  }
}

Response:
{
  "address": "0x...",
  "risk_score": 78.0,
  "risk_level": "high",
  "total_transactions": 150,
  "total_volume_usd": 50000.0,
  "fired_rules": [...],
  "transaction_summary": {
    "mixer_exposure": 3,
    "sanctioned_exposure": 1,
    "high_value_count": 10
  },
  "timeline": [...]
}
```

### 2. 실시간 탐지

```http
POST /api/detect/realtime
Content-Type: application/json

{
  "tx_hash": "0x...",
  "chain": "ethereum",
  ...
}

Response:
{
  "risk_score": 85.0,
  "risk_level": "critical",
  "alert": true,
  "fired_rules": [...]
}
```

### 3. 대시보드 통계

```http
GET /api/dashboard/stats?period=24h

Response:
{
  "total_transactions": 10000,
  "high_risk_count": 150,
  "critical_count": 20,
  "risk_distribution": {
    "low": 8000,
    "medium": 1500,
    "high": 400,
    "critical": 100
  }
}
```

## 💡 구현 우선순위

1. **주소 기반 분석 API** (수동 탐지) - 가장 중요
2. **실시간 탐지 API** - 실시간 모니터링
3. **대시보드 API** - 통계 및 요약
4. **의심거래 보고서 API** - 리포트 생성
