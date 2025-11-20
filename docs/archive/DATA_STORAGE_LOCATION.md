# 데이터 저장 위치 가이드

## 📂 데이터 저장 위치

### 기본 저장 디렉토리

```
data/dataset/
```

---

## 📁 저장되는 파일들

### 1. 수집된 원본 데이터셋

#### 방법 1: 고위험 주소만

```
data/dataset/real_high_risk.json
```

- 제재 주소 + 믹서 주소의 거래 데이터
- 대부분 "fraud" 라벨

#### 방법 2: 고위험 + 정상 주소

```
data/dataset/real_balanced.json
```

- 고위험 주소 + 정상 주소(CEX)의 거래 데이터
- Fraud와 Normal 균형

---

### 2. 분할된 데이터셋 (수집 완료 후)

```
data/dataset/train.json    # 학습 데이터 (70%)
data/dataset/val.json      # 검증 데이터 (15%)
data/dataset/test.json     # 테스트 데이터 (15%)
```

---

### 3. 학습된 모델 (AI 학습 후)

```
models/rule_weights.pkl              # AI 학습 모델
models/rule_weights_rule_based.pkl   # 규칙 기반 가중치
```

---

## 🔍 현재 저장된 데이터 확인

### 파일 목록 확인

```bash
# 데이터셋 디렉토리 확인
ls -lh data/dataset/

# 파일 크기 확인
du -h data/dataset/*.json
```

### 데이터 내용 확인

```bash
# JSON 파일 내용 확인
cat data/dataset/real_balanced.json | jq '.[0]'  # 첫 번째 샘플
cat data/dataset/real_balanced.json | jq 'length'  # 샘플 수
```

### Python으로 확인

```python
import json
from pathlib import Path

# 데이터셋 로드
dataset_path = Path("data/dataset/real_balanced.json")
if dataset_path.exists():
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    print(f"총 샘플: {len(dataset)}개")

    if dataset:
        print(f"\n첫 번째 샘플:")
        print(json.dumps(dataset[0], indent=2, ensure_ascii=False))
else:
    print("데이터셋 파일이 없습니다.")
```

---

## 📊 데이터 구조

### 저장되는 데이터 형식

```json
[
  {
    "rule_results": [
      {
        "rule_id": "C-001",
        "score": 30,
        "axis": "C",
        "severity": "HIGH",
        "name": "Sanction Direct Touch"
      }
    ],
    "actual_risk_score": 85.0,
    "tx_context": {
      "amount_usd": 5000.0,
      "is_sanctioned": true,
      "is_mixer": false,
      "chain": "ethereum"
    },
    "ground_truth_label": "fraud",
    "tx_hash": "0x...",
    "chain": "ethereum",
    "data_source": "etherscan_high_risk"
  }
]
```

---

## 🗂️ 디렉토리 구조

```
data/
├── dataset/
│   ├── real_high_risk.json      # 고위험 주소 데이터
│   ├── real_balanced.json        # 균형잡힌 데이터
│   ├── train.json                # 학습 데이터 (분할 후)
│   ├── val.json                  # 검증 데이터 (분할 후)
│   └── test.json                 # 테스트 데이터 (분할 후)
└── lists/
    ├── sdn_addresses.json         # 제재 주소 리스트
    ├── mixer_addresses.json       # 믹서 주소 리스트
    ├── cex_addresses.json         # CEX 주소 리스트
    └── bridge_contracts.json     # 브릿지 컨트랙트 리스트

models/
├── rule_weights.pkl              # AI 학습 모델
└── rule_weights_rule_based.pkl   # 규칙 기반 가중치

logs/
├── collect.log                   # 수집 로그
└── collection_progress.json      # 진행 상황
```

---

## 🔄 데이터 수집 상태 확인

### 진행 상황 확인

```bash
# 진행 상황 파일 확인
cat logs/collection_progress.json

# 로그 확인
tail -f logs/collect.log
```

### Python으로 확인

```python
import json
from pathlib import Path

# 진행 상황 확인
progress_file = Path("logs/collection_progress.json")
if progress_file.exists():
    with open(progress_file, 'r') as f:
        progress = json.load(f)

    print(f"상태: {progress.get('status')}")
    print(f"시작 시간: {progress.get('started_at')}")
    print(f"완료 주소: {progress.get('completed_addresses')}/{progress.get('total_addresses')}")
    print(f"수집된 거래: {progress.get('collected_transactions')}개")
else:
    print("진행 상황 파일이 없습니다.")
```

---

## 💾 데이터 백업

### 중요 데이터 백업

```bash
# 데이터셋 백업
cp -r data/dataset data/dataset_backup_$(date +%Y%m%d)

# 모델 백업
cp -r models models_backup_$(date +%Y%m%d)
```

---

## 🧹 데이터 정리

### 오래된 데이터 삭제

```bash
# 30일 이상 된 백업 삭제
find data/dataset_backup_* -type d -mtime +30 -exec rm -rf {} \;
```

---

## 📝 현재 상태 확인 스크립트

```python
# scripts/check_data_status.py
import json
from pathlib import Path

def check_data_status():
    """데이터 상태 확인"""
    dataset_dir = Path("data/dataset")

    print("=" * 60)
    print("데이터 저장 상태")
    print("=" * 60)

    # 데이터셋 파일 확인
    dataset_files = list(dataset_dir.glob("*.json"))

    if not dataset_files:
        print("\n❌ 데이터셋 파일이 없습니다.")
        return

    for file in dataset_files:
        size = file.stat().st_size
        print(f"\n📄 {file.name}")
        print(f"   크기: {size:,} bytes ({size/1024:.2f} KB)")

        if size > 0:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    print(f"   샘플 수: {len(data)}개")

                    if data:
                        # 라벨 분포
                        labels = [d.get("ground_truth_label", "unknown") for d in data]
                        label_counts = {}
                        for label in labels:
                            label_counts[label] = label_counts.get(label, 0) + 1

                        print(f"   라벨 분포:")
                        for label, count in label_counts.items():
                            print(f"     {label}: {count}개")
                else:
                    print(f"   형식: {type(data).__name__}")
            except Exception as e:
                print(f"   ⚠️  로드 실패: {e}")
        else:
            print("   ⚠️  파일이 비어있습니다.")

    # 진행 상황 확인
    progress_file = Path("logs/collection_progress.json")
    if progress_file.exists():
        print("\n" + "=" * 60)
        print("수집 진행 상황")
        print("=" * 60)

        with open(progress_file, 'r') as f:
            progress = json.load(f)

        print(f"상태: {progress.get('status', 'unknown')}")
        print(f"시작: {progress.get('started_at', 'unknown')}")
        print(f"완료 주소: {progress.get('completed_addresses', 0)}/{progress.get('total_addresses', 0)}")
        print(f"수집된 거래: {progress.get('collected_transactions', 0)}개")

if __name__ == "__main__":
    check_data_status()
```

---

## 🔗 관련 파일

- `scripts/collect_real_data.py`: 데이터 수집 스크립트
- `core/scoring/real_dataset_builder.py`: 데이터셋 구축 모듈
- `data/dataset/`: 데이터셋 저장 디렉토리
- `logs/`: 로그 및 진행 상황 저장 디렉토리
