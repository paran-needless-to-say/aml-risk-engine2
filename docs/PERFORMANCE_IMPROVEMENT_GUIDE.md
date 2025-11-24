# 성능 개선 가이드

현재 성능: Accuracy 78.86%, ROC-AUC 0.8777

목표: Accuracy 85% 이상, ROC-AUC 0.90 이상

---

## 1. 즉시 시도 가능한 개선 방법

### 1.1 고급 Feature Engineering 적용

**목적**: 30차원 → 50+ 차원으로 확장

**파일**: `scripts/maximize_performance.py` (이미 구현됨)

**주요 추가 Features**:

- 상호작용 Features (rule_score × graph_score 등)
- Fan-in/out 비율 및 비대칭성
- 거래 금액 통계 (최대/최소 비율, 변동성)
- 그래프 밀도 및 평균 연결도
- Rule 다양성 및 심각도 가중 평균
- PPR 상호작용 Features

**실행 방법**:

```bash
cd risk-scoring
python scripts/maximize_performance.py
```

**예상 개선**: +2~3% Accuracy 향상

---

### 1.2 XGBoost / LightGBM 최적화

**현재**: Gradient Boosting (sklearn) 사용
**개선**: XGBoost 또는 LightGBM 사용

**장점**:

- 더 효율적인 알고리즘
- 더 나은 하이퍼파라미터 튜닝
- 더 빠른 학습 속도

**실행 방법**:

```bash
# XGBoost 설치 필요
pip install xgboost lightgbm

# 스크립트 실행 (이미 XGBoost/LightGBM 최적화 포함됨)
python scripts/maximize_performance.py
```

**예상 개선**: +1~2% Accuracy 향상

---

### 1.3 앙상블 모델 적용

**현재**: 단일 Gradient Boosting 모델
**개선**: Voting Classifier (XGBoost + Random Forest + Gradient Boosting)

**파일**: `scripts/maximize_performance.py`의 `create_advanced_ensemble()` 함수

**실행 방법**:

```bash
python scripts/maximize_performance.py
# 스크립트가 자동으로 앙상블 모델 생성 및 비교
```

**예상 개선**: +1~2% Accuracy 향상

---

### 1.4 Threshold 최적화

**현재**: 기본 0.5 threshold
**개선**: F1-Score 최대화하는 최적 threshold 찾기

**파일**: `scripts/maximize_performance.py`의 `optimize_threshold()` 함수

**실행 방법**:

```bash
python scripts/maximize_performance.py
# 스크립트가 자동으로 최적 threshold 계산
```

**예상 개선**: Precision/Recall 균형 개선 (F1-Score +2~5% 향상)

---

### 1.5 하이퍼파라미터 더 깊은 튜닝

**현재**: GridSearchCV (제한적 그리드)
**개선**: RandomizedSearchCV (더 넓은 탐색 공간)

**파일**: `scripts/maximize_performance.py` (이미 구현됨)

**주요 파라미터**:

- `n_estimators`: 200-500
- `max_depth`: 5-10
- `learning_rate`: 0.01-0.2
- `subsample`: 0.7-1.0
- `colsample_bytree`: 0.7-1.0 (XGBoost)

**예상 개선**: +1~2% Accuracy 향상

---

## 2. 중기 개선 방법 (더 많은 작업 필요)

### 2.1 더 많은 데이터 사용

**현재**: 5,000개 샘플 (train/val/test)
**개선**: 전체 92,138개 데이터 사용

**주의사항**:

- 학습 시간 대폭 증가 (수 시간 ~ 수십 시간)
- 메모리 사용량 증가

**실행 방법**:

```bash
# maximize_performance.py 파일 수정
# dataset_path = sampled_dataset_path  # 이 줄 주석 처리
dataset_path = full_dataset_path  # 이 줄 주석 해제
```

**예상 개선**: +3~5% Accuracy 향상

---

### 2.2 클래스 불균형 처리 개선

**현재**: class_weight='balanced' 사용
**개선**: SMOTE, ADASYN, 또는 다른 오버샘플링 기법

**구현 필요**:

```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
```

**예상 개선**: Recall 향상 (+5~10% 개선)

---

### 2.3 Stage 1 최적화

**현재**: rule_weight=0.9, graph_weight=0.1 (고정)
**개선**: Stage 1 가중치 최적화

**실행 방법**:

```bash
python scripts/optimize_stage1_scorer.py
```

**예상 개선**: Stage 1 점수 품질 향상 → Stage 2 성능 +1~2% 향상

---

### 2.4 Deep Learning 모델 시도

**현재**: Tree-based 모델 (Gradient Boosting, XGBoost)
**개선**: MLP (Multi-Layer Perceptron) 또는 TabNet

**파일**: `scripts/maximize_performance.py` (MLPClassifier 포함됨)

**실행 방법**:

```bash
python scripts/maximize_performance.py
# 스크립트가 자동으로 MLP 모델 학습 및 비교
```

**예상 개선**: +1~3% Accuracy 향상 (데이터 크기에 따라 다름)

---

## 3. 고급 개선 방법 (연구적 접근)

### 3.1 Feature Selection

**목적**: 불필요한 feature 제거, 중요한 feature만 사용

**방법**:

- Feature importance 기반 선택
- Recursive Feature Elimination (RFE)
- 상관관계 분석

**예상 개선**: 과적합 방지, 일반화 성능 향상

---

### 3.2 Stacking 앙상블

**현재**: Voting Classifier
**개선**: Stacking Classifier (Meta-learner 사용)

**구현 필요**:

```python
from sklearn.ensemble import StackingClassifier

stacking_clf = StackingClassifier(
    estimators=[('xgb', xgb_model), ('rf', rf_model), ('gb', gb_model)],
    final_estimator=LogisticRegression(),
    cv=5
)
```

**예상 개선**: +1~2% Accuracy 향상

---

### 3.3 Cross-Validation 기반 모델 선택

**현재**: Train/Val/Test 분할
**개선**: K-Fold Cross-Validation으로 더 안정적인 평가

**예상 개선**: 더 안정적인 성능, 과적합 방지

---

## 4. 추천 실행 순서

### 빠른 개선 (1-2시간 내):

1. **XGBoost 최적화** 실행

   ```bash
   python scripts/maximize_performance.py
   ```

2. **Threshold 최적화** 적용

3. **앙상블 모델** 생성 및 평가

**예상 결과**: Accuracy 81-83%, ROC-AUC 0.88-0.89

---

### 중기 개선 (하루 내):

1. **고급 Feature Engineering** 적용

2. **더 깊은 하이퍼파라미터 튜닝** (RandomizedSearchCV, 100+ iterations)

3. **SMOTE 오버샘플링** 적용

**예상 결과**: Accuracy 83-85%, ROC-AUC 0.89-0.91

---

### 장기 개선 (수일):

1. **전체 데이터셋 사용** (92,138개)

2. **Stacking 앙상블** 구현

3. **Deep Learning 모델** 실험

**예상 결과**: Accuracy 85% 이상, ROC-AUC 0.90 이상

---

## 5. 성능 모니터링

개선 작업 후 다음 지표를 확인:

- **Accuracy**: 목표 85% 이상
- **ROC-AUC**: 목표 0.90 이상
- **Precision**: 현재 0.9021 유지 (False Positive 최소화)
- **F1-Score**: Accuracy와 Precision 균형 고려

---

## 6. 주의사항

1. **과적합 주의**: Validation 성능만 올라가고 Test 성능이 떨어지지 않도록 주의

2. **해석 가능성 유지**: 규제 환경에서 요구되는 해석 가능성 보존

3. **실행 시간**: 전체 데이터셋 사용 시 학습 시간이 매우 길어질 수 있음

4. **리소스**: 메모리 부족 시 배치 처리 고려

---

## 7. 빠른 시작

가장 빠르게 성능을 개선하려면:

```bash
cd risk-scoring

# 1. XGBoost 설치
pip install xgboost lightgbm

# 2. 성능 최대화 스크립트 실행
python scripts/maximize_performance.py
```

스크립트가 자동으로:

- 고급 Feature Engineering 적용
- XGBoost/LightGBM 최적화
- 앙상블 모델 생성
- Threshold 최적화
- 최종 성능 평가

결과는 `models/` 디렉토리에 저장됩니다.
