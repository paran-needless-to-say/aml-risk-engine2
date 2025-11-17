# API 명세서

AML Risk Engine API 문서입니다. Swagger UI를 통해 인터랙티브하게 API를 테스트할 수 있습니다.

## 📚 API 문서 접속

서버 실행 후 브라우저에서 접속:

```
http://localhost:5000/api-docs
```

## 🚀 서버 실행

```bash
python3 api/app.py
```

## 📡 엔드포인트

### 1. Manual Analysis (수동 탐지)

#### POST /api/analyze/address

주소의 거래 히스토리를 분석하여 리스크 스코어 계산

**Request Body:**

```json
{
  "address": "0xabc123...",
  "chain": "ethereum",
  "transactions": [
    {
      "tx_hash": "string",
      "chain": "string",
      "timestamp": "2025-11-17T12:34:56Z",
      "block_height": 21039493,
      "target_address": "0xabc123...",
      "counterparty_address": "0xdef456...",
      "entity_type": "mixer",
      "is_sanctioned": true,
      "is_known_scam": false,
      "is_mixer": true,
      "is_bridge": false,
      "amount_usd": 123.45,
      "asset_contract": "0x..."
    }
  ]
}
```

**Response:**

```json
{
  "target_address": "0xabc123...",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "sanction_exposure"],
  "fired_rules": [
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "C-001", "score": 30 }
  ],
  "explanation": "..."
}
```

### 2. Transaction Scoring (단일 거래 스코어링)

#### POST /api/score/transaction

단일 트랜잭션의 리스크 분석

**Request Body:**

```json
{
  "tx_hash": "string",
  "chain": "ethereum",
  "timestamp": "2025-11-17T12:34:56Z",
  "block_height": 21039493,
  "target_address": "0xabc123...",
  "counterparty_address": "0xdef456...",
  "entity_type": "mixer",
  "is_sanctioned": true,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 123.45,
  "asset_contract": "0x..."
}
```

**Response:**

```json
{
  "target_address": "0xabc123...",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "sanction_exposure"],
  "fired_rules": [
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "C-001", "score": 30 }
  ],
  "explanation": "..."
}
```

### 3. Health Check

#### GET /health

서버 상태 확인

**Response:**

```json
{
  "status": "ok",
  "service": "aml-risk-engine"
}
```

## 💡 Swagger UI 사용법

1. 서버 실행: `python3 api/app.py`
2. 브라우저에서 `http://localhost:5000/api-docs` 접속
3. 각 엔드포인트를 클릭하여 상세 정보 확인
4. "Try it out" 버튼으로 실제 API 테스트 가능
5. Request Body에 예시 데이터 입력 후 "Execute" 클릭

## 📝 예시 요청

### 주소 분석 API 테스트

```bash
curl -X POST http://localhost:5000/api/analyze/address \
  -H "Content-Type: application/json" \
  -d @demo/api_request_example.json
```

### 트랜잭션 스코어링 API 테스트

```bash
curl -X POST http://localhost:5000/api/score/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0x123...",
    "chain": "ethereum",
    "timestamp": "2025-11-17T12:34:56Z",
    "block_height": 21039493,
    "target_address": "0xabc123...",
    "counterparty_address": "0xdef456...",
    "entity_type": "mixer",
    "is_sanctioned": true,
    "is_known_scam": false,
    "is_mixer": true,
    "is_bridge": false,
    "amount_usd": 5000.0,
    "asset_contract": "0xETH"
  }'
```
