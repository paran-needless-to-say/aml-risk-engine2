# 현재 구현된 룰 요약

## 📊 전체 현황

**총 룰 수**: 19개

- ✅ **구현 완료**: 11개
- 🚧 **부분 구현**: 3개
- ❌ **미구현**: 5개

---

## ✅ 구현 완료 룰 (11개)

### Compliance (C) - 3개

#### C-001: Sanction Direct Touch ✅

- **점수**: 30점 (HIGH)
- **의미**: 제재 대상 주소와 직접 거래
- **조건**:
  - `from` 또는 `to` 주소가 SDN_LIST에 포함
  - 거래액 >= 1 USD
- **예외**: CEX 내부 거래 제외

#### C-003: High-Value Single Transfer ✅

- **점수**: 20점 (MEDIUM)
- **의미**: 단일 고액 거래
- **조건**: 거래액 >= 7,000 USD
- **예외**: CEX 내부 거래 제외

#### C-004: High-Value Repeated Transfer (24h) ✅

- **점수**: 20점 (MEDIUM)
- **의미**: 24시간 내 반복 고액 거래
- **조건**:
  - 24시간 내 3회 이상 거래
  - 각 거래 >= 3,000 USD
  - 총액 >= 10,000 USD

---

### Exposure (E) - 1개

#### E-101: Mixer Direct Exposure ✅

- **점수**: 25점 (HIGH)
- **의미**: 믹서에서 직접 유입
- **조건**:
  - `from` 주소가 MIXER_LIST에 포함
  - 거래액 >= 20 USD
- **예외**: REWARD_PAYOUT 제외

---

### Behavior (B) - 7개

#### B-101: Burst (10m) ✅

- **점수**: 15점 (MEDIUM)
- **의미**: 10분 내 급증 거래
- **조건**: 10분 내 3회 이상 거래
- **쿨다운**: 30분

#### B-102: Rapid Sequence (1m) ✅

- **점수**: 20점 (HIGH)
- **의미**: 1분 내 급속 연속 거래
- **조건**: 1분 내 5회 이상 거래
- **쿨다운**: 15분

#### B-103: Inter-arrival Std High ✅

- **점수**: 10점 (LOW)
- **의미**: 거래 간격 불규칙 패턴
- **조건**:
  - 최소 10개 거래 필요
  - 거래 간격 표준편차 >= 2.0
  - 거래액 >= 50 USD

#### B-201: Layering Chain (same token) ✅ **그래프 룰**

- **점수**: 25점 (HIGH)
- **의미**: 3홉 이상 레이어링 체인 (자금 세탁)
- **조건**:
  - 동일 토큰
  - 3홉 이상
  - 각 홉 금액 차이 <= 5%
  - 최소 거래액 >= 100 USD
- **⚠️ 주의**: 기본 스코어링에서는 제외 (`analysis_type="advanced"` 필요)

#### B-202: Cycle (length 2-3, same token) ✅ **그래프 룰**

- **점수**: 30점 (HIGH)
- **의미**: 2-3홉 순환 거래 패턴
- **조건**:
  - 동일 토큰
  - 순환 길이: 2-3홉
  - 순환 총액 >= 100 USD
- **⚠️ 주의**: 기본 스코어링에서는 제외 (`analysis_type="advanced"` 필요)

#### B-203: Fan-out (10m bucket) ✅

- **점수**: 20점 (MEDIUM)
- **의미**: 10분 내 한 주소에서 여러 주소로 대량 송금
- **조건**:
  - 10분 버킷 내
  - 고유 수신 주소 >= 5개
  - 총액 >= 1,000 USD
  - 각 거래 >= 100 USD

#### B-204: Fan-in (10m bucket) ✅

- **점수**: 20점 (MEDIUM)
- **의미**: 10분 내 여러 주소에서 한 주소로 대량 입금
- **조건**:
  - 10분 버킷 내
  - 고유 송신 주소 >= 5개
  - 총액 >= 1,000 USD
  - 각 거래 >= 100 USD

---

## 🚧 부분 구현 룰 (3개)

### Compliance (C) - 1개

#### C-002: High-Risk Jurisdiction VASP 🚧

- **점수**: 20점 (MEDIUM)
- **상태**: 룰 구조는 있으나 백엔드 데이터 필요
- **필요한 데이터**: `counterparty.country`, `counterparty.type`, `counterparty.safe_vasp`
- **작동 조건**: 백엔드에서 counterparty 정보 제공 시 자동 작동

---

### Exposure (E) - 2개

#### E-102: Indirect Sanctions Exposure (≤2 hops) 🚧

- **점수**: 30점 (HIGH)
- **상태**: PPR 기반 부분 구현
- **구현 방식**: PPR(PageRank) 알고리즘으로 간접 제재 노출 탐지
- **필요한 데이터**: 3홉까지 거래 히스토리

#### E-103: Counterparty Quality Risk 🚧

- **점수**: 10~20점 (기본 15점) (MEDIUM)
- **상태**: 룰 구조는 있으나 백엔드 데이터 필요
- **필요한 데이터**: `counterparty.risk_score` (0.7 이상)
- **작동 조건**: 백엔드에서 `counterparty.risk_score` 제공 시 자동 작동

---

## ❌ 미구현 룰 (5개)

### Behavior (B) - 5개

#### B-401: First 7 Days Burst ❌

- **점수**: 20점 (MEDIUM)
- **미구현 이유**: 주소 상태 관리 필요
- **필요한 것**: 주소 생성일, 첫 7일간 거래 집계

#### B-402: Reactivation ❌

- **점수**: 15점 (LOW)
- **미구현 이유**: 주소 상태 관리 필요
- **필요한 것**: 주소 생성일, 마지막 거래일, 비활성 기간 계산

#### B-403A: Lifecycle A — Young but Busy ❌

- **점수**: 10점 (LOW)
- **미구현 이유**: 주소 상태 관리 필요
- **필요한 것**: 주소 나이, 30일간 거래 통계

#### B-403B: Lifecycle B — Old and Rare High Value ❌

- **점수**: 10점 (LOW)
- **미구현 이유**: 주소 상태 관리 필요
- **필요한 것**: 주소 나이, 총 거래 통계

#### B-501: High-Value Buckets ❌

- **점수**: 동적 (5~20점) (MEDIUM)
- **미구현 이유**: 동적 점수 할당 필요
- **필요한 것**: 거래 금액에 따른 버킷 분류 및 동적 점수

#### B-502: Structuring Pattern ❌

- **점수**: 10점 (LOW)
- **미구현 이유**: 복합 집계 및 그룹화 필요
- **필요한 것**: 반올림 값 그룹화, 그룹별 집계

---

## 📋 룰별 구현 방식

| 룰 ID     | 구현 방식     | 파일 위치                      |
| --------- | ------------- | ------------------------------ |
| **C-001** | 단일 트랜잭션 | `core/rules/evaluator.py`      |
| **C-003** | 단일 트랜잭션 | `core/rules/evaluator.py`      |
| **C-004** | 윈도우 집계   | `core/aggregation/window.py`   |
| **E-101** | 단일 트랜잭션 | `core/rules/evaluator.py`      |
| **B-101** | 윈도우 집계   | `core/aggregation/window.py`   |
| **B-102** | 윈도우 집계   | `core/aggregation/window.py`   |
| **B-103** | 통계 계산     | `core/aggregation/stats.py`    |
| **B-201** | 그래프 분석   | `core/aggregation/topology.py` |
| **B-202** | 그래프 분석   | `core/aggregation/topology.py` |
| **B-203** | 버킷 집계     | `core/aggregation/bucket.py`   |
| **B-204** | 버킷 집계     | `core/aggregation/bucket.py`   |

---

## 🎯 사용 방법

### 기본 스코어링 (빠름)

```python
# B-201, B-202 제외
result = analyzer.analyze_address(
    address="0x...",
    chain="ethereum",
    transactions=txs,
    analysis_type="basic"  # 기본값
)
```

### 고급 스코어링 (느림, 그래프 룰 포함)

```python
# B-201, B-202 포함
result = analyzer.analyze_address(
    address="0x...",
    chain="ethereum",
    transactions=txs,
    analysis_type="advanced"  # 그래프 룰 포함
)
```

---

## 📊 점수 분포

| 카테고리           | 구현 완료 | 부분 구현 | 미구현 | 총계   |
| ------------------ | --------- | --------- | ------ | ------ |
| **Compliance (C)** | 2         | 1         | 0      | 3      |
| **Exposure (E)**   | 1         | 2         | 0      | 3      |
| **Behavior (B)**   | 7         | 0         | 5      | 12     |
| **총계**           | **11**    | **3**     | **5**  | **19** |

---

## 💡 핵심 정리

### ✅ 잘 작동하는 룰들

- **Compliance 룰**: 제재 주소, 고액 거래 탐지
- **Exposure 룰**: 믹서 직접 노출 탐지
- **Behavior 룰**: Burst, Rapid Sequence, Fan-out/in 패턴 탐지
- **그래프 룰**: Layering Chain, Cycle (고급 분석 시)

### 🚧 백엔드 데이터 필요

- **C-002, E-103**: counterparty 정보 필요
- **E-102**: PPR 기반으로 부분 작동

### ❌ 제외 권장

- **B-401, B-402, B-403A, B-403B**: 주소 상태 관리 필요 (복잡)
- **B-501, B-502**: 구현 가능하지만 대체 룰로 커버 가능

---

## 📝 참고 문서

- `docs/RISK_SCORING_IMPLEMENTATION_STATUS.md`: 상세 구현 현황
- `docs/UNIMPLEMENTED_RULES_SUMMARY.md`: 미구현 룰 상세 설명
- `rules/tracex_rules.yaml`: 룰 정의
