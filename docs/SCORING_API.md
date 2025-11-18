# 트랜잭션 스코어링 API

백엔드에서 제공하는 트랜잭션 정보를 기반으로 AML 스코어링을 수행하는 API입니다.

## 엔드포인트

```
POST /api/score/transaction
```

## Request Body

```json
{
  "tx_hash": "0x1234...",
  "chain": "ethereum",
  "timestamp": "2025-11-17T12:34:56Z",
  "block_height": 21039493,
  "target_address": "0xabc...",
  "counterparty_address": "0xdef...",
  "label": "mixer",
  "is_sanctioned": true,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 123.45,
  "asset_contract": "0x..."
}
```

### 필드 설명

- `tx_hash`: 트랜잭션 해시
- `chain`: 블록체인 (ethereum, bsc, polygon)
- `timestamp`: ISO8601 UTC 형식의 타임스탬프
- `block_height`: 블록 높이 (정렬용)
- `target_address`: 스코어링 대상 주소
- `counterparty_address`: 상대방 주소 (3-hop까지 고려)
- `label`: 엔티티 라벨 (mixer | bridge | cex | dex | defi | unknown, 백엔드에서 라벨링)
- `is_sanctioned`: OFAC 제재 리스트 매핑 결과
- `is_known_scam`: 사기/피싱 블랙리스트 매핑 결과
- `is_mixer`: 믹서 여부 (label에서 파생)
- `is_bridge`: 브릿지 여부 (label에서 파생)
- `amount_usd`: USD 환산 금액
- `asset_contract`: 자산 컨트랙트 주소

## Response

```json
{
  "target_address": "0xabc...",
  "risk_score": 78.0,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "sanction_exposure", "high_value_transfer"],
  "fired_rules": [
    { "rule_id": "MIXER_INFLOW_1HOP", "score": 50 },
    { "rule_id": "SANCTIONED_ENTITY", "score": 40 },
    { "rule_id": "AMOUNT_OVER_1000_USD", "score": 20 }
  ],
  "explanation": "1-hop mixer에서 1,000USD 유입, 제재 대상과 거래, 고액 거래 (1,000USD)로 인해 high로 분류됨.",
  "completed_at": "2025-11-17T12:34:56Z"
}
```

### 필드 설명

- `target_address`: 스코어링 대상 주소
- `risk_score`: 리스크 점수 (0~100)
- `risk_level`: 리스크 레벨 (low | medium | high | critical)
- `risk_tags`: 위험 태그 목록
- `fired_rules`: 발동된 룰 목록 (rule_id, score)
- `explanation`: 스코어링 결과 설명
- `completed_at`: 스코어링 완료 시각 (ISO8601 UTC 형식)

## Risk Level 기준

- `critical`: 80점 이상
- `high`: 60점 이상
- `medium`: 30점 이상
- `low`: 30점 미만

## 스코어링 룰

현재 구현된 룰:

1. **MIXER_INFLOW_1HOP** (50점)

   - 조건: `is_mixer == true`
   - 태그: `mixer_inflow`

2. **SANCTIONED_ENTITY** (40점)

   - 조건: `is_sanctioned == true`
   - 태그: `sanction_exposure`

3. **AMOUNT_OVER_1000_USD** (20점)

   - 조건: `amount_usd >= 1000`
   - 태그: `high_value_transfer`

4. **KNOWN_SCAM** (60점)

   - 조건: `is_known_scam == true`
   - 태그: `scam_exposure`

5. **BRIDGE_LARGE_AMOUNT** (30점)

   - 조건: `is_bridge == true && amount_usd >= 5000`
   - 태그: `bridge_large_transfer`

6. **CEX_INFLOW** (10점)
   - 조건: `label == "cex"`
   - 태그: `cex_inflow`

## 사용 예시

### Python

```python
import requests

url = "http://localhost:5000/api/score/transaction"
data = {
    "tx_hash": "0x1234...",
    "chain": "ethereum",
    "timestamp": "2025-11-17T12:34:56Z",
    "block_height": 21039493,
    "target_address": "0xabc...",
    "counterparty_address": "0xdef...",
    "label": "mixer",
    "is_sanctioned": True,
    "is_known_scam": False,
    "is_mixer": True,
    "is_bridge": False,
    "amount_usd": 1234.56,
    "asset_contract": "0x..."
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### cURL

```bash
curl -X POST http://localhost:5000/api/score/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0x1234...",
    "chain": "ethereum",
    "timestamp": "2025-11-17T12:34:56Z",
    "block_height": 21039493,
    "target_address": "0xabc...",
    "counterparty_address": "0xdef...",
    "label": "mixer",
    "is_sanctioned": true,
    "is_known_scam": false,
    "is_mixer": true,
    "is_bridge": false,
    "amount_usd": 1234.56,
    "asset_contract": "0x..."
  }'
```

## 구현 파일

- `api/score_transaction.py`: 스코어링 로직 구현
- Flask/FastAPI 서버로 래핑하여 사용
