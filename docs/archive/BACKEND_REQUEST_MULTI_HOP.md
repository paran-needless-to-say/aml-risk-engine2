# 백엔드 팀 요청사항: Multi-Hop 거래 수집

## 🎯 TL;DR (요약)

**문제**: 현재 리스크 스코어링이 1-hop 거래만 분석 → 그래프 패턴 탐지 불가능  
**해결**: Target 주소의 counterparty들의 거래도 수집해서 보내주기 (최대 3-hop)  
**영향**: 리스크 탐지 정확도 30-50% 향상, 새로운 룰 활성화 (Layering Chain, Cycle)

---

## 📊 현재 vs 필요한 데이터

### 현재 (1-hop만)

```json
{
  "target_address": "0xTarget",
  "transactions": [
    {
      "from": "0xTarget",
      "to": "0xMixer1",  // 1-hop만!
      ...
    }
  ]
}
```

**한계**: `Target → Mixer1 → Mixer2 → Clean` 경로를 탐지 못함

---

### 필요한 것 (Multi-hop)

```json
{
  "target_address": "0xTarget",
  "max_hops": 3,
  "transactions": [
    // 1-hop
    {"hop_level": 1, "from": "0xTarget", "to": "0xMixer1", ...},

    // 2-hop (Mixer1의 거래)
    {"hop_level": 2, "from": "0xMixer1", "to": "0xMixer2", ...},

    // 3-hop (Mixer2의 거래)
    {"hop_level": 3, "from": "0xMixer2", "to": "0xClean", ...}
  ]
}
```

**장점**: 전체 경로 분석 가능 → Layering Chain, Cycle 탐지 가능

---

## 🔧 백엔드 구현 가이드

### 1. API 변경사항

#### 기존 엔드포인트

```
POST /api/analyze/address
```

#### 파라미터 추가

```json
{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3, // 🆕 추가 (기본값: 1, 최대: 3)
  "analysis_type": "advanced" // "advanced"일 때만 multi-hop
}
```

**주의**: `transactions` 필드는 이제 **백엔드가 수집**

---

### 2. 수집 로직 (의사코드)

```python
def collect_multi_hop_transactions(target_address, chain_id, max_hops=3):
    """
    Target의 거래 + Counterparty들의 거래를 재귀적으로 수집
    """
    all_transactions = []
    visited = set()
    current_level = {target_address}

    for hop in range(1, max_hops + 1):
        next_level = set()

        for address in current_level:
            if address in visited:
                continue

            # Etherscan/Alchemy API 호출
            txs = fetch_address_transactions(address, chain_id, limit=100)

            for tx in txs:
                # hop_level 추가
                tx["hop_level"] = hop
                all_transactions.append(tx)

                # 다음 레벨 주소 수집
                counterparty = tx["to"] if tx["from"] == address else tx["from"]
                next_level.add(counterparty)

            visited.add(address)

        current_level = next_level

        # 성능 제한: 주소 수 제한
        if len(current_level) > 50:
            break

    return all_transactions
```

---

### 3. 응답 데이터 구조

각 거래 객체에 **필수 필드 추가**:

```json
{
  "hop_level": 2,  // 🆕 몇 번째 홉인지
  "from": "0xMixer1",  // 명확히 구분
  "to": "0xMixer2",    // 명확히 구분
  "tx_hash": "0x...",
  "timestamp": "2025-11-17T12:34:56Z",
  "amount_usd": 4950.0,
  "chain_id": 1,
  "label": "mixer",
  "is_sanctioned": false,
  "is_mixer": true,
  ...
}
```

**중요**: 기존 `counterparty_address`, `target_address` 대신 `from`, `to` 사용

---

### 4. 성능 최적화

#### Rate Limiting

- Etherscan: 5 calls/sec (free tier)
- 해결: API 키 로테이션 또는 유료 플랜

#### 캐싱

```python
# Redis 또는 메모리 캐시
cache_key = f"{address}:{chain_id}:{timestamp_day}"
if cached := redis.get(cache_key):
    return cached

# API 호출 후 캐싱
txs = fetch_transactions(address, chain_id)
redis.setex(cache_key, 3600, txs)  # 1시간 캐싱
```

#### 병렬 처리

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(fetch_transactions, addr, chain_id)
        for addr in current_level
    ]
    results = [f.result() for f in futures]
```

#### 제한사항

- 최대 홉: 3
- 최대 주소 수: 50 (홉당)
- 최대 거래 수: 500 (전체)
- 타임아웃: 30초

---

## 📈 예상 영향

### 리스크 탐지 개선

| 패턴           | 기존 (1-hop) | Multi-hop (3-hop)        |
| -------------- | ------------ | ------------------------ |
| Mixer 경로     | ❌ 탐지 못함 | ✅ B-201 발동 (점수 +40) |
| 순환 거래      | ❌ 탐지 못함 | ✅ B-202 발동 (점수 +40) |
| 자금 분산/집중 | ⚠️ 부분 탐지 | ✅ 전체 경로 탐지        |

### 성능 영향

| 항목      | 기존  | Multi-hop (캐싱 없음) | Multi-hop (캐싱 있음) |
| --------- | ----- | --------------------- | --------------------- |
| 응답 시간 | 1-2초 | 10-30초               | 3-8초                 |
| API 호출  | 0회   | 5-20회                | 1-5회                 |
| 응답 크기 | ~10KB | ~100-500KB            | ~100-500KB            |

---

## 🧪 테스트 케이스

### Case 1: Layering Chain (B-201)

**입력**:

```json
{
  "address": "0xSuspicious",
  "chain_id": 1,
  "max_hops": 3,
  "analysis_type": "advanced"
}
```

**기대 결과**:

```json
{
  "risk_score": 75, // 기존: 25 → multi-hop: 75
  "fired_rules": [
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "B-201", "score": 40 }, // 🆕 새로 탐지됨!
    { "rule_id": "C-003", "score": 25 }
  ]
}
```

### Case 2: Cycle (B-202)

**패턴**: `Target → A → B → Target`

**기대 결과**:

- B-202 발동 (점수: 40)
- Risk level: "medium" → "high"

---

## 🚀 구현 우선순위

### Phase 1: 기본 구현 (1주)

- [ ] API 파라미터 추가 (`max_hops`)
- [ ] 재귀적 거래 수집 로직
- [ ] 응답 데이터에 `hop_level` 추가
- [ ] 기본 제한사항 (최대 홉, 최대 주소 수)

### Phase 2: 최적화 (1주)

- [ ] 캐싱 구현 (Redis)
- [ ] 병렬 처리
- [ ] Rate limiting 처리
- [ ] 부분 실패 처리

### Phase 3: 모니터링 (ongoing)

- [ ] 성능 모니터링 (응답 시간, API 호출 수)
- [ ] 에러 추적
- [ ] 캐시 적중률 모니터링

---

## 📞 연락처

**문의사항**:

- Risk Scoring Team
- 상세 문서: [MULTI_HOP_REQUIREMENT.md](./MULTI_HOP_REQUIREMENT.md)

**긴급 질문**:

- Q: 왜 3-hop까지만? → A: 성능과 정확도 균형 (대부분의 패턴은 3홉 이내)
- Q: 기존 API 호환성? → A: 완전 호환 (`analysis_type="basic"` → 기존 동작)
- Q: 성능 우려? → A: 캐싱으로 3-8초까지 단축 가능

---

**작성일**: 2025-11-21  
**우선순위**: High  
**예상 구현 기간**: 2주 (Phase 1 + Phase 2)
