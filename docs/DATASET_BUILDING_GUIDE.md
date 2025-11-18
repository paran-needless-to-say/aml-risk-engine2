# 학습/검증/테스트 데이터셋 구축 가이드

## 📊 현재 데이터 현황

### 레거시 데이터

1. **거래 데이터**: `legacy/data/transactions/{chain}/{address}.csv`

   - 거래 내역은 있음
   - 라벨링은 없음

2. **Features 데이터**: `legacy/data/features/{chain}_basic_metrics_processed.csv`

   - 그래프 메트릭 포함
   - **라벨 컬럼 있음** (`label`: 0=normal, 1=fraud)
   - 하지만 거래 레벨 라벨은 아님

3. **Demo 데이터**: `demo/transactions/*.json`
   - 시나리오별로 분류됨
   - `high_risk`, `medium_risk`, `low_risk`로 구분
   - 라벨링 가능

---

## 🎯 데이터셋 구축 방법 4가지

### 방법 0: Etherscan API로 실제 데이터 수집 (가장 정확) ⭐ **추천**

**장점**:

- 실제 블록체인 데이터
- 대량 데이터 수집 가능
- 즉시 사용 가능
- 정확한 라벨링 가능 (OFAC, 믹서 리스트 활용)

**구현**:

```python
from core.scoring.real_dataset_builder import RealDatasetBuilder
import os

# API 키 설정
api_key = os.getenv("ETHERSCAN_API_KEY")

# 데이터셋 구축기 생성
builder = RealDatasetBuilder(api_key=api_key, chain="ethereum")

# 고위험 주소 리스트 (OFAC, 믹서)
from core.data.lists import ListLoader
list_loader = ListLoader()
high_risk_addresses = list(list_loader.get_sdn_list())[:20] + \
                      list(list_loader.get_mixer_list())[:20]

# 데이터셋 구축
dataset = builder.build_from_high_risk_addresses(
    addresses=high_risk_addresses,
    max_transactions_per_address=50,
    output_path="data/dataset/real_etherscan.json"
)
```

**사용법**:

```bash
# 1. API 키 발급: https://etherscan.io/apis
# 2. 환경변수 설정
export ETHERSCAN_API_KEY="your_api_key_here"

# 3. 스크립트 실행
python scripts/collect_real_data.py
```

**라벨링**:

- OFAC 제재 주소 거래 → fraud (85점)
- 믹서 주소 거래 → fraud (85점)
- 정상 주소 거래 → normal (15점)

---

### 방법 1: Demo 시나리오 활용 (가장 쉬움) ✅

**장점**:

- 이미 시나리오별로 분류되어 있음
- 즉시 사용 가능
- 다양한 리스크 레벨 포함

**구현**:

```python
from core.scoring.dataset_builder import DatasetBuilder

builder = DatasetBuilder()
dataset = builder.build_from_demo_scenarios(
    demo_dir="demo/transactions",
    output_path="data/dataset/demo_labeled.json"
)
```

**시나리오 매핑**:

- `high_risk_*` → fraud (85점)
- `medium_risk_*` → suspicious (60점)
- `low_risk_*` → normal (15점)

---

### 방법 2: 레거시 Features 데이터 활용

**장점**:

- 대량 데이터 가능
- 실제 블록체인 데이터

**단점**:

- 주소 레벨 라벨만 있음 (거래 레벨 아님)
- USD 변환 필요

**구현**:

```python
builder = DatasetBuilder()
dataset = builder.build_from_legacy_features(
    features_path="legacy/data/features/ethereum_basic_metrics_processed.csv",
    transactions_dir="legacy/data/transactions",
    output_path="data/dataset/legacy_labeled.json"
)
```

**라벨 매핑**:

- `label=1` → fraud (85점)
- `label=0` → normal (15점)

---

### 방법 3: 규칙 기반 자동 라벨링 (초기 데이터셋)

**장점**:

- 대량 데이터 자동 생성 가능
- 즉시 사용 가능

**단점**:

- 현재 룰의 한계를 그대로 반영
- 실제 라벨과 차이 있을 수 있음

**구현**:

```python
# 거래 리스트 준비
transactions = [...]  # 백엔드에서 받은 거래 리스트

builder = DatasetBuilder()
dataset = builder.build_from_rule_based_labeling(
    transactions,
    output_path="data/dataset/rule_based_labeled.json"
)
```

**라벨 결정**:

- 규칙 기반 점수 >= 60 → fraud
- 규칙 기반 점수 >= 30 → suspicious
- 규칙 기반 점수 < 30 → normal

---

## 📋 데이터셋 구조

### 학습 데이터 형식

```json
{
  "rule_results": [
    {
      "rule_id": "C-001",
      "score": 30,
      "axis": "C",
      "severity": "HIGH",
      "name": "Sanction Direct Touch"
    },
    {
      "rule_id": "E-101",
      "score": 25,
      "axis": "E",
      "severity": "HIGH",
      "name": "Mixer Direct Exposure"
    }
  ],
  "actual_risk_score": 85.0,
  "tx_context": {
    "amount_usd": 5000.0,
    "is_sanctioned": true,
    "is_mixer": true,
    "chain": "ethereum"
  },
  "ground_truth_label": "fraud",
  "tx_hash": "0x...",
  "chain": "ethereum"
}
```

---

## 🔄 데이터셋 분할

### 학습/검증/테스트 분할

```python
from core.scoring.dataset_builder import DatasetBuilder

builder = DatasetBuilder()
dataset = builder.build_from_demo_scenarios(...)

# 분할 (라벨별 비율 유지)
train, val, test = builder.split_dataset(
    dataset,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    stratify=True  # 라벨별 비율 유지
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

## 👨‍💼 전문가 라벨링 (선택적)

### 라벨링 템플릿 생성

```python
from core.scoring.dataset_builder import ExpertLabelingTool

tool = ExpertLabelingTool("data/dataset/rule_based_labeled.json")
tool.create_labeling_template("data/dataset/labeling_template.json")
```

### 라벨링 템플릿 형식

```json
[
  {
    "id": 0,
    "tx_hash": "0x...",
    "rule_results": [...],
    "rule_based_score": 55.0,
    "expert_label": null,  // 전문가가 채움: "fraud" | "suspicious" | "normal"
    "expert_score": null,  // 전문가가 채움: 0~100
    "notes": ""  // 메모
  },
  ...
]
```

### 라벨링된 데이터 로드

```python
labeled_data = tool.load_labeled_data("data/dataset/labeling_template.json")
```

---

## 🚀 실제 구축 단계

### 1단계: Demo 데이터로 초기 데이터셋 구축 (즉시)

```python
# scripts/build_initial_dataset.py
from core.scoring.dataset_builder import DatasetBuilder

builder = DatasetBuilder()

# Demo 시나리오에서 구축
dataset = builder.build_from_demo_scenarios(
    demo_dir="demo/transactions",
    output_path="data/dataset/initial.json"
)

# 분할
train, val, test = builder.split_dataset(dataset)

print(f"학습: {len(train)}개")
print(f"검증: {len(val)}개")
print(f"테스트: {len(test)}개")
```

**예상 결과**: 약 100~200개 샘플 (Demo 데이터 기준)

---

### 2단계: 레거시 데이터 확장 (1-2주)

```python
# 레거시 features 활용
legacy_dataset = builder.build_from_legacy_features(
    features_path="legacy/data/features/ethereum_basic_metrics_processed.csv",
    transactions_dir="legacy/data/transactions",
    output_path="data/dataset/legacy.json"
)

# Demo와 병합
combined_dataset = demo_dataset + legacy_dataset

# 분할
train, val, test = builder.split_dataset(combined_dataset)
```

**예상 결과**: 수천~수만 개 샘플

---

### 3단계: 규칙 기반 자동 라벨링 (지속적)

```python
# 백엔드에서 받은 거래 데이터로 자동 라벨링
new_transactions = [...]  # 백엔드 API에서 받은 거래

rule_based_dataset = builder.build_from_rule_based_labeling(
    new_transactions,
    output_path="data/dataset/rule_based_new.json"
)

# 기존 데이터셋에 추가
existing_dataset.extend(rule_based_dataset)
```

**장점**: 지속적으로 데이터셋 확장 가능

---

### 4단계: 전문가 라벨링 (선택적, 장기)

```python
# 고위험 샘플만 전문가 라벨링
high_risk_samples = [
    d for d in dataset
    if sum(r.get("score", 0) for r in d["rule_results"]) >= 50
]

tool = ExpertLabelingTool("data/dataset/high_risk.json")
tool.create_labeling_template("data/dataset/expert_labeling.json")

# 전문가가 라벨링 후
labeled_data = tool.load_labeled_data("data/dataset/expert_labeling.json")
```

---

## 📊 데이터셋 통계

### 라벨 분포 확인

```python
def analyze_dataset(dataset):
    """데이터셋 통계 분석"""
    labels = [d.get("ground_truth_label") for d in dataset]
    label_counts = {}
    for label in labels:
        label_counts[label] = label_counts.get(label, 0) + 1

    print("라벨 분포:")
    for label, count in label_counts.items():
        print(f"  {label}: {count}개 ({count/len(dataset)*100:.1f}%)")

    # 점수 분포
    scores = [d.get("actual_risk_score", 0) for d in dataset]
    print(f"\n점수 통계:")
    print(f"  평균: {sum(scores)/len(scores):.1f}")
    print(f"  최소: {min(scores):.1f}")
    print(f"  최대: {max(scores):.1f}")

analyze_dataset(train)
```

---

## 🎯 권장 접근법

### 즉시 시작 (1일)

1. **Demo 데이터로 초기 데이터셋 구축**

   ```bash
   python scripts/build_initial_dataset.py
   ```

2. **규칙 기반 가중치로 모델 학습**

   ```python
   from core.scoring.ai_weight_learner import RuleWeightLearner

   learner = RuleWeightLearner(use_ai=False)  # 규칙 기반으로 시작
   # 이미 작동 중!
   ```

---

### 단기 (1-2주)

1. **레거시 데이터 확장**

   - Features 데이터 활용
   - 거래 데이터와 매칭

2. **데이터셋 품질 개선**
   - 이상치 제거
   - 라벨 분포 균형 조정

---

### 중기 (1개월)

1. **전문가 라벨링**

   - 고위험 샘플 우선 라벨링
   - 점진적 확장

2. **AI 모델 학습**
   ```python
   learner = RuleWeightLearner(use_ai=True)
   learner.train(training_data)
   ```

---

## 💡 라벨이 없을 때 대안

### 1. 규칙 기반 자동 라벨링

현재 룰로 스코어링한 결과를 라벨로 사용:

- 점수 >= 60 → fraud
- 점수 >= 30 → suspicious
- 점수 < 30 → normal

**장점**: 즉시 사용 가능, 대량 생성 가능

**단점**: 현재 룰의 한계 반영

---

### 2. 외부 데이터 소스 활용

- **OFAC SDN 리스트**: 제재 주소 = fraud
- **믹서 리스트**: 믹서 거래 = suspicious
- **CEX 주소**: CEX 거래 = normal (일반적으로)

---

### 3. 반지도 학습 (Semi-supervised Learning)

- 소량의 라벨링된 데이터로 시작
- 대량의 라벨링되지 않은 데이터 활용
- 점진적 라벨링

---

## 📝 실제 사용 예시

### 전체 파이프라인

```python
# scripts/build_training_dataset.py
from core.scoring.dataset_builder import DatasetBuilder

builder = DatasetBuilder()

# 1. Demo 데이터
demo_dataset = builder.build_from_demo_scenarios(
    demo_dir="demo/transactions",
    output_path="data/dataset/demo.json"
)

# 2. 레거시 데이터 (선택적)
# legacy_dataset = builder.build_from_legacy_features(...)

# 3. 규칙 기반 자동 라벨링 (선택적)
# rule_based = builder.build_from_rule_based_labeling(...)

# 4. 병합
all_dataset = demo_dataset  # + legacy_dataset + rule_based

# 5. 분할
train, val, test = builder.split_dataset(
    all_dataset,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    stratify=True
)

# 6. 저장
import json
with open("data/dataset/train.json", 'w') as f:
    json.dump(train, f, indent=2)
with open("data/dataset/val.json", 'w') as f:
    json.dump(val, f, indent=2)
with open("data/dataset/test.json", 'w') as f:
    json.dump(test, f, indent=2)

print(f"데이터셋 구축 완료!")
print(f"  학습: {len(train)}개")
print(f"  검증: {len(val)}개")
print(f"  테스트: {len(test)}개")
```

---

## 🔗 참고

- `core/scoring/dataset_builder.py`: 데이터셋 구축 모듈
- `core/scoring/ai_weight_learner.py`: AI 가중치 학습 모듈
- `demo/transactions/`: Demo 시나리오 데이터
- `legacy/data/features/`: 레거시 features 데이터
