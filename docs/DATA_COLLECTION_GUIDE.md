# 실제 데이터 수집 가이드

## 🔑 API 키 설정

### 방법 1: 코드에 기본값 설정 (현재 상태)

```python
# 이미 설정됨: 91FZVKNIX7GYPESECU5PHPZIMKD72REX43
```

### 방법 2: 환경변수 사용 (권장)

```bash
export ETHERSCAN_API_KEY="91FZVKNIX7GYPESECU5PHPZIMKD72REX43"
```

---

## 📊 데이터 수집 방식

### 1. 고위험 주소만 수집 (빠름, 불균형)

**특징**:

- 제재 주소(SDN)와 믹서 주소의 거래만 수집
- 빠르게 수집 가능
- 라벨이 대부분 "fraud"로 불균형

**사용 시나리오**:

- 초기 테스트
- 고위험 패턴 분석
- 빠른 프로토타이핑

**실행**:

```bash
python scripts/collect_real_data.py
# 선택: 1
```

**결과**:

- `data/dataset/real_high_risk.json`
- 대부분 fraud 라벨
- 빠른 수집 (약 5-10분)

---

### 2. 고위험 + 정상 주소 수집 (느림, 균형) ⭐ **권장**

**특징**:

- 고위험 주소(제재, 믹서) + 정상 주소(CEX 등) 모두 수집
- 균형잡힌 데이터셋
- 더 정확한 모델 학습 가능

**사용 시나리오**:

- 실제 모델 학습
- 프로덕션 데이터셋 구축
- 정확한 성능 평가

**실행**:

```bash
python scripts/collect_real_data.py
# 선택: 2
```

**결과**:

- `data/dataset/real_balanced.json`
- Fraud와 Normal 균형
- 느린 수집 (약 20-30분)

---

## 🔄 수집 프로세스

### 단계별 설명

1. **주소 리스트 로드**

   ```python
   # 제재 주소 (SDN)
   sdn_list = list_loader.get_sdn_list()

   # 믹서 주소
   mixer_list = list_loader.get_mixer_list()

   # CEX 주소
   cex_list = list_loader.get_cex_list()
   ```

2. **거래 내역 수집**

   ```python
   # Etherscan API로 각 주소의 거래 내역 수집
   transactions = collector.collect_address_transactions(
       address="0x...",
       max_transactions=50  # 주소당 최대 거래 수
   )
   ```

3. **태그 정보 조회**

   ```python
   # 각 주소의 Etherscan 태그 정보 조회
   tags = client.get_address_tags(address)
   # {
   #   "label": "cex",
   #   "is_exchange": True,
   #   "is_contract": False,
   #   ...
   # }
   ```

4. **라벨링**

   ```python
   # 자동 라벨링
   if is_sanctioned or is_mixer:
       label = "fraud"
       score = 85.0
   elif is_cex:
       label = "normal"
       score = 15.0
   ```

5. **룰 평가**

   ```python
   # 각 거래에 대해 룰 평가
   rule_results = rule_evaluator.evaluate_single_transaction(tx)
   ```

6. **데이터셋 저장**
   ```python
   # JSON 형식으로 저장
   {
       "rule_results": [...],
       "actual_risk_score": 85.0,
       "ground_truth_label": "fraud",
       "tx_context": {...}
   }
   ```

---

## ⚙️ 수집 설정

### 주소당 최대 거래 수

```python
# 방법 1: 고위험 주소만
dataset = builder.build_from_high_risk_addresses(
    addresses=high_risk_addresses,
    max_transactions_per_address=50,  # 주소당 최대 50개
    output_path="data/dataset/real_high_risk.json"
)

# 방법 2: 균형잡힌 데이터셋
dataset = builder.build_from_known_addresses(
    high_risk_addresses=high_risk_addresses,
    normal_addresses=normal_addresses,
    max_transactions_per_address=30,  # 주소당 최대 30개
    output_path="data/dataset/real_balanced.json"
)
```

**권장값**:

- 테스트: 10-20개
- 학습용: 30-50개
- 대규모: 100개 이상

---

## 📈 수집 시간 예상

### 고위험 주소만 (선택 1)

| 주소 수 | 주소당 거래 | 예상 시간 |
| ------- | ----------- | --------- |
| 10개    | 50개        | 5-10분    |
| 20개    | 50개        | 10-20분   |
| 40개    | 50개        | 20-40분   |

### 고위험 + 정상 (선택 2)

| 고위험 | 정상 | 주소당 거래 | 예상 시간 |
| ------ | ---- | ----------- | --------- |
| 10개   | 5개  | 30개        | 15-25분   |
| 20개   | 10개 | 30개        | 30-50분   |
| 40개   | 20개 | 30개        | 60-100분  |

**참고**: Rate limit (5 calls/sec)로 인해 시간이 걸릴 수 있습니다.

---

## 🎯 수집 전략

### 전략 1: 점진적 수집 (권장)

```python
# 1단계: 소량으로 테스트
dataset = builder.build_from_high_risk_addresses(
    addresses=high_risk_addresses[:5],  # 처음 5개만
    max_transactions_per_address=10,
    output_path="data/dataset/test.json"
)

# 2단계: 중간 규모
dataset = builder.build_from_high_risk_addresses(
    addresses=high_risk_addresses[:20],
    max_transactions_per_address=30,
    output_path="data/dataset/medium.json"
)

# 3단계: 전체 수집
dataset = builder.build_from_high_risk_addresses(
    addresses=high_risk_addresses,
    max_transactions_per_address=50,
    output_path="data/dataset/full.json"
)
```

---

### 전략 2: 배치 수집

```python
# 여러 번 나눠서 수집
for i in range(0, len(addresses), 10):
    batch = addresses[i:i+10]
    dataset = builder.build_from_high_risk_addresses(
        addresses=batch,
        max_transactions_per_address=50,
        output_path=f"data/dataset/batch_{i//10}.json"
    )

    # 나중에 병합
    # python scripts/merge_datasets.py
```

---

## ⚠️ 주의사항

### 1. Rate Limit

Etherscan API는 **5 calls/sec** 제한이 있습니다.

- 자동으로 0.2초 간격으로 요청
- 대량 수집 시 시간이 오래 걸릴 수 있음

### 2. API 할당량

무료 API 키:

- **하루 100,000 calls** 제한
- 주소당 약 2-3 calls (거래 내역 + 태그)
- 약 30,000-50,000개 주소 수집 가능

### 3. 에러 처리

```python
# 자동 재시도 없음
# 에러 발생 시 다음 주소로 넘어감
# 실패한 주소는 로그에 기록됨
```

---

## 🔍 수집 데이터 확인

### 데이터셋 구조

```json
[
  {
    "rule_results": [
      {
        "rule_id": "C-001",
        "score": 30,
        "axis": "C",
        "severity": "HIGH"
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

### 통계 확인

```python
import json

with open("data/dataset/real_balanced.json", 'r') as f:
    dataset = json.load(f)

print(f"총 샘플: {len(dataset)}개")
print(f"Fraud: {sum(1 for d in dataset if d['ground_truth_label'] == 'fraud')}개")
print(f"Normal: {sum(1 for d in dataset if d['ground_truth_label'] == 'normal')}개")
```

---

## 🚀 빠른 시작

### 1. 테스트 수집 (5분)

```bash
python scripts/collect_real_data.py
# 선택: 1
# 주소당 거래: 10개 (코드에서 수정)
```

### 2. 실제 수집 (30분)

```bash
python scripts/collect_real_data.py
# 선택: 2
# 주소당 거래: 30개
```

### 3. 대규모 수집 (2시간+)

```bash
# 코드에서 주소 수와 거래 수 조정
python scripts/collect_real_data.py
```

---

## 📝 다음 단계

수집 완료 후:

1. **데이터셋 분할**

   ```bash
   python scripts/split_dataset.py
   ```

2. **AI 모델 학습**

   ```bash
   python scripts/train_model.py
   ```

3. **성능 평가**
   ```bash
   python scripts/evaluate_model.py
   ```

---

## 💡 팁

### 효율적인 수집

1. **최신 거래 우선**: `sort="desc"` (기본값)
2. **주소당 거래 수 제한**: 불필요한 API 호출 방지
3. **에러 로그 확인**: 실패한 주소 재시도

### 데이터 품질 향상

1. **태그 정보 활용**: Etherscan 태그로 정확한 라벨링
2. **알려진 리스트 활용**: CEX, 믹서 리스트와 매칭
3. **균형잡힌 수집**: Fraud와 Normal 균형 유지

---

## 🔗 참고

- `core/data/etherscan_client.py`: Etherscan API 클라이언트
- `core/scoring/real_dataset_builder.py`: 데이터셋 구축기
- `scripts/collect_real_data.py`: 수집 스크립트
- `docs/DATASET_BUILDING_GUIDE.md`: 상세 가이드
