# 1-Hop vs Multi-Hop: 간단 비교

## 📊 한눈에 보는 차이

### 현재 시스템 (1-hop)

```
Target 주소만 분석
    ↓
[Target ↔ A]
[Target ↔ B]
[Target ↔ C]
    ↓
❌ A, B, C가 서로 어떻게 연결되어 있는지 모름
❌ Layering Chain, Cycle 패턴 탐지 불가능
```

### 필요한 시스템 (Multi-hop)

```
Target + Counterparty 주소들도 분석
    ↓
[Target → A → X → Y]  ← 3-hop 경로 추적 가능!
[Target → B → C → Target]  ← Cycle 탐지 가능!
    ↓
✅ 전체 거래 흐름 파악
✅ 복잡한 세탁 패턴 탐지
```

---

## 🎯 백엔드가 해야 할 일

### Before (현재)

```python
# Target의 거래만 가져오기
transactions = get_transactions(target_address)
return {"transactions": transactions}
```

### After (Multi-hop)

```python
# Target + Counterparty들의 거래도 가져오기
all_transactions = []

# 1-hop: Target의 거래
target_txs = get_transactions(target_address)
all_transactions.extend(target_txs)

# 2-hop: Counterparty들의 거래
for tx in target_txs:
    counterparty = tx["to"] if tx["from"] == target_address else tx["from"]
    counterparty_txs = get_transactions(counterparty)
    all_transactions.extend(counterparty_txs)

# 3-hop: 2-hop의 counterparty들의 거래
# (위와 동일하게 반복)

return {"transactions": all_transactions}
```

---

## 📝 API 변경 요약

### Request (요청)

**Before**:

```json
POST /api/analyze/address
{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [...]  ← 프론트엔드가 보냄
}
```

**After**:

```json
POST /api/analyze/address
{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3  ← 백엔드가 알아서 수집
}
```

**핵심 변경**: `transactions` 필드를 **백엔드가 수집**하도록 변경

---

### Response (응답)

**변경 없음!** 기존 응답 형식 그대로 사용:

```json
{
  "target_address": "0xTarget",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "layering_chain"],
  "fired_rules": [...]
}
```

---

## 🔍 실제 예시

### 시나리오: Mixer를 통한 자금 세탁

#### 실제 거래 흐름

```
Target → Mixer1 (5000 USD)
    → Mixer2 (4950 USD)
        → Clean Address (4900 USD)
            → CEX (4850 USD)
```

#### 1-hop 시스템 (현재)

**수집되는 데이터**:

```json
[{ "from": "0xTarget", "to": "0xMixer1", "amount_usd": 5000 }]
```

**탐지 결과**:

- ✅ E-101 (Mixer 유입) 발동 → 점수 25
- ❌ B-201 (Layering Chain) **탐지 못함**
- **최종 점수**: 25 (low)

#### Multi-hop 시스템 (필요한 것)

**수집되는 데이터**:

```json
[
  { "hop_level": 1, "from": "0xTarget", "to": "0xMixer1", "amount_usd": 5000 },
  { "hop_level": 2, "from": "0xMixer1", "to": "0xMixer2", "amount_usd": 4950 },
  { "hop_level": 3, "from": "0xMixer2", "to": "0xClean", "amount_usd": 4900 }
]
```

**탐지 결과**:

- ✅ E-101 (Mixer 유입) 발동 → 점수 25
- ✅ B-201 (Layering Chain) **발동!** → 점수 40
- **최종 점수**: 65 (high)

**차이**: 25점 → 65점 (160% 증가!)

---

## ⚙️ 구현 체크리스트

### 백엔드 팀 TODO

#### [ ] 1. API 파라미터 추가

```python
@app.route("/api/analyze/address", methods=["POST"])
def analyze_address():
    address = request.json.get("address")
    chain_id = request.json.get("chain_id")
    max_hops = request.json.get("max_hops", 1)  # 기본값: 1

    # max_hops에 따라 수집
    transactions = collect_transactions(address, chain_id, max_hops)
    ...
```

#### [ ] 2. 재귀적 거래 수집

```python
def collect_transactions(address, chain_id, max_hops):
    all_txs = []
    visited = set()
    current_level = {address}

    for hop in range(1, max_hops + 1):
        next_level = set()
        for addr in current_level:
            if addr in visited:
                continue

            txs = etherscan_api.get_transactions(addr, chain_id)
            for tx in txs:
                tx["hop_level"] = hop
                all_txs.append(tx)

                # 다음 홉 주소 추가
                counterparty = tx["to"] if tx["from"] == addr else tx["from"]
                next_level.add(counterparty)

            visited.add(addr)

        current_level = next_level

    return all_txs
```

#### [ ] 3. 캐싱 (성능 최적화)

```python
import redis
redis_client = redis.Redis()

def get_transactions_cached(address, chain_id):
    cache_key = f"txs:{address}:{chain_id}"

    # 캐시 확인
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # API 호출
    txs = etherscan_api.get_transactions(address, chain_id)

    # 캐싱 (1시간)
    redis_client.setex(cache_key, 3600, json.dumps(txs))

    return txs
```

#### [ ] 4. Rate Limiting 처리

```python
import time
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=5, period=1)  # 5 calls/sec
def call_etherscan_api(address, chain_id):
    return etherscan_api.get_transactions(address, chain_id)
```

---

## 🚨 주의사항

### 1. 성능 제한

- **최대 홉**: 3 (더 많으면 너무 느림)
- **최대 주소 수**: 50 (홉당)
- **타임아웃**: 30초

### 2. Rate Limiting

- Etherscan Free: 5 calls/sec
- 해결: 유료 플랜 또는 API 키 로테이션

### 3. 하위 호환성

```python
# 기본값은 1-hop (기존 동작)
max_hops = request.json.get("max_hops", 1)

if max_hops == 1:
    # 기존 로직 (빠름)
    transactions = get_transactions(address, chain_id)
else:
    # Multi-hop (느림)
    transactions = collect_multi_hop(address, chain_id, max_hops)
```

---

## 💰 비용-효과 분석

### 개발 비용

- **예상 개발 시간**: 1-2주
- **난이도**: 중간 (재귀 로직 + 캐싱)
- **유지보수**: 낮음 (안정적인 로직)

### 효과

- **리스크 탐지 정확도**: 30-50% 향상
- **새로운 룰 활성화**: B-201, B-202 (현재 작동 안 함)
- **사용자 만족도**: 높음 (더 정확한 분석)

### ROI (투자 대비 효과)

```
투자: 2주 개발 시간
효과: 리스크 탐지 정확도 30-50% 향상
      → False Positive 감소
      → 사용자 신뢰도 증가

ROI: 매우 높음 ★★★★★
```

---

## 📞 질문 있으신가요?

### Q1: 왜 꼭 필요한가요?

**A**: 현재 시스템은 복잡한 세탁 패턴을 탐지하지 못합니다. Multi-hop 없이는 B-201, B-202 룰이 **전혀 작동하지 않습니다**.

### Q2: 너무 느려지지 않을까요?

**A**: 캐싱을 쓰면 3-8초로 단축 가능합니다. 또한 `analysis_type="basic"` (기본값)일 때는 1-hop만 수집하여 기존 속도 유지.

### Q3: 기존 API가 깨지나요?

**A**: 아니요, 완전히 하위 호환됩니다. `max_hops` 파라미터가 없으면 기존대로 1-hop만 수집합니다.

---

**다음 단계**:

1. 이 문서를 백엔드 팀과 공유
2. 구현 스케줄 논의 (추천: 2주)
3. Phase 1 구현 → Phase 2 최적화

**관련 문서**:

- [MULTI_HOP_REQUIREMENT.md](./MULTI_HOP_REQUIREMENT.md) - 상세 스펙
- [BACKEND_REQUEST_MULTI_HOP.md](./BACKEND_REQUEST_MULTI_HOP.md) - 구현 가이드
