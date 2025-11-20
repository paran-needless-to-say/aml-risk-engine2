# 리스크 스코어링 구현 현황 정리

## 📊 전체 룰 현황 (총 19개)

- ✅ **구현 완료**: 11개
- 🚧 **부분 구현**: 3개
- ❌ **미구현**: 5개

---

## ✅ 구현 완료 룰 (11개)

### Compliance (C) - 3개

#### C-001: Sanction Direct Touch ✅

- **구현 방식**: 단일 트랜잭션 기반
- **로직**: `from` 또는 `to` 주소가 SDN_LIST에 포함되는지 확인
- **조건**: `usd_value >= 1 USD`
- **예외**: CEX_INTERNAL 거래 제외
- **점수**: 30점
- **파일**: `core/rules/evaluator.py`

#### C-003: High-Value Single Transfer ✅

- **구현 방식**: 단일 트랜잭션 기반
- **로직**: 거래 금액이 7,000 USD 이상인지 확인
- **예외**: CEX_INTERNAL 거래 제외
- **점수**: 20점
- **파일**: `core/rules/evaluator.py`

#### C-004: High-Value Repeated Transfer (24h) ✅

- **구현 방식**: 윈도우 기반 집계
- **로직**: 24시간 내 동일 주소에서 3회 이상 고액 거래 (각 3,000 USD 이상, 총 10,000 USD 이상)
- **점수**: 20점
- **파일**: `core/aggregation/window.py`, `core/rules/evaluator.py`

### Exposure (E) - 1개

#### E-101: Mixer Direct Exposure ✅

- **구현 방식**: 단일 트랜잭션 기반
- **로직**: `from` 주소가 MIXER_LIST에 포함되는지 확인
- **조건**: `usd_value >= 20 USD`
- **예외**: REWARD_PAYOUT 제외
- **점수**: 25점
- **파일**: `core/rules/evaluator.py`

### Behavior (B) - 7개

#### B-101: Burst (10m) ✅

- **구현 방식**: 윈도우 기반 집계
- **로직**: 10분 내 동일 주소에서 3회 이상 거래
- **쿨다운**: 30분
- **점수**: 15점
- **파일**: `core/aggregation/window.py`, `core/rules/evaluator.py`

#### B-102: Rapid Sequence (1m) ✅

- **구현 방식**: 윈도우 기반 집계
- **로직**: 1분 내 동일 주소에서 5회 이상 거래
- **쿨다운**: 15분
- **점수**: 20점
- **파일**: `core/aggregation/window.py`, `core/rules/evaluator.py`

#### B-103: Inter-arrival Std High ✅

- **구현 방식**: 통계 계산 기반
- **로직**: 거래 간격 표준편차 계산 (prerequisites: 최소 10개 거래)
- **조건**: `interarrival_std >= 2.0`, `usd_value >= 50`
- **점수**: 10점
- **파일**: `core/aggregation/stats.py`, `core/rules/evaluator.py`

#### B-201: Layering Chain (same token) ✅ **그래프 룰**

- **구현 방식**: 토폴로지(그래프) 기반 분석
- **로직**: NetworkX로 그래프 구축 후 3홉 이상 레이어링 체인 탐지
- **조건**:
  - 동일 토큰
  - 3홉 이상
  - 각 홉 금액 차이 <= 5%
  - 최소 거래액 >= 100 USD
- **점수**: 25점
- **파일**: `core/aggregation/topology.py`, `core/rules/evaluator.py`
- **⚠️ 주의**: 기본 스코어링에서는 제외됨 (`include_topology=False`가 기본값)
- **사용 방법**: `analysis_type="advanced"` 또는 `include_topology=True`로 설정 필요

#### B-202: Cycle (length 2-3, same token) ✅ **그래프 룰**

- **구현 방식**: 토폴로지(그래프) 기반 분석
- **로직**: NetworkX로 그래프 구축 후 2-3홉 순환 구조 탐지
- **조건**:
  - 동일 토큰
  - 순환 길이: 2-3홉
  - 순환 총액 >= 100 USD
- **점수**: 30점
- **파일**: `core/aggregation/topology.py`, `core/rules/evaluator.py`
- **⚠️ 주의**: 기본 스코어링에서는 제외됨 (`include_topology=False`가 기본값)
- **사용 방법**: `analysis_type="advanced"` 또는 `include_topology=True`로 설정 필요

#### B-203: Fan-out (10m bucket) ✅

- **구현 방식**: 버킷 기반 집계
- **로직**: 10분 버킷 내 동일 주소(`from`)에서 5개 이상의 고유 주소(`to`)로 총 1,000 USD 이상 송금, 각 거래 100 USD 이상
- **점수**: 20점
- **파일**: `core/aggregation/bucket.py`, `core/rules/evaluator.py`

#### B-204: Fan-in (10m bucket) ✅

- **구현 방식**: 버킷 기반 집계
- **로직**: 10분 버킷 내 여러 주소(`from`)에서 동일 주소(`to`)로 총 1,000 USD 이상 입금, 각 거래 100 USD 이상
- **점수**: 20점
- **파일**: `core/aggregation/bucket.py`, `core/rules/evaluator.py`

---

## 🚧 부분 구현 룰 (3개)

### Compliance (C) - 1개

#### C-002: High-Risk Jurisdiction VASP 🚧

- **현재 상태**: 룰 구조는 있으나 백엔드 데이터 필요
- **필요한 데이터**:
  - `counterparty.country` (IR, RU, KP)
  - `counterparty.type` (VASP)
  - `counterparty.safe_vasp` (예외 처리)
- **구현 방법**: 백엔드에서 `counterparty` 정보 제공 시 자동 작동
- **점수**: 20점
- **파일**: `core/rules/evaluator.py` (tag 기반)

### Exposure (E) - 2개

#### E-102: Indirect Sanctions Exposure (≤2 hops) 🚧

- **현재 상태**: PPR 기반 구현됨 (부분 구현)
- **구현 방식**: PPR(PageRank) 알고리즘으로 간접 제재 노출 탐지
- **필요한 데이터**: 3홉까지 거래 히스토리
- **점수**: 30점
- **파일**: `core/aggregation/ppr_connector.py`, `core/rules/evaluator.py`
- **⚠️ 주의**: 기본 스코어링에서는 작동하지만, 충분한 거래 히스토리가 필요함

#### E-103: Counterparty Quality Risk 🚧

- **현재 상태**: 룰 구조는 있으나 백엔드 데이터 필요
- **필요한 데이터**: `counterparty.risk_score` (0.7 이상)
- **구현 방법**: 백엔드에서 `counterparty.risk_score` 제공 시 자동 작동
- **점수**: 10~20점 (기본 15점)
- **파일**: `core/rules/evaluator.py` (tag 기반)

---

## ❌ 미구현 룰 (5개)

### Behavior (B) - 5개

#### B-401: First 7 Days Burst ❌

- **미구현 이유**: 주소 상태(state) 관리 필요
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

- **미구현 이유**: 주소 상태(state) 관리 필요
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

- **미구현 이유**: 주소 상태(state) 관리 필요
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

- **미구현 이유**: 주소 상태(state) 관리 필요
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

- **미구현 이유**: 동적 점수 할당 필요
- **필요한 기능**:
  - 거래 금액에 따른 버킷 분류
  - 동적 점수 할당 (5, 10, 15, 20점)
- **구현 방법**:
  1. `core/rules/evaluator.py`에서 `score: dynamic` 처리
  2. 버킷별 점수 할당 로직 추가
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

## 🎯 그래프 관련 룰 정리

### ✅ 구현 완료 (그래프 룰)

#### B-201: Layering Chain ✅

- **상태**: 구현 완료
- **구현 위치**: `core/aggregation/topology.py`
- **기능**: NetworkX로 그래프 구축 후 3홉 이상 레이어링 체인 탐지
- **사용 조건**:
  - `include_topology=True` 또는 `analysis_type="advanced"` 필요
  - 3홉까지 거래 데이터 필요
- **기본 동작**: 기본 스코어링에서는 제외됨 (성능 최적화)

#### B-202: Cycle ✅

- **상태**: 구현 완료
- **구현 위치**: `core/aggregation/topology.py`
- **기능**: NetworkX로 그래프 구축 후 2-3홉 순환 구조 탐지
- **사용 조건**:
  - `include_topology=True` 또는 `analysis_type="advanced"` 필요
  - 3홉까지 거래 데이터 필요
- **기본 동작**: 기본 스코어링에서는 제외됨 (성능 최적화)

### 🚧 부분 구현 (그래프 관련)

#### E-102: Indirect Sanctions Exposure 🚧

- **상태**: PPR 기반 부분 구현
- **구현 위치**: `core/aggregation/ppr_connector.py`
- **기능**: PPR 알고리즘으로 간접 제재 노출 탐지
- **사용 조건**: 충분한 거래 히스토리 필요

---

## 📋 사용 방법

### 기본 스코어링 (빠름, 그래프 룰 제외)

```python
# address_analyzer.py
result = analyzer.analyze_address(
    address="0x...",
    chain="ethereum",
    transactions=txs,
    analysis_type="basic"  # B-201, B-202 제외
)
```

### 고급 스코어링 (느림, 그래프 룰 포함)

```python
# address_analyzer.py
result = analyzer.analyze_address(
    address="0x...",
    chain="ethereum",
    transactions=txs,
    analysis_type="advanced"  # B-201, B-202 포함
)
```

### 직접 제어

```python
# evaluator.py
fired_rules = rule_evaluator.evaluate_single_transaction(
    tx_data,
    include_topology=True  # B-201, B-202 포함
)
```

---

## 📊 구현 현황 요약표

| 카테고리           | 구현 완료        | 부분 구현 | 미구현 | 총계   |
| ------------------ | ---------------- | --------- | ------ | ------ |
| **Compliance (C)** | 2                | 1         | 0      | 3      |
| **Exposure (E)**   | 1                | 2         | 0      | 3      |
| **Behavior (B)**   | 7                | 0         | 5      | 12     |
| **그래프 룰**      | 2 (B-201, B-202) | 1 (E-102) | 0      | 3      |
| **총계**           | **11**           | **3**     | **5**  | **19** |

---

## 🔍 핵심 정리

### 그래프 관련 룰

- ✅ **B-201 (Layering Chain)**: 구현 완료, 하지만 기본 스코어링에서는 제외
- ✅ **B-202 (Cycle)**: 구현 완료, 하지만 기본 스코어링에서는 제외
- 🚧 **E-102 (Indirect Sanctions)**: PPR 기반 부분 구현

### 미구현 룰

- ❌ **B-401, B-402, B-403A, B-403B**: 주소 상태 관리 시스템 필요
- ❌ **B-501**: 동적 점수 할당 필요
- ❌ **B-502**: 복합 집계 및 그룹화 필요

### 성능 최적화

- 기본 스코어링에서는 그래프 룰(B-201, B-202) 제외
- 고급 분석(`analysis_type="advanced"`)에서만 그래프 룰 포함
- 이유: 그래프 분석은 계산 비용이 높음
