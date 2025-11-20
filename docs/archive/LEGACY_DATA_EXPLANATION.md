# Legacy 데이터 설명

## 📋 개요

Legacy 데이터는 **GOG (Graph of Graphs) 논문**에서 연구진들이 수집한 특정 기간의 라벨링된 블록체인 데이터입니다.

### 데이터 소스

- **출처**: Graph of Graphs 논문 연구진
- **수집 기간**: 2016-02 ~ 2024-02 (약 8년간)
- **체인**: Ethereum, Polygon, BSC
- **데이터 소스**: 주요 블록체인 탐색기
  - [Etherscan](https://etherscan.io/)
  - [Polygonscan](https://polygonscan.com/)
  - [Bscscan](https://bscscan.com/)

---

## 📊 데이터 규모 (논문 기준)

### Ethereum (실험에서 사용)

- **# Token**: 14,464개
- **시작 월**: 2016-02
- **종료 월**: 2024-02
- **# Transactions**: 81,788,211개
- **# Addresses**: 10,247,767개

### Polygon

- **# Token**: 2,353개
- **시작 월**: 2020-08
- **종료 월**: 2024-02
- **# Transactions**: 64,882,233개
- **# Addresses**: 1,801,976개

### BSC

- **# Token**: 7,499개
- **시작 월**: 2020-09
- **종료 월**: 2024-02
- **# Transactions**: 121,612,480개
- **# Addresses**: 6,550,399개

---

## 🏷️ 라벨링 정보

### 라벨 정의 방법

Legacy 데이터의 라벨은 **Etherscan에서 제공하는 주소 태그**를 기반으로 정의되었습니다.

#### 라벨링 프로세스 (추정)

1. **Etherscan 태그 수집**

   - Etherscan API 또는 웹사이트에서 주소별 태그 정보 수집
   - 태그 종류: Phishing, Hack, Scam, Finance, Meme 등

2. **Fraud 라벨 할당**

   - **Phishing 태그**: 피싱 관련 주소 → `label = 1` (fraud)
   - **Hack 태그**: 해킹 관련 주소 → `label = 1` (fraud)
   - **Scam 태그**: 사기 관련 주소 → `label = 1` (fraud)
   - **기타 의심스러운 태그**: Suspicious 등 → `label = 1` (fraud)

3. **Normal 라벨 할당**
   - **Finance 태그**: 금융 관련 주소 → `label = 0` (normal)
   - **Meme 태그**: 밈 토큰 관련 주소 → `label = 0` (normal)
   - **기타 정상 태그**: 일반적인 카테고리 → `label = 0` (normal)
   - **태그 없음**: 태그가 없는 주소 → `label = 0` (normal, 추정)

### Fraud Cases (`label = 1`)

- **정의**: Suspicious phishing or hack tokens
- **라벨 소스**: **Etherscan 태그 기반**
  - Phishing 태그
  - Hack 태그
  - Scam 태그
  - 기타 의심스러운 태그
- **특징**:
  - 피싱 또는 해킹 관련 토큰
  - 의심스러운 거래 패턴
  - 위험 주소와의 연결
  - **Etherscan에서 공식적으로 표시된 위험 주소**

### Other Classes / Normal (`label = 0`)

- **정의**: Category tag, such as Finance, Meme
- **라벨 소스**: **Etherscan 태그 기반**
  - Finance 태그
  - Meme 태그
  - 기타 정상 카테고리 태그
  - 태그 없음 (추정)
- **특징**:
  - 정상적인 토큰 (Finance, Meme 등)
  - 일반적인 거래 패턴
  - 정상 주소와의 연결
  - **Etherscan에서 정상으로 분류된 주소**

### 라벨의 신뢰성

#### 장점

1. **공식 데이터 소스**

   - Etherscan은 가장 신뢰할 수 있는 이더리움 블록체인 탐색기
   - 공식적으로 검증된 태그 정보

2. **실제 운영 환경과 유사**

   - 실제로 CEX나 규제 기관에서 사용하는 정보
   - 실무적 가치가 높음

3. **일관성**
   - 동일한 기준으로 라벨링
   - 주관적 판단 최소화

#### 한계

1. **태그의 불완전성**

   - 모든 위험 주소가 태그되어 있지 않을 수 있음
   - 태그 업데이트 지연 가능성

2. **태그 정의의 모호성**

   - "Phishing"과 "Scam"의 경계가 모호할 수 있음
   - 카테고리 태그의 정확성

3. **시간적 변화**

   - 과거에는 정상이었지만 나중에 위험으로 분류된 경우
   - 태그가 업데이트되지 않은 경우

4. **주소 레벨 라벨**
   - 주소 전체에 대한 라벨
   - 특정 거래는 다른 성격일 수 있음 (라벨 노이즈)

---

## 📁 Legacy 데이터 구조

### 1. Features 파일

**경로**: `legacy/data/features/ethereum_basic_metrics_processed.csv`

**구조**:

```csv
Chain,Contract,Num_nodes,Num_edges,Density,Assortativity,Reciprocity,Effective_Diameter,Clustering_Coefficient,label
ethereum,0x00000000000045166c45af0fc6e4cf31d9e14b9a,1636,3047,0.0011391250383197625,-0.4472135937574412,0.29996718083360685,8.0,0.09112948947503759,0
```

**컬럼 설명**:

- `Chain`: 블록체인 (ethereum, polygon, bsc)
- `Contract`: 컨트랙트 주소
- `Num_nodes`: 그래프 노드 수
- `Num_edges`: 그래프 엣지 수
- `Density`: 그래프 밀도
- `Assortativity`: 어소티비티 (연결성 패턴)
- `Reciprocity`: 상호성 (양방향 연결 비율)
- `Effective_Diameter`: 유효 직경
- `Clustering_Coefficient`: 클러스터링 계수
- `label`: 라벨 (0=normal, 1=fraud)

**특징**:

- **주소 레벨 라벨**: 각 컨트랙트 주소에 대한 라벨
- **그래프 통계**: 주소의 거래 그래프에 대한 통계 정보
- **GOG 논문**: Graph of Graphs 방법론으로 계산된 통계

### 2. Transaction 파일

**경로**: `legacy/data/transactions/ethereum/{contract_address}.csv`

**구조**:

```csv
block_number,from,to,transaction_hash,value,timestamp
12230315,0x0000000000000000000000000000000000000000,0xc37f3a8c511329c9028b8d82f491847256b56de7,0xdd58ea28b846abba6e98bfa1c63968767607a47320dfb9b14e99a9e744302739,10000000000000000000000000,1618297835
```

**컬럼 설명**:

- `block_number`: 블록 번호
- `from`: 송신 주소
- `to`: 수신 주소
- `transaction_hash`: 트랜잭션 해시
- `value`: 거래 금액 (Wei 단위)
- `timestamp`: 타임스탬프 (Unix timestamp)

**특징**:

- **거래 레벨 데이터**: 각 컨트랙트 주소의 모든 거래 내역
- **USD 변환 없음**: 원본 Wei 값만 포함
- **라벨 없음**: 거래 자체에는 라벨이 없음 (주소 레벨 라벨 사용)

---

## 🔄 데이터 매칭 과정

### 문제점

1. **Features 파일**: 주소 레벨 라벨 (label 0 또는 1)
2. **Transaction 파일**: 거래 레벨 데이터 (라벨 없음)
3. **목표**: 거래 레벨 데이터셋 구축 (학습용)

### 해결 방법

1. **Features 파일에서 주소별 라벨 추출**

   ```python
   contract = "0x..."
   label = 1  # fraud 또는 0 (normal)
   ```

2. **해당 주소의 Transaction 파일 로드**

   ```python
   transactions = load_transactions(f"legacy/data/transactions/ethereum/{contract}.csv")
   ```

3. **각 거래에 주소 레벨 라벨 적용**

   ```python
   for tx in transactions:
       tx["ground_truth_label"] = "fraud" if label == 1 else "normal"
   ```

4. **Rule 평가 및 Feature 추출**

   - 각 거래에 대해 룰 평가
   - 그래프 통계 feature 계산
   - ML feature 추출

5. **최종 데이터셋 생성**
   - 거래 레벨 데이터셋
   - Rule results 제거 (데이터 누수 방지)
   - ML features 포함

---

## 📈 현재 프로젝트에서의 활용

### 1. 데이터셋 구축

- **파일**: `scripts/collect_diverse_rules_data.py`
- **입력**:
  - `legacy/data/features/ethereum_basic_metrics_processed.csv`
  - `legacy/data/transactions/ethereum/*.csv`
- **출력**:
  - `data/dataset/diverse_rules_enhanced_sampled.json` (5,000개 샘플)
  - `data/dataset/diverse_rules_enhanced.json` (전체, 92,138개 샘플)

### 2. 데이터 분할

- **Train**: 3,499개 (70%)
- **Val**: 749개 (15%)
- **Test**: 752개 (15%)

### 3. 실험 범위

- **체인**: Ethereum만 사용 (GOG 논문과 동일)
- **이유**:
  - Legacy 데이터에서 Ethereum이 가장 많음
  - GOG 논문에서도 Ethereum으로 실험
  - 데이터 일관성 유지

---

## ⚠️ 주의사항

### 1. 라벨의 한계

#### 1.1 주소 레벨 라벨

- **문제**: 거래 레벨이 아닌 주소 레벨 라벨
- **가정**: 같은 주소의 모든 거래가 같은 라벨을 가짐
- **실제**: 일부 거래는 다른 라벨일 수 있음 (라벨 노이즈)
- **예시**:
  - 주소가 대부분 정상 거래를 하지만, 일부 피싱 거래가 있을 수 있음
  - 주소가 나중에 위험으로 분류되었지만, 과거 거래는 정상일 수 있음

#### 1.2 Etherscan 태그의 한계

- **불완전성**: 모든 위험 주소가 태그되어 있지 않을 수 있음
- **업데이트 지연**: 태그가 실시간으로 업데이트되지 않을 수 있음
- **정의 모호성**: "Phishing"과 "Scam"의 경계가 모호할 수 있음
- **시간적 변화**: 과거에는 정상이었지만 나중에 위험으로 분류된 경우

### 2. 시간 범위

- **수집 기간**: 2016-02 ~ 2024-02
- **최신성**: 일부 데이터가 오래됨
- **시장 변화**: 암호화폐 시장이 크게 변화함

### 3. 데이터 불균형

- **Normal**: 58.1% (2,904개)
- **Fraud**: 41.9% (2,096개)
- **비고**: 상대적으로 균형 잡힌 분포

### 4. Feature 계산

- **그래프 통계**: Legacy 데이터의 그래프 통계와 다를 수 있음
- **이유**:
  - Legacy: GOG 방법론으로 계산
  - 현재: MPOCryptoML 방법론으로 재계산
  - 차이: 방법론이 다르면 결과도 다를 수 있음

---

## 📚 참고 자료

### GOG 논문

- **제목**: Graph of Graphs (추정)
- **내용**: 블록체인 데이터 수집 및 라벨링
- **데이터**: Ethereum, Polygon, BSC
- **기간**: 2016-02 ~ 2024-02

### 데이터 소스

- [Etherscan](https://etherscan.io/)
- [Polygonscan](https://polygonscan.com/)
- [Bscscan](https://bscscan.com/)

---

## 🎯 현재 프로젝트에서의 의미

### 1. 학습 데이터 제공

- **목적**: 모델 학습을 위한 라벨링된 데이터
- **규모**: 92,138개 샘플 (Ethereum)
- **품질**: 연구진이 수집 및 라벨링한 데이터

### 2. Baseline 비교

- **GOG 논문**: 기존 연구 결과
- **현재 프로젝트**: 2단계 스코어러 성능
- **비교**: Baseline 대비 우수성 입증

### 3. 실험 재현성

- **동일 데이터**: GOG 논문과 동일한 데이터 소스
- **공정 비교**: 같은 데이터로 성능 비교 가능
- **학술적 가치**: 기존 연구와의 비교 가능

---

## 📊 데이터 통계 (현재 프로젝트)

### 전체 데이터셋

- **총 샘플**: 92,138개 (Ethereum)
- **Normal**: 58.1% (53,500개)
- **Fraud**: 41.9% (38,638개)

### 학습 데이터셋 (Sampled)

- **총 샘플**: 5,000개
- **Normal**: 58.1% (2,904개)
- **Fraud**: 41.9% (2,096개)

### 분할

- **Train**: 3,499개 (70%)
- **Val**: 749개 (15%)
- **Test**: 752개 (15%)

---

## 💡 결론

Legacy 데이터는:

1. **GOG 논문 연구진이 수집한 데이터**

   - 기간: 2016-02 ~ 2024-02
   - 체인: Ethereum, Polygon, BSC
   - 소스: Etherscan, Polygonscan, Bscscan

2. **라벨링된 데이터**

   - Fraud: Suspicious phishing or hack tokens
   - Normal: Category tag (Finance, Meme 등)

3. **현재 프로젝트의 기반**

   - 학습 데이터 제공
   - Baseline 비교 기준
   - 실험 재현성 확보

4. **Ethereum만 사용**
   - GOG 논문과 동일
   - 데이터 일관성 유지
   - 실험 범위 명확화
