# AI 작업 관리 가이드

데이터 수집 중에도 AI 관련 작업을 진행할 수 있도록 정리한 가이드입니다.

---

## 📊 현재 상태

### ✅ 구현 완료

1. **AI 기반 가중치 학습 모듈** (`core/scoring/ai_weight_learner.py`)

   - 규칙 기반 가중치 (즉시 사용 가능)
   - AI 모델 학습 기능 (데이터 필요)
   - 룰 특성 반영 (axis, severity, pattern type)

2. **데이터셋 구축 모듈** (`core/scoring/dataset_builder.py`)

   - Demo 데이터 활용
   - 레거시 데이터 활용
   - 규칙 기반 자동 라벨링

3. **실제 데이터 수집** (`core/scoring/real_dataset_builder.py`)
   - Etherscan API V2 연동
   - 자동 태그 정보 조회
   - 자동 라벨링

---

## 🎯 다음 단계 작업

### 1. 데이터 수집 완료 대기 (현재 진행 중)

**상태 확인**:

```bash
# 진행 상황 확인
cat logs/collection_progress.json

# 로그 확인
tail -f logs/collect.log
```

**예상 시간**: 10-30분 (주소 수에 따라)

---

### 2. 데이터셋 분할 (수집 완료 후)

**목적**: 학습/검증/테스트 데이터셋으로 분할

**구현 필요**:

```python
# scripts/split_dataset.py
from core.scoring.dataset_builder import DatasetBuilder
import json

builder = DatasetBuilder()

# 데이터셋 로드
with open("data/dataset/real_high_risk.json", 'r') as f:
    dataset = json.load(f)

# 분할
train, val, test = builder.split_dataset(
    dataset,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    stratify=True
)

# 저장
with open("data/dataset/train.json", 'w') as f:
    json.dump(train, f, indent=2)
with open("data/dataset/val.json", 'w') as f:
    json.dump(val, f, indent=2)
with open("data/dataset/test.json", 'w') as f:
    json.dump(test, f, indent=2)
```

---

### 3. AI 모델 학습 (데이터셋 준비 후)

**현재 상태**: 모듈은 구현되어 있으나 학습 데이터 필요

**학습 스크립트 작성 필요**:

```python
# scripts/train_ai_model.py
from core.scoring.ai_weight_learner import RuleWeightLearner
import json

# 학습 데이터 로드
with open("data/dataset/train.json", 'r') as f:
    train_data = json.load(f)

# 데이터 형식 변환
training_data = [
    (
        item["rule_results"],
        item["actual_risk_score"],
        item.get("tx_context", {})
    )
    for item in train_data
]

# 모델 학습
learner = RuleWeightLearner(use_ai=True)
learner.train(training_data)

# 모델 저장
learner.save_model("models/rule_weights.pkl")
```

---

### 4. 모델 평가 (학습 완료 후)

**평가 스크립트 작성 필요**:

```python
# scripts/evaluate_model.py
from core.scoring.ai_weight_learner import RuleWeightLearner
import json

# 모델 로드
learner = RuleWeightLearner(use_ai=True)
learner.load_model("models/rule_weights.pkl")

# 테스트 데이터 로드
with open("data/dataset/test.json", 'r') as f:
    test_data = json.load(f)

# 평가
# ... 평가 로직
```

---

## 🔧 지금 할 수 있는 작업

### 1. 데이터셋 분할 스크립트 작성

```bash
# 새 파일 생성
touch scripts/split_dataset.py
```

**구현 내용**:

- 데이터셋 로드
- 학습/검증/테스트 분할
- 통계 출력
- 저장

---

### 2. AI 모델 학습 스크립트 작성

```bash
# 새 파일 생성
touch scripts/train_ai_model.py
```

**구현 내용**:

- 학습 데이터 로드
- 데이터 형식 변환
- 모델 학습
- 모델 저장

---

### 3. 모델 평가 스크립트 작성

```bash
# 새 파일 생성
touch scripts/evaluate_model.py
```

**구현 내용**:

- 모델 로드
- 테스트 데이터 평가
- 메트릭 계산 (Accuracy, F1, Precision, Recall)
- 결과 출력

---

### 4. 문서 정리

- AI 가중치 학습 가이드 업데이트
- 데이터셋 구축 가이드 업데이트
- 전체 워크플로우 문서화

---

## 📋 작업 체크리스트

### 즉시 가능 (데이터 수집 대기 중)

- [ ] 데이터셋 분할 스크립트 작성
- [ ] AI 모델 학습 스크립트 작성
- [ ] 모델 평가 스크립트 작성
- [ ] 문서 정리 및 업데이트

### 데이터 수집 완료 후

- [ ] 데이터셋 분할 실행
- [ ] 데이터셋 통계 확인
- [ ] AI 모델 학습 실행
- [ ] 모델 평가 실행
- [ ] 결과 분석

---

## 🚀 빠른 시작

### 1. 데이터셋 분할 스크립트 작성

```python
# scripts/split_dataset.py
from core.scoring.dataset_builder import DatasetBuilder
import json
from pathlib import Path

def main():
    builder = DatasetBuilder()

    # 데이터셋 로드
    dataset_path = Path("data/dataset/real_high_risk.json")
    if not dataset_path.exists():
        print(f"데이터셋이 없습니다: {dataset_path}")
        return

    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    print(f"총 {len(dataset)}개 샘플")

    # 분할
    train, val, test = builder.split_dataset(
        dataset,
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        stratify=True
    )

    # 저장
    output_dir = Path("data/dataset")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "train.json", 'w') as f:
        json.dump(train, f, indent=2)
    with open(output_dir / "val.json", 'w') as f:
        json.dump(val, f, indent=2)
    with open(output_dir / "test.json", 'w') as f:
        json.dump(test, f, indent=2)

    print(f"\n✅ 분할 완료:")
    print(f"   학습: {len(train)}개")
    print(f"   검증: {len(val)}개")
    print(f"   테스트: {len(test)}개")

if __name__ == "__main__":
    main()
```

---

### 2. AI 모델 학습 스크립트 작성

```python
# scripts/train_ai_model.py
from core.scoring.ai_weight_learner import RuleWeightLearner
import json
from pathlib import Path

def main():
    # 학습 데이터 로드
    train_path = Path("data/dataset/train.json")
    if not train_path.exists():
        print(f"학습 데이터가 없습니다: {train_path}")
        return

    with open(train_path, 'r') as f:
        train_data = json.load(f)

    print(f"학습 데이터: {len(train_data)}개")

    # 데이터 형식 변환
    training_data = [
        (
            item["rule_results"],
            item["actual_risk_score"],
            item.get("tx_context", {})
        )
        for item in train_data
    ]

    # 모델 학습
    print("\n모델 학습 시작...")
    learner = RuleWeightLearner(use_ai=True)
    learner.train(training_data)

    # 모델 저장
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)

    # TODO: save_model 메서드 구현 필요
    # learner.save_model(model_dir / "rule_weights.pkl")

    print("✅ 학습 완료!")

if __name__ == "__main__":
    main()
```

---

## 💡 현재 할 수 있는 작업 우선순위

### 1순위: 스크립트 작성 (즉시 가능)

1. `scripts/split_dataset.py` - 데이터셋 분할
2. `scripts/train_ai_model.py` - 모델 학습
3. `scripts/evaluate_model.py` - 모델 평가

### 2순위: 문서 정리

1. 전체 워크플로우 문서화
2. AI 학습 가이드 업데이트
3. 사용 예시 추가

### 3순위: 기능 개선

1. 모델 저장/로드 기능 추가
2. 평가 메트릭 계산
3. 결과 시각화

---

## 🔗 관련 파일

- `core/scoring/ai_weight_learner.py`: AI 가중치 학습 모듈
- `core/scoring/dataset_builder.py`: 데이터셋 구축 모듈
- `core/scoring/real_dataset_builder.py`: 실제 데이터 수집
- `docs/AI_WEIGHT_LEARNING.md`: AI 학습 가이드
- `docs/DATASET_BUILDING_GUIDE.md`: 데이터셋 구축 가이드

---

## 📝 다음 작업 제안

데이터 수집이 완료되면:

1. **데이터셋 분할** → 학습/검증/테스트
2. **AI 모델 학습** → 실제 데이터로 가중치 학습
3. **모델 평가** → 성능 확인
4. **프로덕션 적용** → 학습된 모델 사용

지금은 스크립트를 미리 작성해두면 수집 완료 후 바로 진행할 수 있습니다!
