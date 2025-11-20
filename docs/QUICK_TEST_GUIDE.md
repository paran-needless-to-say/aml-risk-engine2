# 빠른 테스트 가이드

API를 빠르게 테스트하는 방법입니다.

## 🚀 서버 실행 확인

```bash
# 서버가 실행 중인지 확인
curl http://localhost:5002/health
```

응답:

```json
{
  "status": "ok",
  "service": "aml-risk-engine"
}
```

---

## 📝 테스트 방법

### 방법 1: Swagger UI (가장 쉬움) ⭐

1. 브라우저에서 접속:

   ```
   http://localhost:5002/api-docs
   ```

2. `POST /api/analyze/address` 클릭

3. "Try it out" 버튼 클릭

4. Request body에 아래 JSON 입력:

   ```json
   {
     "address": "0xhigh_risk_mixer_sanctioned",
     "chain_id": 1,
     "transactions": [
       {
         "tx_hash": "0xtx1_mixer",
         "chain_id": 1,
         "timestamp": "2025-11-15T00:27:17.865209Z",
         "block_height": 1000,
         "target_address": "0xhigh_risk_mixer_sanctioned",
         "counterparty_address": "0xmixer_service_123",
         "label": "mixer",
         "is_sanctioned": false,
         "is_known_scam": false,
         "is_mixer": true,
         "is_bridge": false,
         "amount_usd": 5000.0,
         "asset_contract": "0xETH"
       },
       {
         "tx_hash": "0xtx2_sanctioned",
         "chain_id": 1,
         "timestamp": "2024-01-01T10:30:00Z",
         "block_height": 1001,
         "target_address": "0xhigh_risk_mixer_sanctioned",
         "counterparty_address": "0xsanctioned_address_ofac",
         "label": "unknown",
         "is_sanctioned": true,
         "is_known_scam": false,
         "is_mixer": false,
         "is_bridge": false,
         "amount_usd": 3000.0,
         "asset_contract": "0xETH"
       }
     ],
     "analysis_type": "basic"
   }
   ```

5. "Execute" 클릭

6. 결과 확인!

---

### 방법 2: curl (터미널)

#### 주소 분석 테스트

```bash
curl -X POST http://localhost:5002/api/analyze/address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xhigh_risk_mixer_sanctioned",
    "chain_id": 1,
    "transactions": [
      {
        "tx_hash": "0xtx1_mixer",
        "chain_id": 1,
        "timestamp": "2025-11-15T00:27:17.865209Z",
        "block_height": 1000,
        "target_address": "0xhigh_risk_mixer_sanctioned",
        "counterparty_address": "0xmixer_service_123",
        "label": "mixer",
        "is_sanctioned": false,
        "is_known_scam": false,
        "is_mixer": true,
        "is_bridge": false,
        "amount_usd": 5000.0,
        "asset_contract": "0xETH"
      }
    ],
    "analysis_type": "basic"
  }'
```

#### 단일 트랜잭션 스코어링 테스트

```bash
curl -X POST http://localhost:5002/api/score/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0xtx1_mixer",
    "chain_id": 1,
    "timestamp": "2025-11-15T00:27:17.865209Z",
    "block_height": 1000,
    "target_address": "0xhigh_risk_mixer_sanctioned",
    "counterparty_address": "0xmixer_service_123",
    "label": "mixer",
    "is_sanctioned": false,
    "is_known_scam": false,
    "is_mixer": true,
    "is_bridge": false,
    "amount_usd": 5000.0,
    "asset_contract": "0xETH"
  }'
```

---

### 방법 3: 테스트 파일 사용

프로젝트 루트에 `test_api.json` 파일이 있습니다:

```bash
# 주소 분석 테스트
curl -X POST http://localhost:5002/api/analyze/address \
  -H "Content-Type: application/json" \
  -d @test_api.json

# 단일 트랜잭션 테스트
curl -X POST http://localhost:5002/api/score/transaction \
  -H "Content-Type: application/json" \
  -d @test_single_transaction.json
```

---

## ✅ 예상 결과

### High Risk 주소 테스트

**입력**: Mixer + 제재 주소 + 고액 거래

**예상 결과**:

```json
{
  "target_address": "0xhigh_risk_mixer_sanctioned",
  "risk_score": 98,
  "risk_level": "critical",
  "risk_tags": ["mixer_inflow", "sanction_exposure", "high_value_transfer"],
  "fired_rules": [
    { "rule_id": "E-101", "score": 32 },
    { "rule_id": "C-001", "score": 30 },
    { "rule_id": "C-003", "score": 25 }
  ],
  "chain_id": 1,
  "timestamp": "2025-11-15T00:57:17.865209Z",
  "value": 16000.0
}
```

---

## 🧪 다양한 시나리오 테스트

### 1. Low Risk (정상 거래)

```json
{
  "address": "0xlow_risk_normal",
  "chain_id": 1,
  "transactions": [
    {
      "tx_hash": "0xtx1_cex",
      "chain_id": 1,
      "timestamp": "2025-11-15T00:27:17.865209Z",
      "block_height": 1000,
      "target_address": "0xlow_risk_normal",
      "counterparty_address": "0xbinance_hot_wallet",
      "label": "cex",
      "is_sanctioned": false,
      "is_known_scam": false,
      "is_mixer": false,
      "is_bridge": false,
      "amount_usd": 500.0,
      "asset_contract": "0xETH"
    }
  ]
}
```

**예상**: `risk_score: 0-20`, `risk_level: "low"`

### 2. Medium Risk (고액 거래)

```json
{
  "address": "0xmedium_risk_high_value",
  "chain_id": 1,
  "transactions": [
    {
      "tx_hash": "0xtx1_high",
      "chain_id": 1,
      "timestamp": "2025-11-15T00:27:17.865209Z",
      "block_height": 1000,
      "target_address": "0xmedium_risk_high_value",
      "counterparty_address": "0xnormal_address",
      "label": "unknown",
      "is_sanctioned": false,
      "is_known_scam": false,
      "is_mixer": false,
      "is_bridge": false,
      "amount_usd": 8000.0,
      "asset_contract": "0xETH"
    }
  ]
}
```

**예상**: `risk_score: 20-40`, `risk_level: "medium"`

---

## 💡 테스트 팁

1. **Swagger UI 사용**: 가장 쉽고 직관적
2. **JSON 포맷 확인**: `chain_id`는 숫자로!
3. **에러 확인**: 필수 필드 누락 시 400 에러
4. **응답 확인**: `chain_id`, `timestamp`, `value` 필드 포함 확인

---

## ❓ 문제 해결

### "Method Not Allowed" 에러

- Swagger UI에서 "Try it out" 버튼 사용
- curl로 POST 요청 보내기

### "Missing required field" 에러

- 모든 필수 필드 확인
- `chain_id`가 숫자인지 확인

### 서버가 응답하지 않음

- 서버 실행 확인: `curl http://localhost:5002/health`
- 포트 확인 (5001 또는 5002)

---

**테스트 파일 위치**: 프로젝트 루트의 `test_api.json`, `test_single_transaction.json`
