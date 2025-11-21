# 리스크 스코어링 파라미터 변경사항

## 🎯 질문: "리스크 스코어링 파라미터가 바뀌어야 하나요?"

### 답변: **네, 확장됩니다** (기존 파라미터 유지 + 신규 추가)

---

## 📊 파라미터 변경 요약

### ✅ 유지되는 것 (변경 없음)

- 기본 입력: `address`, `chain_id`
- 거래 필드: `tx_hash`, `timestamp`, `amount_usd`, 등
- 출력 형식: `risk_score`, `risk_level`, `fired_rules`, 등

### 🆕 추가되는 것 (신규)

- 입력: `max_hops` (선택, 기본값: 1)
- 거래 필드: `hop_level` (몇 번째 홉인지)
- 거래 필드: `from`, `to` (명확한 방향성)

### ⚠️ 변경되는 것 (기존 필드 개선)

- 기존: `counterparty_address`, `target_address` (모호함)
- 신규: `from`, `to` (명확함)

---

## 📝 상세 변경사항

### 1. API 요청 파라미터 (Request)

#### Before (기존)

```json
POST /api/analyze/address
{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [
    {
      "target_address": "0xTarget",
      "counterparty_address": "0xMixer1",
      "amount_usd": 5000.0,
      ...
    }
  ],
  "analysis_type": "basic"
}
```

**문제점**:

- `target_address` vs `counterparty_address`: 누가 보낸 건지, 받은 건지 모호함
- `transactions`를 프론트엔드가 제공 → 백엔드 로직 부족

---

#### After (Multi-hop)

```json
POST /api/analyze/address
{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3,  // 🆕 추가 (선택, 기본값: 1)
  "analysis_type": "advanced"
}
```

**개선사항**:

- `transactions`를 **백엔드가 수집** (프론트엔드 부담 감소)
- `max_hops`로 수집 범위 제어

---

### 2. 거래 데이터 구조 (Transaction Object)

#### Before (기존)

```json
{
  "tx_hash": "0x123...",
  "chain_id": 1,
  "timestamp": "2025-11-17T12:34:56Z",
  "target_address": "0xTarget",        // 모호함
  "counterparty_address": "0xMixer1",  // 모호함
  "amount_usd": 5000.0,
  "label": "mixer",
  "is_sanctioned": false,
  "is_mixer": true,
  ...
}
```

**문제점**:

- `Target → Mixer1`인지, `Mixer1 → Target`인지 불명확
- 그래프 구조 파악 불가

---

#### After (Multi-hop)

```json
{
  "tx_hash": "0x123...",
  "chain_id": 1,
  "timestamp": "2025-11-17T12:34:56Z",
  "hop_level": 1,         // 🆕 추가: 몇 번째 홉인지
  "from": "0xTarget",     // 🆕 명확: 송신자
  "to": "0xMixer1",       // 🆕 명확: 수신자
  "amount_usd": 5000.0,
  "label": "mixer",
  "is_sanctioned": false,
  "is_mixer": true,
  ...
}
```

**개선사항**:

- `from`, `to`로 방향성 명확
- `hop_level`로 깊이 파악
- 그래프 구조 구축 가능

---

### 3. API 응답 (Response)

#### 변경 없음!

기존 응답 형식 그대로 유지:

```json
{
  "target_address": "0xTarget",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "layering_chain"],
  "fired_rules": [
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "B-201", "score": 40 }
  ],
  "explanation": "...",
  "completed_at": "2025-11-21T10:00:00Z",
  "timestamp": "2025-11-17T12:34:56Z",
  "chain_id": 1,
  "value": 5000.0
}
```

**포인트**: 응답 형식은 그대로, 내부 로직만 개선

---

## 🔄 마이그레이션 가이드

### Phase 1: 하위 호환성 유지 (추천)

#### 백엔드 로직

```python
@app.route("/api/analyze/address", methods=["POST"])
def analyze_address():
    data = request.get_json()

    address = data.get("address")
    chain_id = data.get("chain_id")
    max_hops = data.get("max_hops", 1)  # 기본값: 1 (기존 동작)
    analysis_type = data.get("analysis_type", "basic")

    # 기존 방식 (프론트엔드가 transactions 제공)
    if "transactions" in data:
        transactions = data["transactions"]
    # 신규 방식 (백엔드가 수집)
    else:
        transactions = collect_transactions(
            address,
            chain_id,
            max_hops=max_hops
        )

    # 나머지 로직은 동일
    result = analyze(address, chain_id, transactions)
    return jsonify(result)
```

**장점**:

- 기존 API 호출 방식 유지
- 신규 기능 점진적 도입

---

### Phase 2: 필드 정규화

#### 거래 데이터 정규화 함수

```python
def normalize_transaction(tx, target_address):
    """
    기존 포맷 → 신규 포맷 변환
    """
    # 기존 필드 지원
    from_addr = tx.get("from") or (
        tx.get("target_address")
        if tx.get("counterparty_address")
        else tx.get("counterparty_address")
    )
    to_addr = tx.get("to") or (
        tx.get("counterparty_address")
        if tx.get("target_address") == target_address
        else tx.get("target_address")
    )

    return {
        "tx_hash": tx.get("tx_hash"),
        "chain_id": tx.get("chain_id"),
        "timestamp": tx.get("timestamp"),
        "hop_level": tx.get("hop_level", 1),  # 기본값: 1
        "from": from_addr,
        "to": to_addr,
        "amount_usd": tx.get("amount_usd"),
        "label": tx.get("label"),
        "is_sanctioned": tx.get("is_sanctioned"),
        "is_mixer": tx.get("is_mixer"),
        ...
    }
```

---

## 📋 파라미터 비교표

| 파라미터        | 기존 (1-hop) | Multi-hop | 변경 유형 | 기본값      |
| --------------- | ------------ | --------- | --------- | ----------- |
| `address`       | ✅           | ✅        | 유지      | -           |
| `chain_id`      | ✅           | ✅        | 유지      | -           |
| `transactions`  | ✅ (필수)    | ⚠️ (선택) | 변경      | 백엔드 수집 |
| `max_hops`      | ❌           | ✅ (선택) | 신규      | 1           |
| `analysis_type` | ✅           | ✅        | 유지      | "basic"     |
| `time_range`    | ✅           | ✅        | 유지      | null        |

### 거래 필드

| 필드                   | 기존 (1-hop) | Multi-hop       | 변경 유형 | 필수 여부 |
| ---------------------- | ------------ | --------------- | --------- | --------- |
| `tx_hash`              | ✅           | ✅              | 유지      | 필수      |
| `timestamp`            | ✅           | ✅              | 유지      | 필수      |
| `target_address`       | ✅           | ⚠️ (Deprecated) | 변경      | 선택      |
| `counterparty_address` | ✅           | ⚠️ (Deprecated) | 변경      | 선택      |
| `from`                 | ❌           | ✅              | 신규      | 필수      |
| `to`                   | ❌           | ✅              | 신규      | 필수      |
| `hop_level`            | ❌           | ✅              | 신규      | 필수      |
| `amount_usd`           | ✅           | ✅              | 유지      | 필수      |
| `label`                | ✅           | ✅              | 유지      | 필수      |

---

## 🔧 구현 체크리스트

### 백엔드 팀

- [ ] `max_hops` 파라미터 추가 및 처리
- [ ] 재귀적 거래 수집 로직 구현
- [ ] `from`, `to` 필드 생성 로직
- [ ] `hop_level` 계산 및 할당
- [ ] 하위 호환성 유지 (기존 필드 지원)
- [ ] 캐싱 구현 (성능 최적화)

### 프론트엔드 팀 (선택)

- [ ] `max_hops` 파라미터 추가 (UI에서 선택)
- [ ] `transactions` 필드 제거 (백엔드가 처리)
- [ ] 로딩 UI 개선 (응답 시간 증가 대비)

### 리스크 스코어링 엔진 (우리 팀)

- [x] `from`, `to` 필드 지원 (이미 구현됨)
- [x] `hop_level` 활용 (그래프 구축)
- [x] 하위 호환성 유지 (기존 필드도 지원)

---

## ⚠️ 주의사항

### 1. Breaking Changes 없음

- 기존 API 호출 방식 **100% 호환**
- `max_hops` 없으면 기존대로 1-hop만 수집
- `transactions` 제공하면 백엔드 수집 생략

### 2. 점진적 마이그레이션

- Phase 1: 하위 호환성 유지 (2주)
- Phase 2: 필드 정규화 권장 (4주)
- Phase 3: 구 필드 Deprecated 경고 (8주)

### 3. 문서 업데이트

- [ ] CORRECT_INPUT_FORMAT.md 업데이트
- [ ] RISK_SCORING_IO.md 업데이트
- [ ] API 문서 (Swagger) 업데이트

---

## 💡 요약

### 리스크 스코어링 파라미터가 바뀌나요?

**네, 확장됩니다:**

1. **신규 입력 파라미터**:

   - `max_hops` (선택, 기본값: 1)

2. **신규 거래 필드**:

   - `hop_level` (몇 번째 홉)
   - `from`, `to` (명확한 방향성)

3. **Deprecated 필드**:

   - `target_address`, `counterparty_address` → `from`, `to`로 대체

4. **기존 파라미터**:

   - **모두 유지됨** (하위 호환성)

5. **응답 형식**:
   - **변경 없음**

**결론**: 기존 시스템을 깨지 않으면서, 신규 기능 추가

---

**작성일**: 2025-11-21  
**버전**: 1.0
