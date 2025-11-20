# AI 기반 룰 가중치 학습 가이드

## 🎯 개요

각 룰의 특성(axis, severity, 점수, 패턴 유형)을 반영하여 최적의 가중치를 학습하는 AI 모듈입니다.

---

## 📊 룰 특성 분석

### 현재 룰들의 특성

| 룰 ID     | Axis           | Severity | Base Score | Pattern Type | 특성                |
| --------- | -------------- | -------- | ---------- | ------------ | ------------------- |
| **C-001** | C (Compliance) | HIGH     | 30         | single       | 제재 주소 직접 거래 |
| **C-003** | C (Compliance) | MEDIUM   | 20         | single       | 고액 단일 거래      |
| **C-004** | C (Compliance) | MEDIUM   | 20         | window       | 고액 반복 거래      |
| **E-101** | E (Exposure)   | HIGH     | 25         | single       | 믹서 직접 노출      |
| **B-101** | B (Behavior)   | MEDIUM   | 15         | window       | Burst 패턴          |
| **B-102** | B (Behavior)   | HIGH     | 20         | window       | Rapid Sequence      |
| **B-103** | B (Behavior)   | LOW      | 10         | stats        | 통계 패턴           |
| **B-201** | B (Behavior)   | HIGH     | 25         | topology     | 레이어링 체인       |
| **B-202** | B (Behavior)   | HIGH     | 30         | topology     | 순환 패턴           |
| **B-203** | B (Behavior)   | MEDIUM   | 20         | bucket       | Fan-out             |
| **B-204** | B (Behavior)   | MEDIUM   | 20         | bucket       | Fan-in              |

---

## 🤖 AI 기반 가중치 학습

### 1. 피처 추출

각 룰의 특성을 피처로 변환:

```python
# 피처 벡터 구성
features = [
    # Axis (one-hot encoding)
    is_compliance,      # C 룰인가?
    is_exposure,        # E 룰인가?
    is_behavior,        # B 룰인가?

    # Severity (one-hot encoding)
    is_high_severity,   # HIGH인가?
    is_medium_severity, # MEDIUM인가?
    is_low_severity,    # LOW인가?

    # Base score (정규화)
    normalized_score,   # 점수 / 30

    # Pattern type (one-hot encoding)
    is_single,          # 단일 거래 패턴?
    is_window,          # 윈도우 패턴?
    is_bucket,          # 버킷 패턴?
    is_topology,        # 그래프 패턴?
    is_stats,           # 통계 패턴?

    # 룰 조합 피처
    combination_score,  # 위험한 조합인가?
]
```

---

### 2. 학습 데이터 구축

```python
# 학습 데이터 형식
training_data = [
    (
        rule_results,      # 발동된 룰 목록
        actual_risk_score, # 실제 리스크 점수 (0~100)
        tx_context         # 트랜잭션 컨텍스트 (선택적)
    ),
    # ...
]

# 예시
example = (
    [
        {"rule_id": "C-001", "score": 30, "axis": "C", "severity": "HIGH"},
        {"rule_id": "E-101", "score": 25, "axis": "E", "severity": "HIGH"},
    ],
    75.0,  # 실제 리스크 점수
    {
        "amount_usd": 5000,
        "is_sanctioned": True,
        "is_mixer": True
    }
)
```

---

### 3. 모델 학습

```python
from core.scoring.ai_weight_learner import RuleWeightLearner

# 학습기 생성
learner = RuleWeightLearner(use_ai=True)

# 학습 데이터 로드
training_data = load_training_data()  # 과거 거래 데이터

# 모델 학습
learner.train(training_data)
```

---

## 💡 규칙 기반 가중치 (AI 없이도 사용 가능)

AI 모델이 없어도 룰 특성을 반영한 가중치를 사용할 수 있습니다:

```python
# 규칙 기반 가중치 계산
def calculate_rule_based_weight(rule_feature):
    weight = 1.0

    # Severity 기반
    if rule_feature.severity == "HIGH":
        weight *= 1.2
    elif rule_feature.severity == "MEDIUM":
        weight *= 1.0
    elif rule_feature.severity == "LOW":
        weight *= 0.8

    # Axis 기반
    if rule_feature.axis == "C":  # Compliance는 중요
        weight *= 1.1
    elif rule_feature.axis == "E":  # Exposure도 중요
        weight *= 1.1
    elif rule_feature.axis == "B":  # Behavior는 상대적으로 덜 중요
        weight *= 0.95

    # 패턴 유형 기반
    if rule_feature.pattern_type == "topology":  # 그래프 패턴은 중요
        weight *= 1.15
    elif rule_feature.pattern_type == "window":  # 시간 패턴도 중요
        weight *= 1.05

    return weight
```

---

## 🔧 실제 사용 방법

### 1. 스코어링 엔진에 통합

```python
# core/scoring/engine.py 수정
from core.scoring.ai_weight_learner import RuleWeightLearner

class TransactionScorer:
    def __init__(self, rules_path: str = "rules/tracex_rules.yaml"):
        self.rule_evaluator = RuleEvaluator(rules_path)
        self.list_loader = ListLoader()

        # 가중치 학습기 추가
        self.weight_learner = RuleWeightLearner(use_ai=True)
        # 학습된 모델 로드 (선택적)
        # self.weight_learner.load_model("models/rule_weights.pkl")

    def _calculate_risk_score(self, rule_results: List[Dict[str, Any]]) -> float:
        """가중치를 적용한 리스크 점수 계산"""
        # 가중치 계산
        weights = self.weight_learner.get_weights(rule_results)

        # 가중치 적용 점수 계산
        total_score = 0.0
        for rule in rule_results:
            rule_id = rule.get("rule_id")
            base_score = rule.get("score", 0)
            weight = weights.get(rule_id, 1.0)

            total_score += base_score * weight

        return min(100.0, total_score)
```

---

### 2. 룰 조합 보너스 자동 계산

```python
def _calculate_combination_bonus(self, rule_results):
    """AI가 학습한 룰 조합 보너스"""
    rule_ids = [r.get("rule_id") for r in rule_results]

    # 위험한 조합 확인
    dangerous_combinations = {
        ("C-001", "E-101"): 1.2,  # 제재 + 믹서 = 20% 보너스
        ("C-001", "B-201"): 1.15,  # 제재 + 레이어링 = 15% 보너스
        ("E-101", "B-202"): 1.18,  # 믹서 + 순환 = 18% 보너스
    }

    max_bonus = 1.0
    for (r1, r2), multiplier in dangerous_combinations.items():
        if r1 in rule_ids and r2 in rule_ids:
            max_bonus = max(max_bonus, multiplier)

    return max_bonus
```

---

## 📈 학습 데이터 수집

### 방법 1: 과거 거래 데이터 활용

```python
# core/scoring/data_collector.py
class TrainingDataCollector:
    """학습 데이터 수집기"""

    def collect_from_history(
        self,
        historical_transactions: List[Dict],
        ground_truth_labels: Dict[str, str]  # {tx_hash: "fraud" | "normal"}
    ) -> List[Tuple]:
        """과거 거래 데이터에서 학습 데이터 생성"""

        training_data = []

        for tx in historical_transactions:
            # 룰 평가
            rule_results = self.rule_evaluator.evaluate(tx)

            # 실제 리스크 점수 계산 (라벨 기반)
            ground_truth = ground_truth_labels.get(tx["tx_hash"], "normal")
            actual_score = self._label_to_score(ground_truth)

            # 컨텍스트
            tx_context = {
                "amount_usd": tx.get("amount_usd", 0),
                "is_sanctioned": tx.get("is_sanctioned", False),
                "is_mixer": tx.get("is_mixer", False),
            }

            training_data.append((rule_results, actual_score, tx_context))

        return training_data

    def _label_to_score(self, label: str) -> float:
        """라벨을 점수로 변환"""
        label_scores = {
            "fraud": 85.0,
            "suspicious": 60.0,
            "normal": 15.0,
            "low_risk": 5.0
        }
        return label_scores.get(label, 15.0)
```

---

### 방법 2: 전문가 라벨링

```python
# 전문가가 직접 라벨링한 데이터 사용
expert_labeled_data = [
    {
        "tx_hash": "0x...",
        "rule_results": [...],
        "expert_score": 75.0,  # 전문가가 평가한 점수
        "tx_context": {...}
    },
    # ...
]
```

---

## 🎯 룰 특성별 가중치 예시

### Severity 기반

```python
# HIGH 룰은 더 높은 가중치
C-001 (HIGH): 1.2배
E-101 (HIGH): 1.2배
B-102 (HIGH): 1.2배
B-201 (HIGH): 1.2배
B-202 (HIGH): 1.2배

# MEDIUM 룰은 기본 가중치
C-003 (MEDIUM): 1.0배
C-004 (MEDIUM): 1.0배
B-101 (MEDIUM): 1.0배

# LOW 룰은 낮은 가중치
B-103 (LOW): 0.8배
```

---

### Axis 기반

```python
# Compliance (C) 룰은 중요
C-001: 1.1배
C-003: 1.1배
C-004: 1.1배

# Exposure (E) 룰도 중요
E-101: 1.1배

# Behavior (B) 룰은 상대적으로 덜 중요
B-101: 0.95배
B-102: 0.95배
# 하지만 그래프 룰은 예외
B-201: 1.15배 (topology 패턴)
B-202: 1.15배 (topology 패턴)
```

---

### 패턴 유형 기반

```python
# 그래프 패턴은 중요
B-201 (topology): 1.15배
B-202 (topology): 1.15배

# 시간 패턴도 중요
B-101 (window): 1.05배
B-102 (window): 1.05배
C-004 (window): 1.05배

# 단일 거래 패턴은 기본
C-001 (single): 1.0배
C-003 (single): 1.0배
E-101 (single): 1.0배
```

---

## 🔄 룰 조합 상호작용

### 위험한 조합 예시

```python
# 제재 + 믹서 = 매우 위험
C-001 (30점) + E-101 (25점) = 55점
→ 가중치 적용: 55 * 1.2 = 66점

# 제재 + 레이어링 = 위험
C-001 (30점) + B-201 (25점) = 55점
→ 가중치 적용: 55 * 1.15 = 63.25점

# 믹서 + 순환 = 위험
E-101 (25점) + B-202 (30점) = 55점
→ 가중치 적용: 55 * 1.18 = 64.9점
```

---

## 📝 구현 단계

### 1단계: 규칙 기반 가중치 구현 (즉시 적용 가능)

```python
# core/scoring/engine.py에 통합
from core.scoring.ai_weight_learner import RuleWeightLearner

scorer = TransactionScorer()
scorer.weight_learner = RuleWeightLearner(use_ai=False)  # 규칙 기반 사용
```

**장점**: 즉시 적용 가능, AI 모델 불필요

---

### 2단계: 학습 데이터 수집 (1-2주)

- 과거 거래 데이터 수집
- 라벨링 작업 (fraud/normal)
- 학습 데이터셋 구축

---

### 3단계: AI 모델 학습 (1주)

```python
# 학습 데이터 로드
training_data = load_training_data()

# 모델 학습
learner = RuleWeightLearner(use_ai=True)
learner.train(training_data)

# 모델 저장
learner.save_model("models/rule_weights.pkl")
```

---

### 4단계: 프로덕션 적용 (1주)

- 학습된 모델 로드
- 스코어링 엔진에 통합
- 성능 모니터링

---

## 💡 핵심 아이디어

### 룰 특성을 반영한 집계

현재는 단순 합산:

```python
score = sum(rule.score for rule in rules)  # 30 + 25 = 55점
```

개선: 룰 특성 반영

```python
# C-001 (HIGH, Compliance): 30 * 1.2 * 1.1 = 39.6
# E-101 (HIGH, Exposure): 25 * 1.2 * 1.1 = 33.0
# 조합 보너스: (39.6 + 33.0) * 1.2 = 87.12점
score = weighted_sum_with_combination_bonus(rules)
```

---

## 🎯 예상 효과

### Before (단순 합산)

- C-001 (30) + E-101 (25) = 55점 → "medium"

### After (가중치 적용)

- C-001 (30 _ 1.2 _ 1.1 = 39.6)
- E-101 (25 _ 1.2 _ 1.1 = 33.0)
- 조합 보너스: (39.6 + 33.0) \* 1.2 = 87.12점 → "critical"

**결과**: 더 정확한 리스크 평가 가능!

---

## 📚 참고

- `core/scoring/ai_weight_learner.py`: AI 가중치 학습 모듈
- `core/scoring/engine.py`: 스코어링 엔진
- `rules/tracex_rules.yaml`: 룰 정의
