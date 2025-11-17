# TRACE-X 룰 구현 현황

## 📊 전체 룰 현황

**총 룰 수**: 19개

- ✅ **구현 완료**: 8개
- 🚧 **부분 구현**: 3개
- ❌ **미구현**: 8개

---

## ✅ 구현 완료 룰 (8개)

### Compliance (C) - 3개

#### C-001: Sanction Direct Touch ✅

- **구현 방식**: 단일 트랜잭션 기반
- **로직**: `from` 또는 `to` 주소가 SDN_LIST에 포함되는지 확인
- **조건**: `usd_value >= 1 USD`
- **예외**: CEX_INTERNAL 거래 제외
- **점수**: 30점
- **파일**: `core/rules/evaluator.py` - `_match_rule()`, `_check_conditions()`

#### C-003: High-Value Single Transfer ✅

- **구현 방식**: 단일 트랜잭션 기반
- **로직**: 거래 금액이 7,000 USD 이상인지 확인
- **예외**: CEX_INTERNAL 거래 제외
- **점수**: 20점
- **파일**: `core/rules/evaluator.py` - `_check_conditions()`

#### C-004: High-Value Repeated Transfer (24h) ✅

- **구현 방식**: 윈도우 기반 집계
- **로직**: 24시간 내 동일 주소에서 3회 이상 고액 거래 (각 3,000 USD 이상, 총 10,000 USD 이상)
- **점수**: 20점
- **파일**:
  - `core/aggregation/window.py` - `WindowEvaluator`
  - `core/rules/evaluator.py` - 윈도우 룰 평가

### Exposure (E) - 1개

#### E-101: Mixer Direct Exposure ✅

- **구현 방식**: 단일 트랜잭션 기반
- **로직**: `from` 주소가 MIXER_LIST에 포함되는지 확인
- **조건**: `usd_value >= 20 USD`
- **예외**: REWARD_PAYOUT 제외
- **점수**: 25점
- **파일**: `core/rules/evaluator.py` - `_match_rule()`, `_check_conditions()`

### Behavior (B) - 4개

#### B-101: Burst (10m) ✅

- **구현 방식**: 윈도우 기반 집계
- **로직**: 10분 내 동일 주소에서 3회 이상 거래
- **쿨다운**: 30분
- **점수**: 15점
- **파일**:
  - `core/aggregation/window.py` - `WindowEvaluator`
  - `core/rules/evaluator.py` - 윈도우 룰 평가

#### B-102: Rapid Sequence (1m) ✅

- **구현 방식**: 윈도우 기반 집계
- **로직**: 1분 내 동일 주소에서 5회 이상 거래
- **쿨다운**: 15분
- **점수**: 20점
- **파일**:
  - `core/aggregation/window.py` - `WindowEvaluator`
  - `core/rules/evaluator.py` - 윈도우 룰 평가

#### B-203: Fan-out (10m bucket) ✅

- **구현 방식**: 버킷 기반 집계
- **로직**: 10분 버킷 내 동일 주소(`from`)에서 5개 이상의 고유 주소(`to`)로 총 1,000 USD 이상 송금, 각 거래 100 USD 이상
- **점수**: 20점
- **파일**:
  - `core/aggregation/bucket.py` - `BucketEvaluator`
  - `core/rules/evaluator.py` - 버킷 룰 평가
  - `core/aggregation/mpocryptml_patterns.py` - MPOCryptoML 패턴 탐지

#### B-204: Fan-in (10m bucket) ✅

- **구현 방식**: 버킷 기반 집계
- **로직**: 10분 버킷 내 여러 주소(`from`)에서 동일 주소(`to`)로 총 1,000 USD 이상 입금, 각 거래 100 USD 이상
- **점수**: 20점
- **파일**:
  - `core/aggregation/bucket.py` - `BucketEvaluator`
  - `core/rules/evaluator.py` - 버킷 룰 평가
  - `core/aggregation/mpocryptml_patterns.py` - MPOCryptoML 패턴 탐지

---

## 🚧 부분 구현 룰 (3개)

### Compliance (C) - 1개

#### C-002: High-Risk Jurisdiction VASP 🚧

- **현재 상태**: 룰 구조는 있으나 백엔드 데이터 필요
- **필요한 데이터**:
  - `counterparty.country` (IR, RU, KP)
  - `counterparty.type` (VASP)
  - `counterparty.safe_vasp` (예외 처리)
- **구현 방법**:
  - 백엔드에서 `counterparty` 정보 제공 시 자동 작동
  - 현재는 `tag` 필드가 없으면 건너뜀
- **점수**: 20점
- **파일**: `core/rules/evaluator.py` - `_check_conditions()` (tag 기반)

### Exposure (E) - 2개

#### E-102: Indirect Sanctions Exposure (≤2 hops) 🚧

- **현재 상태**: 룰 구조는 있으나 SDN_HOP1, SDN_HOP2 리스트 필요
- **필요한 데이터**:
  - SDN_HOP1 리스트 (1홉 제재 주소)
  - SDN_HOP2 리스트 (2홉 제재 주소)
- **구현 방법**:
  - 홉 분석 로직 구현 필요
  - 또는 백엔드에서 홉 정보 제공
- **점수**: 30점
- **파일**: `core/data/lists.py` - `ListLoader` (SDN_HOP1, SDN_HOP2 추가 필요)

#### E-103: Counterparty Quality Risk 🚧

- **현재 상태**: 룰 구조는 있으나 백엔드 데이터 필요
- **필요한 데이터**: `counterparty.risk_score` (0.7 이상)
- **구현 방법**:
  - 백엔드에서 `counterparty.risk_score` 제공 시 자동 작동
  - 현재는 `tag` 필드가 없으면 건너뜀
- **점수**: 10~20점 (기본 15점)
- **파일**: `core/rules/evaluator.py` - `_check_conditions()` (tag 기반)

---

## ❌ 미구현 룰 (8개)

### Behavior (B) - 8개

#### B-103: Inter-arrival Std High ❌

- **미구현 이유**: `prerequisites` 및 통계 계산 필요
- **필요한 기능**:
  - `prerequisites.min_edges: 10` 체크
  - `interarrival_std` 계산 (거래 간격 표준편차)
- **구현 방법**:
  1. `core/rules/evaluator.py`에 `prerequisites` 체크 로직 추가
  2. `core/aggregation/stats.py` 모듈 생성
  3. 거래 간격 계산 및 표준편차 계산
- **예상 구현 시간**: 1-2시간
- **난이도**: ⭐ (낮음)

#### B-201: Layering Chain (same token) ❌

- **미구현 이유**: `topology` 분석 필요
- **필요한 기능**:
  - 그래프 구조 분석 (NetworkX)
  - 3홉 이상 경로 탐색
  - 동일 토큰 체크
  - 각 홉 금액 차이 <= 5% 체크
- **구현 방법**:
  1. `core/aggregation/topology.py` 모듈 생성
  2. `MPOCryptoMLPatternDetector.detect_stack_pattern()` 활용
  3. 토큰 필터링 및 금액 차이 계산 추가
- **예상 구현 시간**: 반나절
- **난이도**: ⭐⭐⭐ (중간)
- **MPOCryptoML 활용**: ✅ `detect_stack_pattern()` 사용 가능

#### B-202: Cycle (length 2-3, same token) ❌

- **미구현 이유**: `topology` 분석 필요
- **필요한 기능**:
  - 순환 구조 탐지 (A → B → A 또는 A → B → C → A)
  - 동일 토큰 체크
  - 순환 총액 >= 100 USD
- **구현 방법**:
  1. `core/aggregation/topology.py` 모듈 생성
  2. `MPOCryptoMLPatternDetector`에 `detect_cycle_pattern()` 추가
  3. NetworkX의 순환 탐지 알고리즘 활용
- **예상 구현 시간**: 반나절
- **난이도**: ⭐⭐⭐ (중간)

#### B-401: First 7 Days Burst ❌

- **미구현 이유**: `state` 관리 필요
- **필요한 기능**:
  - 주소 생성일 추적 (`first_seen_ts`)
  - 첫 7일간 거래 집계 (`first7d_usd`, `first7d_tx_count`)
  - `age_days` 계산
- **구현 방법**:
  1. `core/data/address_metadata.py` 모듈 생성
  2. 주소별 메타데이터 저장소 구축 (DB 또는 캐시)
  3. 상태 업데이트 로직 구현
- **예상 구현 시간**: 1-2일
- **난이도**: ⭐⭐⭐ (높음)

#### B-402: Reactivation ❌

- **미구현 이유**: `state` 관리 필요
- **필요한 기능**:
  - 주소 생성일 및 마지막 거래일 추적
  - `age_days >= 365` 체크
  - `inactive_days >= 180` 체크
- **구현 방법**:
  1. `core/data/address_metadata.py` 모듈 생성
  2. 주소별 메타데이터 저장소 구축
  3. 비활성 기간 계산 로직
- **예상 구현 시간**: 1-2일
- **난이도**: ⭐⭐⭐ (높음)

#### B-403A: Lifecycle A — Young but Busy ❌

- **미구현 이유**: `state` 관리 필요
- **필요한 기능**:
  - `age_days <= 30` 체크
  - `tx_count_30d >= 100` (30일간 거래 수)
  - `median_usd_30d >= 100` (30일간 중앙값 거래액)
- **구현 방법**:
  1. `core/data/address_metadata.py` 모듈 생성
  2. 시간 기반 집계 로직
  3. 통계 계산 (중앙값)
- **예상 구현 시간**: 1-2일
- **난이도**: ⭐⭐⭐ (높음)

#### B-403B: Lifecycle B — Old and Rare High Value ❌

- **미구현 이유**: `state` 관리 필요
- **필요한 기능**:
  - `age_days >= 365` 체크
  - `tx_count_total <= 10` (총 거래 수)
  - `total_usd_total >= 50000` (총 거래액)
  - `median_usd_total >= 5000` (중앙값 거래액)
- **구현 방법**:
  1. `core/data/address_metadata.py` 모듈 생성
  2. 주소별 통계 집계
  3. 통계 계산 (중앙값)
- **예상 구현 시간**: 1-2일
- **난이도**: ⭐⭐⭐ (높음)

#### B-501: High-Value Buckets ❌

- **미구현 이유**: `buckets` 기반 동적 점수 할당 필요
- **필요한 기능**:
  - 거래 금액에 따른 버킷 분류
  - 동적 점수 할당 (5, 10, 15, 20점)
- **구현 방법**:
  1. `core/aggregation/bucket.py`에 동적 점수 로직 추가
  2. 또는 `core/rules/evaluator.py`에서 `score: dynamic` 처리
- **예상 구현 시간**: 반나절
- **난이도**: ⭐⭐ (중간)

#### B-502: Structuring — Rounded Value Repetition (24h outgoing) ❌

- **미구현 이유**: 복합 집계 및 그룹화 필요
- **필요한 기능**:
  - `group_by_value: "rounded_value"` (반올림 값 그룹화)
  - `per_group` 집계 (각 그룹별 count, sum)
  - `direction:outgoing` 필터링
- **구현 방법**:
  1. `core/aggregation/window.py`에 그룹화 로직 추가
  2. 반올림 값 계산 로직
  3. 그룹별 집계 로직
- **예상 구현 시간**: 반나절
- **난이도**: ⭐⭐ (중간)

---

## 🛠️ 구현 방법 가이드

### 1. 단일 트랜잭션 룰 구현

**구조**:

```yaml
- id: "C-001"
  match:
    any:
      - in_list: { field: "from", list: "SDN_LIST" }
  conditions:
    all:
      - gte: { field: "usd_value", value: 1 }
  exceptions:
    any:
      - tag: { field: "from", key: "CEX_INTERNAL", equals: true }
  score: 30
```

**구현 위치**: `core/rules/evaluator.py`

- `_match_rule()`: 룰 매칭 확인
- `_check_conditions()`: 조건 확인
- `_check_exceptions()`: 예외 확인

### 2. 윈도우 기반 룰 구현

**구조**:

```yaml
- id: "C-004"
  window:
    duration_sec: 86400
    group_by: ["address"]
  aggregations:
    - sum_gte: { field: "usd_value", value: 10000 }
    - count_gte: { value: 3 }
  score: 20
```

**구현 위치**:

- `core/aggregation/window.py` - `WindowEvaluator`
- `core/rules/evaluator.py` - 윈도우 룰 평가

**집계 함수**:

- `sum_gte`: 합계 >= 값
- `count_gte`: 개수 >= 값
- `every_gte`: 모든 값 >= 값
- `distinct_gte`: 고유값 개수 >= 값
- `any_gte`: 하나라도 >= 값
- `avg_gte`: 평균 >= 값

### 3. 버킷 기반 룰 구현

**구조**:

```yaml
- id: "B-203"
  bucket:
    size_sec: 600
    group: ["chain_id", "token", "from", "bucket_10m"]
  aggregations:
    - distinct_gte: { field: "to", value: 5 }
    - sum_gte: { field: "usd_value", value: 1000 }
  score: 20
```

**구현 위치**:

- `core/aggregation/bucket.py` - `BucketEvaluator`
- `core/rules/evaluator.py` - 버킷 룰 평가

### 4. 토폴로지 기반 룰 구현 (미구현)

**구조**:

```yaml
- id: "B-201"
  topology:
    same_token: true
    hop_length_gte: 3
    hop_amount_delta_pct_lte: 5
    min_usd_value: 100
  score: 25
```

**구현 방법**:

1. `core/aggregation/topology.py` 모듈 생성
2. `MPOCryptoMLPatternDetector` 활용
3. NetworkX 그래프 구축 및 경로 탐색

### 5. 상태 기반 룰 구현 (미구현)

**구조**:

```yaml
- id: "B-401"
  state:
    required: ["first_seen_ts", "first7d_usd", "first7d_tx_count"]
  conditions:
    all:
      - lte: { field: "age_days", value: 7 }
      - gte: { field: "first7d_usd", value: 10000 }
  score: 20
```

**구현 방법**:

1. `core/data/address_metadata.py` 모듈 생성
2. 주소별 메타데이터 저장소 구축
3. 상태 업데이트 로직 구현

### 6. Prerequisites 기반 룰 구현 (미구현)

**구조**:

```yaml
- id: "B-103"
  prerequisites:
    - min_edges: 10
  conditions:
    all:
      - gte: { field: "interarrival_std", value: 2.0 }
  score: 10
```

**구현 방법**:

1. `core/rules/evaluator.py`에 `_check_prerequisites()` 추가
2. 통계 계산 모듈 생성

---

## 📋 구현 우선순위

### 높은 우선순위 (빠르게 구현 가능)

1. **B-103: Inter-arrival Std High** ⭐

   - 통계 계산만 추가
   - 예상 시간: 1-2시간

2. **B-501: High-Value Buckets** ⭐⭐

   - 버킷 기반 동적 점수
   - 예상 시간: 반나절

3. **B-502: Structuring Pattern** ⭐⭐
   - 그룹화 로직 추가
   - 예상 시간: 반나절

### 중간 우선순위 (구조 개선 필요)

4. **B-201: Layering Chain** ⭐⭐⭐

   - MPOCryptoML Stack 패턴 활용
   - 예상 시간: 반나절

5. **B-202: Cycle** ⭐⭐⭐
   - 순환 탐지 알고리즘
   - 예상 시간: 반나절

### 낮은 우선순위 (복잡한 구조 필요)

6. **B-401, B-402, B-403A, B-403B: Lifecycle 룰** ⭐⭐⭐
   - 상태 관리 시스템 구축
   - 예상 시간: 1-2일

---

## 🔗 관련 파일

- **룰 평가**: `core/rules/evaluator.py`
- **윈도우 집계**: `core/aggregation/window.py`
- **버킷 집계**: `core/aggregation/bucket.py`
- **패턴 탐지**: `core/aggregation/mpocryptml_patterns.py`
- **리스트 로더**: `core/data/lists.py`
- **룰북**: `rules/tracex_rules.yaml`
