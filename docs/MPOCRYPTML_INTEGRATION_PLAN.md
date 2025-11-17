# MPOCryptoML 통합 계획

## 📚 논문 요약

**MPOCryptoML: Multi-Pattern based Off-Chain Crypto Money Laundering Detection**

- **저자**: Yasaman Samadi, Hai Dong, Xiaoyu Xia
- **arXiv**: https://arxiv.org/abs/2508.12641v1
- **성능**: Precision +9.13%, Recall +10.16%, F1 +7.63%, Accuracy +10.19%

## 🎯 핵심 패턴 정의

논문에서 정의한 수학적 패턴:

### 1. Fan-in

```
fan-in(v) = d_i^-(S) = Σ_{v_k ∈ M_{l-1} ∧ (k,v) ∈ E} e_{kv}
```

- **의미**: 여러 주소에서 하나의 주소로 자금이 집중
- **TRACE-X 룰**: B-204 (Fan-in 10m bucket)

### 2. Fan-out

```
fan-out(v) = d_i^+(S) = Σ_{v_j ∈ M_{l+1} ∧ (v,j) ∈ E} e_{vj}
```

- **의미**: 하나의 주소에서 여러 주소로 자금이 분산
- **TRACE-X 룰**: B-203 (Fan-out 10m bucket)

### 3. Gather-Scatter

```
gather-scatter(v) = fan-in(v) + fan-out(v)
```

- **의미**: Fan-in과 Fan-out의 결합
- **용도**: 주소의 전체 연결성 평가

### 4. Stack

```
P = (v1, v2, ..., vk) where v_i ∈ M_l and v_{i+1} ∈ M_{l+1}
```

- **의미**: 방향성 경로 (directed path)
- **TRACE-X 룰**: B-201 (Layering Chain)과 유사

### 5. Bipartite

```
∀(u, v) ∈ E, u ∈ M_l ⇒ v ∈ M_{l+1}
```

- **의미**: 두 레이어로 나뉜 그래프 구조
- **용도**: 특정 거래 패턴 탐지

## ✅ 구현 완료

### 1. MPOCryptoMLPatternDetector (`core/aggregation/mpocryptml_patterns.py`)

논문의 수학적 정의에 따른 패턴 탐지기:

```python
from core.aggregation import MPOCryptoMLPatternDetector

detector = MPOCryptoMLPatternDetector()
detector.build_from_transactions(transactions)

# Fan-in 계산
fan_in_value = detector.fan_in(address)
fan_in_count = detector.fan_in_count(address)

# Fan-out 계산
fan_out_value = detector.fan_out(address)
fan_out_count = detector.fan_out_count(address)

# Gather-Scatter
gather_scatter = detector.gather_scatter(address)

# 패턴 탐지
fan_in_pattern = detector.detect_fan_in_pattern(
    address,
    min_fan_in_count=5,
    min_total_value=1000.0,
    min_each_value=100.0
)

fan_out_pattern = detector.detect_fan_out_pattern(
    address,
    min_fan_out_count=5,
    min_total_value=1000.0,
    min_each_value=100.0
)

# Stack 패턴
stack_paths = detector.detect_stack_pattern(
    address,
    min_length=3,
    min_path_value=100.0
)

# Bipartite 패턴
bipartite = detector.detect_bipartite_pattern([address])
```

### 2. BucketEvaluator (`core/aggregation/bucket.py`)

시간 버킷 기반 집계 평가기:

- **B-203 (Fan-out 10m bucket)**: 10분 내 여러 주소로 분산
- **B-204 (Fan-in 10m bucket)**: 10분 내 여러 주소에서 집중

```python
from core.aggregation import BucketEvaluator

bucket_eval = BucketEvaluator()
bucket_eval.add_transaction(tx, bucket_spec)
bucket_txs = bucket_eval.get_bucket_transactions(tx, bucket_spec)
```

### 3. RuleEvaluator 통합

`core/rules/evaluator.py`에 버킷 기반 룰 평가 추가:

- `bucket` 키가 있으면 `BucketEvaluator` 사용
- `window` 키가 있으면 `WindowEvaluator` 사용
- 기존 단일 트랜잭션 룰은 그대로 유지

## 🔄 통합 방식

### 현재 구조

```
RuleEvaluator
├── WindowEvaluator (C-004, B-101, B-102)
├── BucketEvaluator (B-203, B-204) ← 새로 추가
└── MPOCryptoMLPatternDetector (패턴 분석) ← 새로 추가
```

### 사용 흐름

1. **트랜잭션 수신**: `RuleEvaluator.evaluate_single_transaction()`
2. **룰 타입 판별**: `bucket`, `window`, 또는 단일 트랜잭션
3. **버킷 룰 평가**: `BucketEvaluator.evaluate_bucket_rule()`
   - 10분 버킷으로 그룹화
   - 집계 조건 평가 (distinct_gte, sum_gte, every_gte)
4. **패턴 분석** (선택적): `MPOCryptoMLPatternDetector`로 상세 분석

## 📋 TRACE-X 룰 매핑

| TRACE-X 룰                  | MPOCryptoML 패턴 | 상태                                     |
| --------------------------- | ---------------- | ---------------------------------------- |
| B-203: Fan-out (10m bucket) | Fan-out          | ✅ 구현 완료                             |
| B-204: Fan-in (10m bucket)  | Fan-in           | ✅ 구현 완료                             |
| B-201: Layering Chain       | Stack            | 🚧 구현 가능 (detect_stack_pattern 활용) |
| B-202: Cycle                | -                | 🚧 구현 필요 (순환 탐지 추가)            |

## 🚀 다음 단계

### 1. B-201 (Layering Chain) 구현

`MPOCryptoMLPatternDetector.detect_stack_pattern()` 활용:

```python
# B-201 룰 평가
stack_paths = detector.detect_stack_pattern(
    address,
    min_length=3,  # 3홉 이상
    min_path_value=100.0  # 최소 100 USD
)

# 같은 토큰 체크
# 각 홉 금액 차이 <= 5% 체크
```

### 2. B-202 (Cycle) 구현

순환 탐지 기능 추가:

```python
def detect_cycle_pattern(
    self,
    vertex: str,
    min_length: int = 2,
    max_length: int = 3,
    min_cycle_value: float = 100.0
) -> List[Dict[str, Any]]:
    """순환 패턴 탐지"""
    # DFS로 순환 탐지
    # v1 → v2 → ... → vk → v1
```

### 3. 실험 및 검증

- **데이터셋**: Elliptic++, Ethereum fraud detection, Wormhole
- **평가 지표**: Precision, Recall, F1-score, Accuracy
- **비교**: 기존 룰 기반 방법과 성능 비교

## 💡 활용 방안

### 1. 주소 분석 API 강화

`/api/analyze/address` 엔드포인트에 패턴 정보 추가:

```json
{
  "target_address": "0x...",
  "risk_score": 78,
  "risk_level": "high",
  "patterns": {
    "fan_in": {
      "detected": true,
      "count": 7,
      "total_value": 5000.0
    },
    "fan_out": {
      "detected": true,
      "count": 5,
      "total_value": 3000.0
    },
    "gather_scatter": 8000.0,
    "stack_paths": [...],
    "bipartite": {...}
  }
}
```

### 2. 룰 점수 조정

MPOCryptoML 패턴 탐지 결과를 룰 점수에 반영:

- Fan-in/Fan-out 패턴이 탐지되면 추가 점수 부여
- Gather-Scatter 값이 높으면 리스크 증가
- Stack 패턴이 길면 레이어링 의심

### 3. 시각화

그래프 구조 시각화:

- Fan-in/Fan-out 구조를 노드 크기로 표현
- Stack 경로를 하이라이트
- Bipartite 구조를 레이어로 표시

## 📊 예상 효과

논문 결과를 기반으로:

- **Precision**: +9.13% 향상
- **Recall**: +10.16% 향상
- **F1-score**: +7.63% 향상
- **Accuracy**: +10.19% 향상

특히 **Fan-in/Fan-out 패턴**을 정확히 탐지하여:

- 자금 세탁의 **레이어링 단계** 탐지 강화
- **스머핑(Smurfing)** 패턴 탐지 개선
- **자금 집결/분산** 패턴 인식 향상
