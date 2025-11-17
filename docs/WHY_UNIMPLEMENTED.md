# 미구현 룰이 미구현인 이유

## 📊 미구현 룰 현황

**총 6개 미구현 룰**:

- B-201, B-202: `topology` 필요
- B-401, B-402: `state` 필요
- B-501: `buckets` (동적 점수) 필요
- B-502: 복합 집계 필요

---

## 🔍 각 룰이 미구현인 이유

### 1. B-201: Layering Chain (same token) - Topology 필요

**왜 미구현인가?**

```yaml
topology:
  same_token: true
  hop_length_gte: 3
  hop_amount_delta_pct_lte: 5
  min_usd_value: 100
```

**필요한 기능**:

1. **그래프 구조 분석**: 여러 거래를 그래프로 연결
2. **경로 탐색**: A → B → C → D 같은 3홉 이상 경로 찾기
3. **토큰 필터링**: 같은 토큰으로만 거래한 경로만 고려
4. **금액 차이 계산**: 각 홉의 금액 변화율 <= 5% 체크

**현재 문제**:

- 단일 트랜잭션만 평가하는 구조
- 여러 거래 간의 관계를 분석할 수 없음
- 그래프 탐색 알고리즘 필요

**구현 방법**:

- `MPOCryptoMLPatternDetector.detect_stack_pattern()` 활용
- 토큰 필터링 및 금액 차이 계산 추가

---

### 2. B-202: Cycle (length 2-3, same token) - Topology 필요

**왜 미구현인가?**

```yaml
topology:
  same_token: true
  cycle_length_in: [2, 3]
  cycle_total_usd_gte: 100
```

**필요한 기능**:

1. **순환 구조 탐지**: A → B → A 또는 A → B → C → A
2. **토큰 필터링**: 같은 토큰으로만 거래한 순환만 고려
3. **순환 총액 계산**: 순환 경로의 총 거래액 >= 100 USD

**현재 문제**:

- 순환 구조를 찾으려면 그래프 전체를 봐야 함
- DFS/BFS 같은 그래프 탐색 알고리즘 필요
- NetworkX의 순환 탐지 기능 활용 필요

**구현 방법**:

- `MPOCryptoMLPatternDetector`에 `detect_cycle_pattern()` 추가
- NetworkX의 순환 탐지 알고리즘 활용

---

### 3. B-401: First 7 Days Burst - State 필요

**왜 미구현인가?**

```yaml
state:
  required: ["first_seen_ts", "first7d_usd", "first7d_tx_count"]
conditions:
  all:
    - lte: { field: "age_days", value: 7 }
    - gte: { field: "first7d_usd", value: 10000 }
    - gte: { field: "first7d_tx_count", value: 3 }
```

**필요한 기능**:

1. **주소 메타데이터 관리**: 주소별 상태 정보 저장
   - `first_seen_ts`: 주소가 처음 발견된 시간
   - `first7d_usd`: 첫 7일간 총 거래액
   - `first7d_tx_count`: 첫 7일간 거래 수
2. **시간 기반 계산**: `age_days` 계산 (현재 시간 - first_seen_ts)
3. **상태 업데이트**: 새로운 거래마다 상태 업데이트

**현재 문제**:

- 트랜잭션만 평가하는 구조
- 주소의 생성일, 거래 히스토리 등 메타데이터 저장소 없음
- 상태 관리 시스템 필요 (DB 또는 캐시)

**구현 방법**:

1. `core/data/address_metadata.py` 모듈 생성
2. 주소별 메타데이터 저장소 구축
3. 상태 업데이트 로직 구현

---

### 4. B-402: Reactivation - State 필요

**왜 미구현인가?**

```yaml
state:
  required: ["first_seen_ts", "last_seen_ts"]
conditions:
  all:
    - gte: { field: "age_days", value: 365 }
    - gte: { field: "inactive_days", value: 180 }
    - gte: { field: "usd_value", value: 1000 }
```

**필요한 기능**:

1. **주소 메타데이터 관리**:
   - `first_seen_ts`: 주소 생성일
   - `last_seen_ts`: 마지막 거래일
2. **시간 기반 계산**:
   - `age_days`: 주소 나이 (현재 - first_seen_ts)
   - `inactive_days`: 비활성 기간 (현재 - last_seen_ts)
3. **상태 업데이트**: 거래마다 last_seen_ts 업데이트

**현재 문제**:

- 주소의 생성일, 마지막 거래일 추적 불가
- 비활성 기간 계산 불가
- 상태 관리 시스템 필요

**구현 방법**:

- B-401과 동일 (주소 메타데이터 저장소 구축)

---

### 5. B-501: High-Value Buckets - Buckets (동적 점수) 필요

**왜 미구현인가?**

```yaml
buckets:
  field: "usd_value"
  ranges:
    - { min: 10000, max: 50000, score: 5 }
    - { min: 50000, max: 250000, score: 10 }
    - { min: 250000, max: 1000000, score: 15 }
    - { min: 1000000, score: 20 }
score: dynamic
```

**필요한 기능**:

1. **동적 점수 할당**: 거래 금액에 따라 점수 범위 결정
   - 10,000 ~ 50,000 USD: 5점
   - 50,000 ~ 250,000 USD: 10점
   - 250,000 ~ 1,000,000 USD: 15점
   - 1,000,000 USD 이상: 20점
2. **버킷 분류**: 거래 금액을 적절한 버킷에 매핑

**현재 문제**:

- `score: dynamic` 처리 로직 없음
- 버킷 기반 동적 점수 할당 기능 없음
- 현재는 고정 점수만 지원

**구현 방법**:

1. `core/aggregation/bucket.py`에 동적 점수 로직 추가
2. 또는 `core/rules/evaluator.py`에서 `score: dynamic` 처리

---

### 6. B-502: Structuring — Rounded Value Repetition - 복합 집계 필요

**왜 미구현인가?**

```yaml
window:
  duration_sec: 86400
  group_by: ["address", "direction:outgoing"]
aggregations:
  - any_gte: { field: "usd_value", value: 10000000 }
  - group_by_value: "rounded_value"
  - per_group:
      - count_gte: { value: 5 }
      - sum_gte: { field: "usd_value", value: 10000 }
```

**필요한 기능**:

1. **값 그룹화**: `group_by_value: "rounded_value"` (반올림 값으로 그룹화)
2. **그룹별 집계**: `per_group` (각 그룹에서 count, sum 계산)
3. **방향 필터링**: `direction:outgoing` (출금만 고려)
4. **복합 조건**:
   - 전체에서 하나라도 >= 10,000,000 USD
   - 각 그룹에서 count >= 5, sum >= 10,000 USD

**현재 문제**:

- `group_by_value` 기능 없음 (값 기반 그룹화)
- `per_group` 집계 기능 없음 (그룹별 집계)
- `direction:outgoing` 필터링 기능 없음
- 복합 집계 로직 필요

**구현 방법**:

1. `core/aggregation/window.py`에 그룹화 로직 추가
2. 반올림 값 계산 로직
3. 그룹별 집계 로직

---

## 📋 요약

| 룰 ID     | 미구현 이유           | 필요한 기능                                   | 난이도 |
| --------- | --------------------- | --------------------------------------------- | ------ |
| **B-201** | `topology`            | 그래프 경로 탐색, 토큰 필터링, 금액 차이 계산 | ⭐⭐⭐ |
| **B-202** | `topology`            | 순환 구조 탐지, 토큰 필터링                   | ⭐⭐⭐ |
| **B-401** | `state`               | 주소 메타데이터 저장소, 시간 기반 계산        | ⭐⭐⭐ |
| **B-402** | `state`               | 주소 메타데이터 저장소, 비활성 기간 계산      | ⭐⭐⭐ |
| **B-501** | `buckets` (동적 점수) | 동적 점수 할당 로직                           | ⭐⭐   |
| **B-502** | 복합 집계             | 값 그룹화, 그룹별 집계, 방향 필터링           | ⭐⭐   |

---

## 🛠️ 구현 우선순위

### 빠르게 구현 가능 (반나절)

1. **B-501**: 동적 점수 로직만 추가
2. **B-502**: 그룹화 로직 추가

### 중간 난이도 (반나절)

3. **B-201**: MPOCryptoML Stack 패턴 활용
4. **B-202**: 순환 탐지 알고리즘 추가

### 높은 난이도 (1-2일)

5. **B-401, B-402**: 주소 메타데이터 저장소 구축

---

## 💡 핵심 문제

### 1. Topology 룰 (B-201, B-202)

**문제**: 단일 트랜잭션만 평가 → 여러 거래 간 관계 분석 불가

**해결**: 그래프 구조 분석 시스템 구축

### 2. State 룰 (B-401, B-402)

**문제**: 트랜잭션만 평가 → 주소 메타데이터 없음

**해결**: 주소 메타데이터 저장소 구축

### 3. 동적 점수/복합 집계 (B-501, B-502)

**문제**: 고정 점수만 지원 → 동적 점수/복합 집계 불가

**해결**: 집계 로직 확장
