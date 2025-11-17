# AI 통합 계획

## 📋 개요

현재는 **룰 베이스드** 방식만 사용하지만, **AI를 활용하여 성능을 향상**시킬 수 있습니다.

## 🎯 AI 활용 방안

### 1. 룰 점수 가중치 학습 (Rule Weight Learning)

**문제**: 모든 룰이 동일한 가중치로 합산됨

```python
# 현재: 단순 합산
risk_score = sum(rule.score for rule in fired_rules)
```

**해결**: AI가 룰별 가중치를 학습

```python
# AI 기반 가중치 적용
risk_score = sum(
    rule.score * ai_model.get_weight(rule.rule_id, context)
    for rule in fired_rules
)
```

**학습 데이터**:

- 과거 거래 데이터
- 실제 사기/정상 라벨
- 룰 발동 이력

**모델**:

- Logistic Regression (해석 가능)
- Gradient Boosting (성능 우수)
- Neural Network (복잡한 패턴)

### 2. 룰 조합 최적화 (Rule Combination)

**문제**: 룰 조합의 효과를 수동으로 결정

```python
# 현재: 모든 룰 점수 합산
if rule1_fired and rule2_fired:
    score = rule1.score + rule2.score  # 단순 합산
```

**해결**: AI가 룰 조합의 상호작용 학습

```python
# AI 기반 조합 점수
if rule1_fired and rule2_fired:
    # 룰 조합이 더 위험할 수 있음
    score = ai_model.get_combination_score(rule1, rule2, context)
```

**예시**:

- "Mixer 유입 + 제재 주소" = 매우 위험 (단순 합산보다 높음)
- "CEX 유입 + 고액 거래" = 정상 (단순 합산보다 낮음)

### 3. 이상 패턴 탐지 보완 (Anomaly Detection)

**문제**: 룰로 잡지 못하는 새로운 패턴

```python
# 현재: 룰만으로 평가
if not any_rule_fired:
    risk_score = 0  # 정상으로 판단
```

**해결**: AI가 룰 밖의 이상 패턴 탐지

```python
# 룰 점수 + AI 이상 탐지 점수
rule_score = calculate_rule_score(...)
anomaly_score = ai_model.detect_anomaly(transaction_features)
final_score = combine(rule_score, anomaly_score)
```

**특징 추출**:

- 거래 시간 패턴
- 금액 분포
- 주소 연결성
- 거래 빈도

### 4. 점수 보정/보정 (Score Calibration)

**문제**: 룰 점수가 실제 위험도와 불일치

```python
# 현재: 고정된 점수
if is_mixer:
    score += 50  # 항상 50점
```

**해결**: AI가 컨텍스트에 따라 점수 보정

```python
# 컨텍스트 기반 점수 보정
base_score = 50
context = {
    "amount": tx.amount_usd,
    "time_of_day": tx.timestamp.hour,
    "chain": tx.chain,
}
adjusted_score = ai_model.adjust_score(base_score, context)
```

**예시**:

- Mixer + 소액 (< $100) = 점수 감소
- Mixer + 대액 (> $10,000) = 점수 증가
- Mixer + 심야 시간 = 점수 증가

### 5. 시간적 패턴 학습 (Temporal Pattern Learning)

**문제**: 시간 기반 룰이 고정된 윈도우만 사용

```python
# 현재: 고정 윈도우 (24h)
window = 86400  # 24시간
```

**해결**: AI가 최적 윈도우 크기 학습

```python
# 동적 윈도우 크기
optimal_window = ai_model.predict_window_size(
    address_history,
    transaction_pattern
)
```

## 🏗️ 구현 단계

### Phase 1: 데이터 수집 (1-2주)

- 과거 거래 데이터 수집
- 라벨링 (사기/정상)
- 룰 발동 이력 기록

### Phase 2: 베이스라인 모델 (2-3주)

- Logistic Regression으로 룰 가중치 학습
- 성능 평가 (AUC, Precision, Recall)

### Phase 3: 고급 모델 (3-4주)

- Gradient Boosting / Neural Network
- 룰 조합 최적화
- 이상 탐지 모델

### Phase 4: 통합 및 배포 (2-3주)

- API 통합
- A/B 테스트
- 모니터링

## 📊 예상 효과

| 방법           | 예상 성능 향상 | 구현 난이도       |
| -------------- | -------------- | ----------------- |
| 룰 가중치 학습 | +10-15% AUC    | ⭐⭐ (쉬움)       |
| 룰 조합 최적화 | +5-10% AUC     | ⭐⭐⭐ (보통)     |
| 이상 탐지 보완 | +15-20% AUC    | ⭐⭐⭐⭐ (어려움) |
| 점수 보정      | +5-10% AUC     | ⭐⭐⭐ (보통)     |

## 🔄 하이브리드 접근법

**최종 구조**:

```
트랜잭션 입력
    ↓
[룰 베이스드 평가] → 룰 점수
    ↓
[AI 모델 평가] → AI 점수
    ↓
[가중치 결합] → 최종 점수
    ↓
Risk Level 결정
```

**장점**:

- 해석 가능성 (룰 베이스드)
- 높은 성능 (AI)
- 안정성 (룰 + AI 이중 검증)

## 💡 추천 시작점

1. **룰 가중치 학습**부터 시작 (가장 쉬움, 효과 큼)
2. 데이터가 충분하면 **룰 조합 최적화** 추가
3. 최종적으로 **이상 탐지 보완**으로 완성
