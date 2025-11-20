# 리스크 스코어링 최적화 가이드

## 📊 현재 구현된 스코어링 방식

### 1. 단일 트랜잭션 스코어링 (`TransactionScorer`)

```python
# 현재 방식: 단순 합산
def _calculate_risk_score(self, rule_results):
    total_score = sum(r.get("score", 0) for r in rule_results)
    return min(100.0, total_score)  # 0~100 범위로 제한
```

**특징**:

- 모든 룰 점수를 단순 합산
- 최대 100점으로 제한
- 룰 간 상관관계 고려 안 함

---

### 2. 주소 분석 스코어링 (`AddressAnalyzer`)

```python
# 현재 방식: 최대값과 가중 평균 중 더 높은 값
def _calculate_final_score(self, transaction_scores, transactions):
    max_score = max(transaction_scores)

    # 가중 평균 (최근 거래 70%, 과거 거래 30%)
    recent_weight = 0.7
    old_weight = 0.3
    weighted_avg = recent_avg * recent_weight + old_avg * old_weight

    return min(100.0, max(max_score, weighted_avg))
```

**특징**:

- 최대값과 가중 평균 중 더 높은 값 사용
- 최근 거래에 더 높은 가중치 (70%)
- 시간적 요소 고려

---

## 🎯 최적의 스코어링 방식을 찾는 방법

### 방법 1: 실험적 검증 (A/B 테스트)

#### 1단계: 다양한 스코어링 방식 구현

```python
# core/scoring/scoring_strategies.py
class ScoringStrategy:
    """스코어링 전략 인터페이스"""

    def calculate_score(self, rule_results: List[Dict]) -> float:
        raise NotImplementedError


class SumStrategy(ScoringStrategy):
    """단순 합산"""
    def calculate_score(self, rule_results):
        return min(100.0, sum(r.get("score", 0) for r in rule_results))


class WeightedSumStrategy(ScoringStrategy):
    """가중 합산 (severity 기반)"""
    SEVERITY_WEIGHTS = {
        "CRITICAL": 1.5,
        "HIGH": 1.2,
        "MEDIUM": 1.0,
        "LOW": 0.8
    }

    def calculate_score(self, rule_results):
        total = 0
        for r in rule_results:
            severity = r.get("severity", "MEDIUM")
            weight = self.SEVERITY_WEIGHTS.get(severity, 1.0)
            total += r.get("score", 0) * weight
        return min(100.0, total)


class MaxStrategy(ScoringStrategy):
    """최대값 사용"""
    def calculate_score(self, rule_results):
        if not rule_results:
            return 0.0
        return max(r.get("score", 0) for r in rule_results)


class DecayStrategy(ScoringStrategy):
    """감쇠 합산 (중복 룰 발동 시 감쇠)"""
    def calculate_score(self, rule_results):
        # 첫 번째 룰: 100%, 두 번째: 80%, 세 번째: 60%...
        total = 0
        for i, r in enumerate(rule_results):
            decay = 1.0 / (1.0 + i * 0.2)  # 20%씩 감쇠
            total += r.get("score", 0) * decay
        return min(100.0, total)


class CombinationStrategy(ScoringStrategy):
    """룰 조합 고려"""
    # 특정 룰 조합이 더 위험할 수 있음
    DANGEROUS_COMBINATIONS = {
        ("C-001", "E-101"): 1.5,  # 제재 + 믹서 = 매우 위험
        ("C-001", "B-201"): 1.3,  # 제재 + 레이어링 = 위험
        ("E-101", "B-202"): 1.4,  # 믹서 + 순환 = 위험
    }

    def calculate_score(self, rule_results):
        base_score = sum(r.get("score", 0) for r in rule_results)

        # 룰 조합 보너스
        rule_ids = tuple(sorted(r.get("rule_id") for r in rule_results))
        multiplier = self.DANGEROUS_COMBINATIONS.get(rule_ids, 1.0)

        return min(100.0, base_score * multiplier)
```

---

#### 2단계: 검증 데이터셋 구축

```python
# core/scoring/validation.py
@dataclass
class ValidationCase:
    """검증 케이스"""
    transaction: Dict[str, Any]
    expected_risk_level: str  # low, medium, high, critical
    expected_score_range: Tuple[float, float]  # (min, max)
    ground_truth_label: str  # "fraud", "normal", "suspicious"
    description: str


# 검증 데이터셋 예시
VALIDATION_DATASET = [
    ValidationCase(
        transaction={
            "is_sanctioned": True,
            "amount_usd": 1000,
            "is_mixer": False
        },
        expected_risk_level="high",
        expected_score_range=(30, 50),
        ground_truth_label="fraud",
        description="제재 주소와 거래"
    ),
    ValidationCase(
        transaction={
            "is_sanctioned": False,
            "is_mixer": True,
            "amount_usd": 50
        },
        expected_risk_level="high",
        expected_score_range=(25, 35),
        ground_truth_label="suspicious",
        description="믹서에서 유입"
    ),
    # ... 더 많은 케이스
]
```

---

#### 3단계: 성능 평가

```python
# core/scoring/evaluator.py
class ScoringEvaluator:
    """스코어링 방식 평가기"""

    def evaluate_strategy(
        self,
        strategy: ScoringStrategy,
        dataset: List[ValidationCase]
    ) -> Dict[str, float]:
        """스코어링 전략 평가"""

        results = {
            "accuracy": 0.0,  # 예측 정확도
            "precision": 0.0,  # 정밀도
            "recall": 0.0,  # 재현율
            "f1_score": 0.0,  # F1 점수
            "false_positive_rate": 0.0,  # 거짓 양성 비율
            "false_negative_rate": 0.0,  # 거짓 음성 비율
        }

        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0

        for case in dataset:
            # 스코어링 수행
            rule_results = self.rule_evaluator.evaluate(case.transaction)
            score = strategy.calculate_score(rule_results)
            risk_level = self._score_to_level(score)

            # 예측 vs 실제 비교
            predicted_high_risk = risk_level in ["high", "critical"]
            actual_high_risk = case.ground_truth_label in ["fraud", "suspicious"]

            if predicted_high_risk and actual_high_risk:
                true_positives += 1
            elif predicted_high_risk and not actual_high_risk:
                false_positives += 1
            elif not predicted_high_risk and not actual_high_risk:
                true_negatives += 1
            else:
                false_negatives += 1

        # 메트릭 계산
        total = len(dataset)
        results["accuracy"] = (true_positives + true_negatives) / total
        results["precision"] = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        results["recall"] = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        results["f1_score"] = 2 * (results["precision"] * results["recall"]) / (results["precision"] + results["recall"]) if (results["precision"] + results["recall"]) > 0 else 0

        return results
```

---

### 방법 2: 통계적 분석

#### 룰별 점수 분포 분석

```python
# core/scoring/analysis.py
class RuleScoreAnalyzer:
    """룰 점수 분석기"""

    def analyze_rule_distribution(self, historical_data):
        """룰별 점수 분포 분석"""
        rule_stats = {}

        for tx in historical_data:
            rule_results = self.evaluate(tx)
            for rule in rule_results:
                rule_id = rule["rule_id"]
                if rule_id not in rule_stats:
                    rule_stats[rule_id] = {
                        "count": 0,
                        "total_score": 0,
                        "scores": []
                    }
                rule_stats[rule_id]["count"] += 1
                rule_stats[rule_id]["total_score"] += rule["score"]
                rule_stats[rule_id]["scores"].append(rule["score"])

        # 통계 계산
        for rule_id, stats in rule_stats.items():
            stats["avg_score"] = stats["total_score"] / stats["count"]
            stats["max_score"] = max(stats["scores"])
            stats["min_score"] = min(stats["scores"])
            stats["std_score"] = np.std(stats["scores"])

        return rule_stats
```

---

#### 룰 간 상관관계 분석

```python
def analyze_rule_correlations(self, historical_data):
    """룰 간 상관관계 분석"""
    # 룰 발동 매트릭스 구축
    rule_matrix = []
    labels = []

    for tx in historical_data:
        rule_results = self.evaluate(tx)
        rule_vector = [1 if rule["rule_id"] in [r["rule_id"] for r in rule_results] else 0
                      for rule in ALL_RULES]
        rule_matrix.append(rule_vector)
        labels.append(tx["ground_truth_label"])

    # 상관관계 계산
    correlation_matrix = np.corrcoef(np.array(rule_matrix).T)

    # 위험한 룰 조합 찾기
    dangerous_combinations = []
    for i, rule1 in enumerate(ALL_RULES):
        for j, rule2 in enumerate(ALL_RULES[i+1:], i+1):
            correlation = correlation_matrix[i][j]
            if correlation > 0.3:  # 상관관계가 높으면
                # 실제 위험도 확인
                risk_when_both = self._calculate_risk_when_both_fire(rule1, rule2)
                dangerous_combinations.append({
                    "rule1": rule1,
                    "rule2": rule2,
                    "correlation": correlation,
                    "combined_risk": risk_when_both
                })

    return dangerous_combinations
```

---

### 방법 3: 도메인 전문가 검토

#### 룰별 중요도 평가

```yaml
# rules/rule_weights.yaml
rule_weights:
  # Compliance 룰 (높은 중요도)
  C-001: 1.2 # 제재 주소는 매우 중요
  C-003: 1.0
  C-004: 1.0

  # Exposure 룰 (높은 중요도)
  E-101: 1.3 # 믹서는 매우 중요
  E-102: 1.1

  # Behavior 룰 (중간 중요도)
  B-101: 0.9
  B-102: 1.0
  B-103: 0.8
  B-201: 1.2 # 레이어링은 중요
  B-202: 1.3 # 순환은 매우 중요
  B-203: 0.9
  B-204: 0.9
```

---

## 🔬 실험 설계

### 실험 1: 스코어링 방식 비교

```python
# experiments/compare_scoring_strategies.py
strategies = [
    SumStrategy(),
    WeightedSumStrategy(),
    MaxStrategy(),
    DecayStrategy(),
    CombinationStrategy()
]

results = {}
for strategy in strategies:
    evaluator = ScoringEvaluator()
    metrics = evaluator.evaluate_strategy(strategy, VALIDATION_DATASET)
    results[strategy.__class__.__name__] = metrics

# 결과 비교
print("스코어링 방식 비교:")
for name, metrics in results.items():
    print(f"{name}:")
    print(f"  Accuracy: {metrics['accuracy']:.2%}")
    print(f"  F1 Score: {metrics['f1_score']:.2%}")
    print(f"  False Positive Rate: {metrics['false_positive_rate']:.2%}")
```

---

### 실험 2: 임계값 최적화

```python
# experiments/optimize_thresholds.py
def optimize_thresholds(validation_data):
    """리스크 레벨 임계값 최적화"""

    best_thresholds = None
    best_f1 = 0.0

    # 그리드 서치
    for critical_threshold in range(70, 95, 5):
        for high_threshold in range(50, 75, 5):
            for medium_threshold in range(20, 45, 5):
                thresholds = {
                    "critical": critical_threshold,
                    "high": high_threshold,
                    "medium": medium_threshold
                }

                f1 = evaluate_thresholds(thresholds, validation_data)

                if f1 > best_f1:
                    best_f1 = f1
                    best_thresholds = thresholds

    return best_thresholds
```

---

## 💡 권장 최적화 전략

### 단계별 접근

#### 1단계: 현재 방식 개선 (즉시 적용 가능)

```python
# 개선된 스코어링 방식
def _calculate_risk_score_improved(self, rule_results):
    """개선된 스코어링 방식"""

    if not rule_results:
        return 0.0

    # 1. Severity 기반 가중치 적용
    severity_weights = {
        "HIGH": 1.2,
        "MEDIUM": 1.0,
        "LOW": 0.8
    }

    weighted_scores = []
    for r in rule_results:
        severity = r.get("severity", "MEDIUM")
        weight = severity_weights.get(severity, 1.0)
        weighted_scores.append(r.get("score", 0) * weight)

    # 2. 룰 조합 보너스
    rule_ids = [r.get("rule_id") for r in rule_results]
    combination_bonus = self._calculate_combination_bonus(rule_ids)

    # 3. 최종 점수 계산
    base_score = sum(weighted_scores)
    final_score = base_score * (1.0 + combination_bonus)

    return min(100.0, final_score)


def _calculate_combination_bonus(self, rule_ids):
    """룰 조합 보너스 계산"""
    # 위험한 조합
    dangerous_pairs = [
        ("C-001", "E-101"),  # 제재 + 믹서
        ("C-001", "B-201"),  # 제재 + 레이어링
        ("E-101", "B-202"),  # 믹서 + 순환
    ]

    bonus = 0.0
    for rule1, rule2 in dangerous_pairs:
        if rule1 in rule_ids and rule2 in rule_ids:
            bonus += 0.15  # 15% 보너스

    return min(0.3, bonus)  # 최대 30% 보너스
```

---

#### 2단계: 데이터 기반 최적화 (중기)

1. **검증 데이터셋 구축**

   - 과거 거래 데이터 수집
   - 실제 사기/정상 라벨링
   - 룰 발동 이력 기록

2. **성능 평가**

   - 각 스코어링 방식 테스트
   - 메트릭 비교 (Accuracy, F1, Precision, Recall)
   - False Positive/Negative Rate 분석

3. **최적 방식 선택**
   - 검증 데이터에서 가장 좋은 성능을 보이는 방식 선택
   - 도메인 전문가 검토

---

#### 3단계: AI 기반 최적화 (장기)

1. **룰 가중치 학습**

   - 지도 학습으로 룰별 가중치 학습
   - Logistic Regression 또는 Gradient Boosting

2. **룰 조합 최적화**

   - 앙상블 학습
   - 룰 간 상호작용 모델링

3. **동적 임계값 조정**
   - 컨텍스트 기반 임계값 조정
   - 주소별, 거래 패턴별 최적 임계값

---

## 📊 평가 메트릭

### 필수 메트릭

1. **Accuracy**: 전체 예측 정확도
2. **Precision**: 위험으로 예측한 것 중 실제 위험 비율
3. **Recall**: 실제 위험 중 탐지한 비율
4. **F1 Score**: Precision과 Recall의 조화 평균

### 추가 메트릭

1. **False Positive Rate**: 정상을 위험으로 잘못 분류한 비율
2. **False Negative Rate**: 위험을 정상으로 잘못 분류한 비율
3. **ROC-AUC**: ROC 곡선 아래 면적
4. **Score Distribution**: 점수 분포 분석

---

## 🎯 즉시 적용 가능한 개선안

### 1. Severity 기반 가중치 적용

```python
# core/scoring/engine.py 수정
def _calculate_risk_score(self, rule_results):
    severity_weights = {"HIGH": 1.2, "MEDIUM": 1.0, "LOW": 0.8}

    total = 0
    for r in rule_results:
        severity = r.get("severity", "MEDIUM")
        weight = severity_weights.get(severity, 1.0)
        total += r.get("score", 0) * weight

    return min(100.0, total)
```

### 2. 룰 조합 보너스 추가

```python
def _calculate_risk_score(self, rule_results):
    base_score = sum(r.get("score", 0) for r in rule_results)

    # 위험한 룰 조합 보너스
    rule_ids = [r.get("rule_id") for r in rule_results]
    if "C-001" in rule_ids and "E-101" in rule_ids:
        base_score *= 1.2  # 제재 + 믹서 = 20% 보너스

    return min(100.0, base_score)
```

### 3. 임계값 조정

```python
def _determine_risk_level(self, score):
    # 현재: 80, 60, 30
    # 개선: 75, 55, 25 (더 민감하게)
    if score >= 75:
        return "critical"
    elif score >= 55:
        return "high"
    elif score >= 25:
        return "medium"
    else:
        return "low"
```

---

## 📝 다음 단계

1. **검증 데이터셋 구축** (1-2주)

   - 과거 거래 데이터 수집
   - 라벨링 작업

2. **다양한 스코어링 방식 구현** (1주)

   - 위의 전략들 구현

3. **성능 평가** (1주)

   - 각 방식 테스트
   - 메트릭 비교

4. **최적 방식 선택 및 적용** (1주)
   - 최고 성능 방식 선택
   - 프로덕션 적용

---

## 🔗 참고

- `core/scoring/engine.py`: 현재 스코어링 구현
- `core/scoring/address_analyzer.py`: 주소 분석 스코어링
- `rules/tracex_rules.yaml`: 룰 정의 및 점수
