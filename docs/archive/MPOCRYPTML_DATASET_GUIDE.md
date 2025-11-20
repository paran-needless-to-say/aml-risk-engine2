# MPOCryptoML 학습용 데이터셋 구축 가이드

## 📋 개요

MPOCryptoML 방법론을 학습하기 위한 데이터셋 구축 방법입니다.

**필요한 데이터:**
1. 주소별 거래 데이터 (3-hop까지)
2. MPOCryptoML 피처 (PPR, 패턴, NTS, NWS)
3. 실제 라벨 (fraud/normal)

---

## 🎯 데이터 수집 방법

### 방법 1: 레거시 데이터 활용 (현재 구현)

레거시 데이터에서 3-hop 그래프를 구축하고 MPOCryptoML 피처를 추출합니다.

**장점:**
- 이미 라벨이 있음
- 빠른 구축 가능

**단점:**
- 3-hop 데이터가 제한적 (직접 거래만)
- 실제 3-hop 그래프 구조가 완전하지 않을 수 있음

**사용법:**
```bash
# 전체 데이터
python scripts/build_mpocryptml_dataset.py

# 샘플 테스트 (10%, 주소당 최대 50건)
python scripts/build_mpocryptml_dataset.py \
    --sample-ratio 0.1 \
    --max-txs-per-contract 50
```

### 방법 2: Etherscan API로 새로 수집 (권장)

백엔드에서 3-hop까지 거래 데이터를 제공받아 수집합니다.

**장점:**
- 완전한 3-hop 그래프 구조
- 최신 데이터

**단점:**
- 수집 시간 소요
- API 비용/제한

**구현 필요:**
```python
# core/scoring/real_dataset_builder.py 확장
class RealDatasetBuilder:
    def build_mpocryptml_dataset(
        self,
        addresses: List[str],
        collect_3hop: bool = True
    ):
        # 1. 주소별 거래 수집
        # 2. 3-hop까지 확장
        # 3. MPOCryptoML 피처 추출
        # 4. 라벨링
        pass
```

---

## 📊 데이터셋 구조

### 입력 데이터

**레거시 데이터:**
- `legacy/data/features/ethereum_basic_metrics_processed.csv`
- `legacy/data/transactions/ethereum/{address}.csv`

**Etherscan API:**
- 주소별 거래 데이터
- 3-hop까지 확장된 거래 데이터

### 출력 데이터셋

```json
{
  "address": "0xabc123...",
  "chain": "ethereum",
  "ground_truth_label": "fraud",
  "actual_risk_score": 85.0,
  
  "rule_results": [...],
  "rule_score": 70.0,
  
  "ml_features": {
    "ppr_score": 0.15,
    "sdn_ppr": 0.10,
    "mixer_ppr": 0.05,
    "pattern_score": 45.0,
    "n_theta": 0.8,
    "n_omega": 0.6,
    "detected_patterns": ["fan_in", "stack"],
    "fan_in_count": 5,
    "fan_out_count": 3,
    "gather_scatter": 10000.0,
    "graph_nodes": 50,
    "graph_edges": 120
  },
  
  "num_transactions": 100,
  "data_source": "legacy_mpocryptml"
}
```

---

## 🔄 데이터셋 구축 프로세스

### 1단계: 데이터 수집

```bash
# 레거시 데이터로 구축
python scripts/build_mpocryptml_dataset.py \
    --output-path data/dataset/mpocryptml_ethereum.json
```

### 2단계: 데이터셋 분할

```bash
# 학습/검증/테스트 분할 (70:15:15)
python scripts/split_dataset.py \
    --input data/dataset/mpocryptml_ethereum.json \
    --output-dir data/dataset/mpocryptml
```

### 3단계: 모델 학습

```bash
# MPOCryptoML 모델 학습
python scripts/train_mpocryptml_model.py
```

---

## 📈 데이터셋 통계

구축 후 확인할 통계:

1. **라벨 분포**: Fraud vs Normal 비율
2. **그래프 크기**: 평균 노드/엣지 수
3. **피처 분포**: PPR, 패턴 점수 분포
4. **패턴 탐지율**: 각 패턴이 탐지된 비율

---

## 🎯 피처 설명

### Rule-based 피처
- `rule_results`: 발동된 룰 목록
- `rule_score`: Rule-based 점수 (0~100)

### MPOCryptoML 피처
- `ppr_score`: Multi-source PPR 점수
- `sdn_ppr`: SDN과의 PPR 연결성
- `mixer_ppr`: 믹서와의 PPR 연결성
- `pattern_score`: 그래프 패턴 점수
- `n_theta`: Timestamp 정규화 점수
- `n_omega`: Weight 정규화 점수
- `detected_patterns`: 탐지된 패턴 리스트
- `fan_in_count`, `fan_out_count`: 연결 개수
- `gather_scatter`: Gather-scatter 값
- `graph_nodes`, `graph_edges`: 그래프 크기

---

## ⚠️ 주의사항

1. **3-hop 데이터 제한**: 레거시 데이터는 직접 거래만 포함
   - 실제 3-hop 그래프는 백엔드에서 제공 필요

2. **USD 값 부재**: 레거시 데이터에 USD 값이 없을 수 있음
   - Weight 정규화에 영향

3. **그래프 크기**: 너무 큰 그래프는 처리 시간 증가
   - `max_transactions_per_contract`로 제한

---

## 🔗 관련 파일

- `scripts/build_mpocryptml_dataset.py`: 데이터셋 구축 스크립트
- `core/aggregation/mpocryptml_scorer.py`: MPOCryptoML 피처 추출
- `core/scoring/real_dataset_builder.py`: 실제 데이터 수집 (확장 필요)

---

## 📝 다음 단계

1. **백엔드 연동**: 3-hop 데이터 수집 API 연동
2. **대규모 수집**: Etherscan API로 실제 데이터 수집
3. **데이터 품질 개선**: USD 값, 타임스탬프 정확도 향상
4. **평가**: 데이터셋 품질 평가 및 개선

