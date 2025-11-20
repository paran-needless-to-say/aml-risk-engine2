# 올바른 입력 포맷 가이드

이상거래 탐지를 위한 정확한 API 입력 형식입니다.

## ✅ 올바른 입력 형식

### 주소 분석 API (`POST /api/analyze/address`)

```json
{
  "address": "0xabc123...", // 필수: 분석 대상 주소
  "chain_id": 1, // 필수: 체인 ID (숫자)
  "transactions": [
    // 필수: 거래 히스토리 배열
    {
      "tx_hash": "0x123...", // 필수
      "chain_id": 1, // 필수: 숫자 (1=Ethereum)
      "timestamp": "2025-11-17T12:34:56Z", // 필수: ISO8601 UTC
      "block_height": 21039493, // 필수: 정수
      "target_address": "0xabc123...", // 필수: 스코어링 대상 주소
      "counterparty_address": "0xdef456...", // 필수: 상대방 주소
      "label": "mixer", // 필수: mixer|bridge|cex|dex|defi|unknown
      "is_sanctioned": true, // 필수: boolean
      "is_known_scam": false, // 필수: boolean
      "is_mixer": true, // 필수: boolean
      "is_bridge": false, // 필수: boolean
      "amount_usd": 500000.0, // 필수: 숫자 (USD)
      "asset_contract": "0xETH" // 필수: 자산 컨트랙트 주소
    }
  ],
  "analysis_type": "basic" // 선택: "basic" 또는 "advanced" (기본값: "basic")
}
```

### 단일 트랜잭션 스코어링 (`POST /api/score/transaction`)

```json
{
  "tx_hash": "0x123...", // 필수
  "chain_id": 1, // 필수: 숫자
  "timestamp": "2025-11-17T12:34:56Z", // 필수
  "block_height": 21039493, // 필수
  "target_address": "0xabc123...", // 필수
  "counterparty_address": "0xdef456...", // 필수
  "label": "mixer", // 필수
  "is_sanctioned": true, // 필수
  "is_known_scam": false, // 필수
  "is_mixer": true, // 필수
  "is_bridge": false, // 필수
  "amount_usd": 500000.0, // 필수
  "asset_contract": "0xETH" // 필수
}
```

---

## 🔑 핵심 포인트

### 1. chain_id는 항상 숫자

❌ **잘못된 예**:

```json
{
  "chain_id": "ETH", // 문자열 ❌
  "chain": "ethereum" // 문자열 ❌
}
```

✅ **올바른 예**:

```json
{
  "chain_id": 1 // 숫자 ✅
}
```

### 2. transactions 배열 내부도 chain_id (숫자)

```json
{
  "transactions": [
    {
      "chain_id": 1,     // ✅ 숫자
      ...
    }
  ]
}
```

### 3. 필수 필드 확인

**최상위 레벨**:

- `address` (필수)
- `chain_id` (숫자, 필수)
- `transactions` (배열, 필수)

**transactions 배열 내부 각 객체**:

- `tx_hash`
- `chain_id` (숫자)
- `timestamp`
- `block_height`
- `target_address`
- `counterparty_address`
- `label`
- `is_sanctioned`
- `is_known_scam`
- `is_mixer`
- `is_bridge`
- `amount_usd`
- `asset_contract`

---

## 📋 체인 ID 매핑

| Chain ID | 체인 이름         |
| -------- | ----------------- |
| `1`      | Ethereum Mainnet  |
| `42161`  | Arbitrum One      |
| `43114`  | Avalanche C-Chain |
| `8453`   | Base Mainnet      |
| `137`    | Polygon Mainnet   |
| `56`     | BSC Mainnet       |
| `250`    | Fantom Opera      |
| `10`     | Optimism Mainnet  |
| `81457`  | Blast Mainnet     |

---

## 🧪 테스트 예시

### High Risk 시나리오 (Mixer + 제재 주소)

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

**예상 결과**: `risk_score: 70-98`, `risk_level: "high"` 또는 `"critical"`

---

## ⚠️ 주의사항

1. **chain_id는 항상 숫자**: 문자열("ETH")이 아닌 숫자(1)로 보내야 합니다
2. **transactions 배열 내부도 chain_id**: 각 트랜잭션 객체에도 `chain_id`가 필요합니다
3. **모든 필수 필드 포함**: 필수 필드가 하나라도 빠지면 400 에러가 발생합니다
4. **timestamp 형식**: ISO8601 UTC 형식 (`"2025-11-17T12:34:56Z"`)

---

## 🔍 Swagger UI와 실제 요청 비교

**Swagger UI 예시**와 **실제 요청**은 동일한 형식입니다:

- ✅ `chain_id`: 숫자 (1, 42161 등)
- ✅ `transactions`: 배열
- ✅ 각 트랜잭션 객체 내부도 `chain_id` (숫자)

**차이점이 있다면**:

- Swagger UI의 예시 값은 단순 예시일 수 있습니다
- 실제 요청은 위의 형식을 정확히 따라야 합니다

---

## 💡 빠른 확인

테스트 파일을 사용하세요:

- `test_api.json` - 주소 분석 테스트
- `test_single_transaction.json` - 단일 트랜잭션 테스트

이 파일들은 올바른 형식으로 작성되어 있습니다.
