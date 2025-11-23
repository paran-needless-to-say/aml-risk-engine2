# 최종 API 스펙 (Multi-Hop 지원)

## 요약

리스크 스코어링 API의 최종 request 형식입니다. **2가지 모드**를 지원합니다:

1. **기본 모드** (1-hop): 프론트엔드가 `transactions` 제공 (기존 방식)
2. **Multi-hop 모드**: 백엔드가 `transactions` 자동 수집 (신규 방식)

---

## 📝 최종 Request 형식

### 옵션 A: 기본 모드 (1-hop, 기존 방식)

**프론트엔드가 `transactions` 제공**

```json
POST /api/analyze/address

{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [
    {
      "tx_hash": "0x123...",
      "chain_id": 1,
      "timestamp": "2025-11-17T12:34:56Z",
      "block_height": 21039493,
      "target_address": "0xTarget",
      "counterparty_address": "0xMixer1",
      "label": "mixer",
      "is_sanctioned": false,
      "is_known_scam": false,
      "is_mixer": true,
      "is_bridge": false,
      "amount_usd": 5000.0,
      "asset_contract": "0xETH"
    }
  ],
  "analysis_type": "basic"  // 선택 (기본값: "basic")
}
```

**특징**:

- 빠른 응답 (1-2초)
- 1-hop 분석만 가능
- 기존 시스템과 완전 호환

---

### 옵션 B: Multi-hop 모드 (신규 방식) - 권장

**백엔드가 `transactions` 자동 수집**

```json
POST /api/analyze/address

{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3,  // 🆕 필수: 최대 홉 수 (1~3)
  "analysis_type": "advanced",  // 🆕 필수: "advanced"
  "time_window_hours": 24  // 선택: 최근 N시간 거래만 수집
}
```

**특징**:

- 정확한 분석 (3-8초, 캐싱 시)
- Multi-hop 그래프 패턴 탐지 가능
- B-201 (Layering Chain), B-202 (Cycle) 룰 활성화
- 백엔드에서 구현 필요

---

## 📊 파라미터 상세

### 필수 파라미터

| 파라미터   | 타입    | 설명           | 예시           |
| ---------- | ------- | -------------- | -------------- |
| `address`  | string  | 분석 대상 주소 | `"0xTarget"`   |
| `chain_id` | integer | 체인 ID (숫자) | `1` (Ethereum) |

### 선택 파라미터

| 파라미터            | 타입    | 기본값    | 설명                              |
| ------------------- | ------- | --------- | --------------------------------- |
| `transactions`      | array   | -         | 거래 히스토리 (옵션 A에서 필수)   |
| `max_hops`          | integer | `1`       | 최대 홉 수 (1~3, 옵션 B에서 필수) |
| `analysis_type`     | string  | `"basic"` | `"basic"` 또는 `"advanced"`       |
| `time_window_hours` | integer | -         | 최근 N시간 거래만 수집            |
| `time_range`        | object  | -         | 시간 범위 필터                    |

---

## 🔄 백엔드 구현 로직 (옵션 B)

### Request 처리

```python
@app.route("/api/analyze/address", methods=["POST"])
def analyze_address():
    data = request.get_json()

    address = data.get("address")  # 필수
    chain_id = data.get("chain_id")  # 필수
    max_hops = data.get("max_hops", 1)  # 기본값: 1
    analysis_type = data.get("analysis_type", "basic")

    # 옵션 A: 프론트엔드가 transactions 제공
    if "transactions" in data:
        transactions = data["transactions"]

    # 옵션 B: 백엔드가 수집
    else:
        if max_hops > 1:
            transactions = collect_multi_hop_transactions(
                address,
                chain_id,
                max_hops
            )
        else:
            transactions = collect_single_hop_transactions(
                address,
                chain_id
            )

    # 분석 수행
    result = analyze(address, chain_id, transactions, analysis_type)
    return jsonify(result)
```

### Multi-hop 수집 로직

```python
def collect_multi_hop_transactions(address, chain_id, max_hops):
    """
    재귀적으로 multi-hop 거래 수집

    Returns:
        List[Dict]: 각 거래에 hop_level 포함
    """
    all_transactions = []
    visited = set()
    current_level = {address}

    for hop in range(1, max_hops + 1):
        next_level = set()

        for addr in current_level:
            if addr in visited:
                continue

            # Etherscan/Alchemy API 호출
            txs = fetch_transactions(addr, chain_id, limit=100)

            for tx in txs:
                # hop_level 추가
                tx["hop_level"] = hop

                # from, to 명확히 설정
                tx["from"] = addr
                tx["to"] = tx.get("counterparty")

                all_transactions.append(tx)

                # 다음 홉 주소 수집
                counterparty = tx["to"] if tx["from"] == addr else tx["from"]
                next_level.add(counterparty)

            visited.add(addr)

        current_level = next_level

        # 성능 제한
        if len(current_level) > 50:
            break

    return all_transactions
```

---

## 📤 Response (공통)

**응답 형식은 동일합니다** (옵션 A, B 모두):

```json
{
  "target_address": "0xTarget",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "layering_chain", "sanction_exposure"],
  "fired_rules": [
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "B-201", "score": 40 }, // Multi-hop에서만 발동
    { "rule_id": "C-001", "score": 30 }
  ],
  "explanation": "Mixer Direct Exposure 패턴 감지, Layering Chain 패턴 감지...",
  "completed_at": "2025-11-21T10:00:00Z",
  "timestamp": "2025-11-17T12:34:56Z",
  "chain_id": 1,
  "value": 5000.0
}
```

---

## 🔍 거래 데이터 구조

### 옵션 A (기존 필드)

```json
{
  "tx_hash": "0x123...",
  "chain_id": 1,
  "timestamp": "2025-11-17T12:34:56Z",
  "block_height": 21039493,
  "target_address": "0xTarget", // 누구를 분석하는지
  "counterparty_address": "0xMixer1", // 누구와 거래했는지
  "label": "mixer",
  "is_sanctioned": false,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 5000.0,
  "asset_contract": "0xETH"
}
```

### 옵션 B (Multi-hop 필드) - 권장

```json
{
  "tx_hash": "0x123...",
  "chain_id": 1,
  "timestamp": "2025-11-17T12:34:56Z",
  "block_height": 21039493,
  "hop_level": 1, // 🆕 몇 번째 홉인지
  "from": "0xTarget", // 🆕 명확: 송신자
  "to": "0xMixer1", // 🆕 명확: 수신자
  "label": "mixer",
  "is_sanctioned": false,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 5000.0,
  "asset_contract": "0xETH"
}
```

**호환성**:

- `target_address`, `counterparty_address`도 계속 지원 (하위 호환성)
- `from`, `to`가 우선적으로 사용됨

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

## 사용 시나리오

### 시나리오 1: 실시간 대시보드 (빠른 분석)

**요구사항**: 빠른 응답 필요, 1-hop 분석으로 충분

```json
{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [...],  // 프론트엔드 제공
  "analysis_type": "basic"
}
```

**응답 시간**: 1-2초

---

### 시나리오 2: 수동 조사 (정밀 분석)

**요구사항**: 정확도 중요, 복잡한 패턴 탐지 필요

```json
{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3, // 백엔드가 수집
  "analysis_type": "advanced"
}
```

**응답 시간**: 3-8초 (캐싱 시), 10-30초 (캐싱 없음)

---

### 시나리오 3: 최근 24시간 활동 분석

```json
{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 2,
  "time_window_hours": 24, // 최근 24시간만
  "analysis_type": "advanced"
}
```

---

## 중요 사항

### 1. 하위 호환성

**기존 API 호출은 그대로 작동합니다**:

```json
// 이전 방식 (여전히 작동)
{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [...]
}
```

### 2. 필수 구현 사항 (백엔드)

- [ ] `max_hops` 파라미터 처리
- [ ] Multi-hop 거래 수집 로직
- [ ] `hop_level` 필드 추가
- [ ] `from`, `to` 필드 설정
- [ ] 캐싱 구현 (권장)

### 3. 성능 제한

- 최대 홉: 3
- 최대 주소 수: 50 (홉당)
- 최대 거래 수: 500 (전체)
- 타임아웃: 30초

### 4. Rate Limiting

- Etherscan Free: 5 calls/sec
- 해결: API 키 로테이션 또는 유료 플랜

---

## 성능 비교

| 모드               | 응답 시간 | 홉 수 | 그래프 패턴 탐지 | 사용 예시       |
| ------------------ | --------- | ----- | ---------------- | --------------- |
| 기본 (옵션 A)      | 1-2초     | 1-hop | 불가능           | 실시간 대시보드 |
| Multi-hop (옵션 B) | 3-8초     | 3-hop | 가능             | 수동 조사       |

---

## 🧪 테스트 예시

### cURL - 기본 모드

```bash
curl -X POST http://localhost:5001/api/analyze/address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xTarget",
    "chain_id": 1,
    "transactions": [
      {
        "tx_hash": "0x123...",
        "chain_id": 1,
        "timestamp": "2025-11-17T12:34:56Z",
        "block_height": 21039493,
        "target_address": "0xTarget",
        "counterparty_address": "0xMixer1",
        "label": "mixer",
        "is_sanctioned": false,
        "is_known_scam": false,
        "is_mixer": true,
        "is_bridge": false,
        "amount_usd": 5000.0,
        "asset_contract": "0xETH"
      }
    ]
  }'
```

### cURL - Multi-hop 모드

```bash
curl -X POST http://localhost:5001/api/analyze/address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xTarget",
    "chain_id": 1,
    "max_hops": 3,
    "analysis_type": "advanced"
  }'
```

---

## 관련 문서

- [MULTI_HOP_REQUIREMENT.md](./MULTI_HOP_REQUIREMENT.md) - 상세 요구사항
- [BACKEND_REQUEST_MULTI_HOP.md](./BACKEND_REQUEST_MULTI_HOP.md) - 백엔드 구현 가이드
- [SIMPLE_COMPARISON_1HOP_VS_MULTIHOP.md](./SIMPLE_COMPARISON_1HOP_VS_MULTIHOP.md) - 간단 비교
- [PARAMETER_CHANGES_SUMMARY.md](./PARAMETER_CHANGES_SUMMARY.md) - 파라미터 변경 요약

---

**작성일**: 2025-11-21  
**버전**: 1.0  
**상태**: Final Spec
