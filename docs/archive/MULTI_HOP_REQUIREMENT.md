# Multi-Hop 거래 데이터 수집 요구사항

## 📌 요약

현재 리스크 스코어링 시스템은 **1-hop 거래만** 분석 가능합니다. 그래프 기반 패턴 탐지(Layering Chain, Cycle 등)를 위해 **multi-hop 거래 데이터**가 필요합니다.

---

## 🚨 현재 문제점

### 1. 현재 백엔드가 제공하는 데이터

```json
{
  "target_address": "0xTarget",
  "transactions": [
    {
      "target_address": "0xTarget",
      "counterparty_address": "0xMixer1",
      "amount_usd": 5000.0,
      ...
    },
    {
      "target_address": "0xTarget",
      "counterparty_address": "0xMixer2",
      "amount_usd": 3000.0,
      ...
    }
  ]
}
```

**한계**: Target과 직접 거래한 주소들만 알 수 있음 (1-hop)

- ✅ `Target ↔ Mixer1` 관계 분석 가능
- ❌ `Mixer1 → Mixer2 → Destination` 경로 분석 **불가능**

### 2. 작동하지 않는 룰들

다음 룰들은 현재 **사실상 작동하지 않음**:

| Rule ID | Rule Name                   | 필요 데이터             | 현재 상태    |
| ------- | --------------------------- | ----------------------- | ------------ |
| B-201   | Layering Chain (3-hop 이상) | Target → A → B → C      | ❌ 불가능    |
| B-202   | Cycle (2-3홉 순환)          | Target → A → B → Target | ❌ 불가능    |
| B-203   | Fan-out (자금 분산)         | Target → [A, B, C, ...] | ✅ 부분 가능 |
| B-204   | Fan-in (자금 집중)          | [A, B, C, ...] → Target | ✅ 부분 가능 |

**B-203, B-204도 제한적**: Target의 counterparty들이 서로 어떻게 연결되어 있는지 모름

### 3. 실제 사례: 왜 Multi-hop이 필요한가?

**시나리오**: Mixer를 통한 자금 세탁 탐지

```
Target → Mixer1 → Mixer2 → Clean Address → CEX
  (1)      (2)       (3)         (4)        (5)
```

**현재 시스템**:

- ✅ (1) `Target → Mixer1` 탐지 가능 → E-101 룰 발동 (점수: 25)
- ❌ (2)-(5) 이후 경로는 **보이지 않음**

**Multi-hop 시스템**:

- ✅ 전체 경로 탐지 가능
- ✅ B-201 (Layering Chain) 룰 발동 → 추가 점수 (40)
- ✅ 더 정확한 리스크 스코어 산출

---

## ✅ 필요한 변경사항

### 옵션 A: 파라미터 추가 (기존 API 유지)

기존 `POST /api/analyze/address` API에 **선택적 파라미터** 추가:

```json
{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [...],  // 기존 1-hop 데이터
  "max_hops": 3,          // 🆕 추가: 몇 홉까지 수집할지 (기본값: 1)
  "analysis_type": "advanced"  // "advanced"일 때만 multi-hop 수집
}
```

**백엔드 로직**:

1. `analysis_type == "basic"` → 기존대로 1-hop만 반환
2. `analysis_type == "advanced"` + `max_hops > 1` → multi-hop 수집

**장점**:

- 기존 API 호환성 유지
- 필요할 때만 multi-hop 수집 (성능 최적화)

**단점**:

- 백엔드에서 재귀적으로 데이터 수집 필요 (느림)

---

### 옵션 B: 새로운 데이터 구조 (권장)

백엔드가 애초에 **모든 관련 거래를 수집**해서 보내주기:

```json
{
  "target_address": "0xTarget",
  "max_hops": 3,  // 실제 수집한 홉 수
  "transactions": [
    // 1-hop: Target의 직접 거래
    {
      "hop_level": 1,  // 🆕 추가
      "from": "0xTarget",
      "to": "0xMixer1",
      "amount_usd": 5000.0,
      "timestamp": "2025-11-17T12:34:56Z",
      ...
    },

    // 2-hop: Counterparty들의 거래
    {
      "hop_level": 2,  // 🆕 추가
      "from": "0xMixer1",
      "to": "0xMixer2",
      "amount_usd": 4950.0,
      "timestamp": "2025-11-17T12:35:10Z",
      ...
    },

    // 3-hop
    {
      "hop_level": 3,  // 🆕 추가
      "from": "0xMixer2",
      "to": "0xCleanAddress",
      "amount_usd": 4900.0,
      "timestamp": "2025-11-17T12:35:45Z",
      ...
    }
  ]
}
```

**백엔드 수집 로직** (의사코드):

```python
def collect_multi_hop_transactions(target_address, chain_id, max_hops=3):
    all_transactions = []
    visited_addresses = set()
    current_hop_addresses = {target_address}

    for hop in range(1, max_hops + 1):
        next_hop_addresses = set()

        for address in current_hop_addresses:
            if address in visited_addresses:
                continue

            # Etherscan/Alchemy API로 거래 수집
            txs = fetch_transactions(address, chain_id, limit=100)

            for tx in txs:
                tx["hop_level"] = hop
                all_transactions.append(tx)

                # 다음 홉 주소 수집
                if tx["from"] == address:
                    next_hop_addresses.add(tx["to"])
                else:
                    next_hop_addresses.add(tx["from"])

            visited_addresses.add(address)

        current_hop_addresses = next_hop_addresses

        # 너무 많은 주소는 제한 (성능)
        if len(current_hop_addresses) > 50:
            break

    return all_transactions
```

**장점**:

- 리스크 스코어링 정확도 크게 향상
- 그래프 패턴 탐지 가능 (B-201, B-202)
- 더 정교한 분석 가능

**단점**:

- API 응답 크기 증가
- 처리 시간 증가 (1-2초 → 5-30초)

---

## 🔧 구현 가이드

### 백엔드 구현 체크리스트

#### 1. API 파라미터 수정

- [ ] `max_hops` 파라미터 추가 (기본값: 1, 최대값: 3)
- [ ] `analysis_type` 파라미터 활용
  - `"basic"` → `max_hops=1` (기존 동작)
  - `"advanced"` → `max_hops=3` (multi-hop 수집)

#### 2. 데이터 수집 로직

- [ ] Etherscan/Alchemy API 호출 함수 구현
- [ ] 재귀적 거래 수집 (BFS/DFS)
- [ ] 방문한 주소 추적 (중복 방지)
- [ ] 최대 주소 수 제한 (성능 최적화)
- [ ] Rate limit 처리 (Etherscan: 5 calls/sec)

#### 3. 응답 데이터 구조

- [ ] 각 거래에 `hop_level` 필드 추가
- [ ] `from`, `to` 필드 명확히 구분 (기존 `counterparty_address` 대신)
- [ ] 타임스탬프 순 정렬

#### 4. 성능 최적화

- [ ] 캐싱 (동일 주소 재방문 시)
- [ ] 병렬 처리 (여러 주소 동시 수집)
- [ ] 타임아웃 설정 (30초)
- [ ] 부분 실패 처리 (일부 주소 실패해도 계속 진행)

---

## 📊 예상 영향

### 리스크 스코어링 정확도 향상

| 시나리오          | 기존 (1-hop)        | Multi-hop (3-hop)        |
| ----------------- | ------------------- | ------------------------ |
| Mixer를 통한 세탁 | 점수: 25 (E-101만)  | 점수: 65 (E-101 + B-201) |
| 순환 거래         | 점수: 0 (탐지 못함) | 점수: 40 (B-202)         |
| 레이어링 체인     | 점수: 0 (탐지 못함) | 점수: 40 (B-201)         |

### 성능 영향

| 항목           | 기존  | Multi-hop               |
| -------------- | ----- | ----------------------- |
| 평균 응답 시간 | 1-2초 | 5-15초 (캐싱 시: 3-8초) |
| API 호출 수    | 1회   | 3-10회 (홉 수에 비례)   |
| 응답 크기      | ~10KB | ~50-200KB               |

---

## 🧪 테스트 시나리오

### 테스트 케이스 1: Layering Chain

**목표**: B-201 룰 발동 확인

```
Target → Mixer1 → Mixer2 → Clean
```

**기대 결과**:

- `hop_level=1`: `Target → Mixer1`
- `hop_level=2`: `Mixer1 → Mixer2`
- `hop_level=3`: `Mixer2 → Clean`
- **B-201 발동**: 3홉 체인, 동일 토큰, 금액 차이 5% 이내

### 테스트 케이스 2: Cycle

**목표**: B-202 룰 발동 확인

```
Target → Address1 → Address2 → Target
```

**기대 결과**:

- `hop_level=1`: `Target → Address1`
- `hop_level=2`: `Address1 → Address2`
- `hop_level=3`: `Address2 → Target`
- **B-202 발동**: 3홉 순환, 동일 토큰

### 테스트 케이스 3: Fan-out → Fan-in

**목표**: 복합 패턴 탐지

```
Target → [A, B, C] → Destination
```

**기대 결과**:

- `hop_level=1`: `Target → A`, `Target → B`, `Target → C`
- `hop_level=2`: `A → Destination`, `B → Destination`, `C → Destination`
- **B-203 발동**: Fan-out (Target)
- **B-204 발동**: Fan-in (Destination)

---

## 📝 API 스펙 변경안

### 요청 (Request)

**기존 (1-hop)**:

```json
{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [...],
  "analysis_type": "basic"
}
```

**새로운 (multi-hop)**:

```json
{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3, // 🆕 추가 (선택, 기본값: 1)
  "analysis_type": "advanced", // "advanced"일 때 multi-hop 활성화
  "time_window_hours": 24 // 🆕 추가 (선택): 최근 N시간 거래만 수집
}
```

**주의**:

- `transactions` 필드를 **백엔드가 수집**하도록 변경
- 프론트엔드는 `address`, `chain_id`, `max_hops`만 보내면 됨

### 응답 (Response)

**변경 없음**: 기존 응답 형식 유지

```json
{
  "target_address": "0xTarget",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "layering_chain"],
  "fired_rules": [
    {"rule_id": "E-101", "score": 25},
    {"rule_id": "B-201", "score": 40}  // 🆕 Multi-hop으로 탐지 가능
  ],
  ...
}
```

---

## 🔐 보안 및 제한사항

### 1. Rate Limiting

- Etherscan API: 5 calls/sec (free tier)
- 해결: API 키 여러 개 로테이션 또는 유료 플랜

### 2. 데이터 양 제한

- 최대 홉: 3홉
- 최대 주소 수: 50개 (홉당)
- 최대 거래 수: 500개 (전체)

### 3. 타임아웃

- 전체 분석: 30초
- 30초 초과 시: 부분 결과 반환 + 경고 메시지

### 4. 캐싱

- 동일 주소 재방문 시 캐시 사용 (유효기간: 1시간)
- Redis 또는 메모리 캐시

---

## 💬 백엔드 팀에게 전달할 내용 요약

### 핵심 요청사항

> **현재 리스크 스코어링 시스템은 1-hop 거래만 분석 가능합니다.**
>
> **그래프 기반 패턴 탐지**(Layering Chain, Cycle)를 위해 **multi-hop 거래 데이터 수집**이 필요합니다.

### 필요한 변경사항

1. **API 파라미터 추가**

   - `max_hops` (기본값: 1, 최대값: 3)
   - `analysis_type == "advanced"`일 때 활성화

2. **데이터 수집 로직**

   - Target의 counterparty 주소들의 거래도 수집
   - 각 거래에 `hop_level` 필드 추가
   - `from`, `to` 필드 명확히 구분

3. **성능 고려사항**
   - 응답 시간: 5-15초 (캐싱 시 3-8초)
   - Rate limiting 처리 (Etherscan API)
   - 최대 주소 수/거래 수 제한

### 기대 효과

- 리스크 스코어링 정확도 **30-50% 향상**
- 새로운 룰 발동 가능 (B-201, B-202)
- 복잡한 세탁 패턴 탐지 가능

---

## 📚 참고 자료

- [CORRECT_INPUT_FORMAT.md](./CORRECT_INPUT_FORMAT.md) - 현재 API 스펙
- [RISK_SCORING_IO.md](./RISK_SCORING_IO.md) - 리스크 스코어링 I/O
- [rules/tracex_rules.yaml](../rules/tracex_rules.yaml) - 전체 룰 정의
  - B-201: Layering Chain (line 290-320)
  - B-202: Cycle (line 321-350)

---

## ❓ FAQ

### Q1: 왜 3-hop까지만?

**A**: 성능과 정확도의 균형. 대부분의 세탁 패턴은 3홉 이내에서 발생합니다. 4홉 이상은 노이즈가 많고 처리 시간이 기하급수적으로 증가합니다.

### Q2: 1-hop만 쓰면 안 되나요?

**A**: 1-hop만으로는 **복잡한 세탁 패턴을 탐지할 수 없습니다**. 예를 들어:

- Tornado Cash → Intermediate → CEX (3홉)
- Circular trading (순환 거래, 2-3홉)

### Q3: 성능이 걱정됩니다

**A**: 캐싱과 병렬 처리로 최적화 가능합니다:

- 캐시 적중률 60-70% 예상 (동일 주소 재방문)
- 병렬 API 호출 (5-10개 동시)
- 부분 실패 시에도 1-hop 결과 반환

### Q4: 기존 API와 호환성은?

**A**: 완전히 호환됩니다:

- `analysis_type="basic"` → 기존 동작 (1-hop)
- `analysis_type="advanced"` → multi-hop 활성화
- 기본값은 `"basic"`

---

**작성일**: 2025-11-21  
**버전**: 1.0  
**담당자**: Risk Scoring Team
