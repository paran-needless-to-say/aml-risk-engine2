# 3홉 데이터 기반 Topology 룰 구현

## 📊 개요

백엔드에서 **3홉까지 거래 데이터**를 제공하면, B-201 (Layering Chain)과 B-202 (Cycle) 룰을 구현할 수 있습니다.

---

## 🎯 3홉 데이터 구조

### 현재 API 입력 (1홉만)

```json
{
  "address": "0xABC...",
  "transactions": [
    {"from": "0xABC", "to": "0xDEF", ...},  // A → B
    {"from": "0xABC", "to": "0xGHI", ...}  // A → C
  ]
}
```

### 3홉 데이터 제공 시

```json
{
  "address": "0xABC...",
  "transactions": [
    // 직접 거래 (0홉)
    {"from": "0xABC", "to": "0xDEF", ...},

    // 1홉 거래 (0xDEF의 거래)
    {"from": "0xDEF", "to": "0xGHI", ...},
    {"from": "0xDEF", "to": "0xJKL", ...},

    // 2홉 거래 (0xGHI의 거래)
    {"from": "0xGHI", "to": "0xMNO", ...},

    // 3홉 거래 (0xMNO의 거래)
    {"from": "0xMNO", "to": "0xPQR", ...}
  ]
}
```

**중요**: `transactions` 배열에 **모든 홉의 거래가 포함**되어야 합니다.

---

## 🔧 구현 내용

### 1. TopologyEvaluator 모듈

**파일**: `core/aggregation/topology.py`

**주요 기능**:

- `evaluate_layering_chain()`: B-201 룰 평가
- `evaluate_cycle()`: B-202 룰 평가
- `_build_token_graphs()`: 토큰별 그래프 분리
- `_find_layering_chain_in_graph()`: DFS로 레이어링 체인 탐색
- `_find_cycle_in_graph()`: 순환 구조 탐지

### 2. RuleEvaluator 통합

**파일**: `core/rules/evaluator.py`

**변경 사항**:

- `TopologyEvaluator` 인스턴스 추가
- B-201, B-202 룰 평가 로직 추가
- `_evaluate_topology_rule()` 메서드 구현

---

## 📋 B-201: Layering Chain 룰

### 룰 정의

```yaml
- id: "B-201"
  name: "Layering Chain (same token)"
  topology:
    same_token: true
    hop_length_gte: 3
    hop_amount_delta_pct_lte: 5
    min_usd_value: 100
  score: 25
```

### 동작 방식

1. **그래프 구축**: 3홉 데이터로 방향 그래프 생성
2. **토큰별 분리**: `same_token: true`이면 토큰별로 그래프 분리
3. **경로 탐색**: DFS로 3홉 이상 경로 탐색
4. **금액 차이 체크**: 각 홉 금액 차이 <= 5%
5. **최소 금액 체크**: 각 홉 >= 100 USD
6. **룰 발동**: 조건 만족 시 25점 (HIGH)

### 예시

```
A → B (100 USD)
B → C (102 USD)  // 2% 차이
C → D (98 USD)   // 2% 차이
```

→ **B-201 룰 발동** ✅

---

## 📋 B-202: Cycle 룰

### 룰 정의

```yaml
- id: "B-202"
  name: "Cycle (length 2-3, same token)"
  topology:
    same_token: true
    cycle_length_in: [2, 3]
    cycle_total_usd_gte: 100
  score: 30
```

### 동작 방식

1. **그래프 구축**: 3홉 데이터로 방향 그래프 생성
2. **토큰별 분리**: `same_token: true`이면 토큰별로 그래프 분리
3. **순환 탐지**: 2-3홉 순환 구조 탐지
4. **총액 체크**: 순환 총액 >= 100 USD
5. **룰 발동**: 조건 만족 시 30점 (HIGH)

### 예시

```
A → B (50 USD)
B → C (50 USD)
C → A (50 USD)  // 3홉 순환
```

→ **B-202 룰 발동** ✅

---

## ✅ 구현 완료 상태

### 구현된 룰

- ✅ **B-201**: Layering Chain (3홉 데이터 필요)
- ✅ **B-202**: Cycle (3홉 데이터 필요)

### 미구현 룰 (4개)

- ❌ **B-401**: First 7 Days Burst (주소 상태 관리 필요)
- ❌ **B-402**: Reactivation (주소 상태 관리 필요)
- ❌ **B-501**: High-Value Buckets (동적 점수 할당 필요)
- ❌ **B-502**: Structuring Pattern (복합 집계 필요)

---

## ⚠️ 주의사항

### 1. 데이터 구조

백엔드에서 제공하는 `transactions` 배열에 **모든 홉의 거래가 포함**되어야 합니다.

**올바른 예**:

```json
{
  "transactions": [
    {"from": "0xABC", "to": "0xDEF", ...},  // 0홉
    {"from": "0xDEF", "to": "0xGHI", ...},  // 1홉
    {"from": "0xGHI", "to": "0xJKL", ...}   // 2홉
  ]
}
```

**잘못된 예**:

```json
{
  "transactions": [
    {"from": "0xABC", "to": "0xDEF", ...}   // 0홉만 있음
  ]
}
```

### 2. 성능 고려사항

- **그래프 크기**: 3홉 데이터는 상당히 많은 거래를 포함할 수 있음
- **DFS 탐색**: 경로 탐색 시 최대 10홉까지만 탐색 (무한 루프 방지)
- **토큰별 분리**: `same_token: true`이면 토큰별로 그래프를 분리하여 탐색

### 3. 백엔드 요구사항

백엔드에서 다음을 제공해야 합니다:

- 주소 분석 시 1-3홉 거래 데이터 포함
- 각 거래의 `from`, `to`, `amount_usd`, `asset_contract` 정보
- 거래 시간 정보 (`timestamp`)

---

## 🧪 테스트 방법

### 1. 데모 데이터 생성

3홉 경로를 포함한 테스트 데이터 생성:

```python
transactions = [
    # 0홉
    {"from": "0xABC", "to": "0xDEF", "amount_usd": 100, "asset_contract": "0xTOKEN1"},
    # 1홉
    {"from": "0xDEF", "to": "0xGHI", "amount_usd": 102, "asset_contract": "0xTOKEN1"},
    # 2홉
    {"from": "0xGHI", "to": "0xJKL", "amount_usd": 98, "asset_contract": "0xTOKEN1"},
]
```

### 2. API 호출

```bash
curl -X POST http://localhost:5000/api/analyze/address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xABC...",
    "chain": "ethereum",
    "transactions": [...]
  }'
```

### 3. 예상 결과

```json
{
  "target_address": "0xABC...",
  "risk_score": 55,
  "risk_level": "high",
  "fired_rules": [
    { "rule_id": "B-201", "score": 25 },
    { "rule_id": "B-202", "score": 30 }
  ],
  "risk_tags": ["layering_chain", "cycle_pattern"],
  "explanation": "..."
}
```

---

## 📚 관련 문서

- `docs/GRAPH_ANALYSIS_LIMITATION.md`: 그래프 분석의 한계
- `docs/RULE_IMPLEMENTATION_STATUS.md`: 룰 구현 상태
- `docs/WHY_UNIMPLEMENTED_SIMPLE.md`: 미구현 룰 설명
