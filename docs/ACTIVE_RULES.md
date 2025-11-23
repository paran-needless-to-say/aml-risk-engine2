# 실제 구현 및 발동되는 룰 목록

## 📋 요약

- **전체 룰 수**: 22개
- **실제 구현 및 발동**: 18개 (Basic 모드), 20개 (Advanced 모드)
- **미구현**: 4개 (state 룰)
- **조건부 구현**: 1개 (E-103, 백엔드 데이터 필요)

---

## ✅ 구현 및 발동되는 룰 (Basic 모드: 18개)

### C축 (Compliance) - 4개

- ✅ **C-001**: Sanction Direct Touch (30점)
- ✅ **C-002**: High-Risk Jurisdiction VASP (20점)
- ✅ **C-003**: High-Value Single Transfer (25점)
- ✅ **C-004**: High-Value Repeated Transfer (24h) (20점)

### E축 (Exposure) - 5개

- ✅ **E-101**: Mixer Direct Exposure (32점)
- ✅ **E-102**: Indirect Sanctions Exposure (≤2 hops) (39점) - PPR 기반 탐지
- ⚠️ **E-103**: Counterparty Quality Risk (19점) - 백엔드에서 `counterparty.risk_score` 제공 시 작동
- ✅ **E-104**: Bridge Direct Exposure (19점)
- ✅ **E-105**: Scam Direct Exposure (26점)

### B축 (Behavior) - 9개

#### 기본 패턴 (B-1xx)

- ✅ **B-101**: Burst (10m) (15점)
- ✅ **B-102**: Rapid Sequence (1m) (20점)
- ✅ **B-103**: Inter-arrival Std High (10점) - Prerequisites 및 통계 계산 포함

#### 그래프 구조 패턴 (B-2xx) - **Advanced 모드에서만 작동**

- ⚙️ **B-201**: Layering Chain (25점) - Advanced 모드 전용
- ⚙️ **B-202**: Cycle (30점) - Advanced 모드 전용
- ✅ **B-203**: Fan-out (10m bucket) (20점)
- ✅ **B-204**: Fan-in (10m bucket) (20점)

#### 고액 거래 패턴 (B-5xx)

- ✅ **B-501**: High-Value Buckets (동적 점수: 3~30점)
- ✅ **B-502**: Structuring — Rounded Value Repetition (10점)

---

## ⚙️ Advanced 모드 전용 룰 (2개)

Advanced 모드(`analysis_type="advanced"`)에서만 발동되는 룰:

- **B-201**: Layering Chain (same token) - 3-hop 이상 레이어링 체인 탐지
- **B-202**: Cycle (length 2-3, same token) - 사이클 패턴 탐지

**참고**: Basic 모드에서는 성능 최적화를 위해 이 룰들이 제외됩니다.

---

## ❌ 미구현 룰 (4개)

다음 룰들은 YAML 파일에 정의되어 있지만, 코드에서 `state` 필드가 있어서 **건너뛰어집니다** (`evaluator.py` 74-75줄):

- ❌ **B-401**: First 7 Days Burst
- ❌ **B-402**: Reactivation
- ❌ **B-403A**: Lifecycle A — Young but Busy
- ❌ **B-403B**: Lifecycle B — Old and Rare High Value

**이유**: `state` 룰은 아직 미구현입니다. (주소의 생명주기 정보 필요)

---

## ⚠️ 조건부 구현 룰 (1개)

- ⚠️ **E-103**: Counterparty Quality Risk (19점)

**조건**: 백엔드에서 `counterparty.risk_score` 필드를 제공해야 작동합니다.

현재 코드에서는 `tx_data.get("counterparty.risk_score")`가 없으면 이 룰은 건너뜁니다.

---

## 🔧 룰 타입별 구현 상태

| 룰 타입                  | 상태                      | 구현 파일                                             |
| ------------------------ | ------------------------- | ----------------------------------------------------- |
| **단일 트랜잭션 룰**     | ✅ 구현됨                 | `evaluator.py` `_match_rule()`, `_check_conditions()` |
| **윈도우 룰**            | ✅ 구현됨                 | `aggregation/window.py`                               |
| **버킷 룰**              | ✅ 구현됨                 | `aggregation/bucket.py`                               |
| **Topology 룰**          | ✅ 구현됨 (Advanced 전용) | `aggregation/topology.py`                             |
| **PPR 룰 (E-102)**       | ✅ 구현됨                 | `evaluator.py` `_evaluate_e102_with_ppr()`            |
| **통계 룰 (B-103)**      | ✅ 구현됨                 | `evaluator.py` `_evaluate_b103_with_stats()`          |
| **동적 점수 룰 (B-501)** | ✅ 구현됨                 | `evaluator.py` 172-198줄                              |
| **State 룰**             | ❌ 미구현                 | -                                                     |

---

## 📊 Basic vs Advanced 모드 비교

| 모드         | 발동되는 룰 수 | 특징                                            |
| ------------ | -------------- | ----------------------------------------------- |
| **Basic**    | 18개           | 빠름 (1-2초), 그래프 구조 분석 제외             |
| **Advanced** | 20개           | 느림 (5-30초), 모든 룰 포함 (B-201, B-202 포함) |

---

## 🔍 룰 평가 순서

`evaluator.py`의 `evaluate_single_transaction()` 메서드에서 룰 평가 순서:

1. **State 룰 건너뛰기** (B-401, B-402, B-403A, B-403B)
2. **E-103 조건부 체크** (백엔드 데이터 필요)
3. **E-102 PPR 평가** (간접 제재 노출)
4. **B-103 통계 평가** (Prerequisites 체크 포함)
5. **B-201, B-202 Topology 평가** (Advanced 모드에서만)
6. **B-501 동적 점수 평가** (거래 금액 기반)
7. **버킷 룰 평가** (B-203, B-204, B-502)
8. **윈도우 룰 평가** (B-101, B-102, C-004)
9. **단일 트랜잭션 룰 평가** (C-001, C-003, E-101, E-104, E-105 등)

---

## 💡 사용 예시

### Basic 모드 (기본 스코어링)

```python
analyzer = AddressAnalyzer()
result = analyzer.analyze_address(
    address="0x...",
    chain="ethereum",
    transactions=[...],
    analysis_type="basic"  # ← 18개 룰만 평가
)
```

### Advanced 모드 (심층 분석)

```python
analyzer = AddressAnalyzer()
result = analyzer.analyze_address(
    address="0x...",
    chain="ethereum",
    transactions=[...],
    analysis_type="advanced"  # ← 20개 룰 모두 평가 (B-201, B-202 포함)
)
```

---

## 📝 참고

- 룰 정의: `rules/tracex_rules.yaml`
- 룰 평가기: `core/rules/evaluator.py`
- 주소 분석기: `core/scoring/address_analyzer.py`
- 윈도우 평가기: `core/aggregation/window.py`
- Topology 평가기: `core/aggregation/topology.py`
