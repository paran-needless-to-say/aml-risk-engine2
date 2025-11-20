# MPOCryptoML 방법론 통합 가이드

## 📋 개요

MPOCryptoML 논문의 방법론을 현재 Rule-based 시스템에 통합하여 하이브리드 리스크 스코어링을 구현했습니다.

**하이브리드 접근 방식:**
- **Rule-based (70%)**: TRACE-X 룰 기반 점수
- **MPOCryptoML (30%)**: 그래프 패턴 분석 점수

---

## 🏗️ 구현 구조

### 1. 핵심 모듈

#### `MPOCryptoMLNormalizer` (`core/aggregation/mpocryptml_normalizer.py`)
- **Nθ(vi)**: Normalized Timestamp Score
  - 시간적 비대칭성 측정
  - 유입/유출 거래의 시간 분포 차이 분석
  - 세탁 계정 탐지 (빠른 자금 순환)
  
- **Nω(vi)**: Normalized Weight Score
  - 거래 금액 불균형 측정
  - 유입/유출 금액 분포 차이 분석

#### `MPOCryptoMLScorer` (`core/aggregation/mpocryptml_scorer.py`)
- Multi-source PPR 점수 계산
- 그래프 패턴 탐지 (Fan-in, Fan-out, Gather-scatter, Stack, Bipartite)
- Timestamp/Weight 정규화 점수 통합
- 최종 MPOCryptoML 점수 계산 (0~100)

#### `HybridAddressAnalyzer` (`core/scoring/hybrid_address_analyzer.py`)
- Rule-based + MPOCryptoML 통합 분석기
- 최종 점수: `0.7 * rule_score + 0.3 * ml_score`

#### `PPRConnector` (개선됨)
- Multi-source Personalized PageRank 구현
- 논문 Algorithm 1 기반
- 소스 노드 자동 탐지

---

## 🚀 사용 방법

### API 엔드포인트

#### 하이브리드 분석 (권장)

```bash
POST /address/hybrid
```

**Request:**
```json
{
  "address": "0xabc123...",
  "chain": "ethereum",
  "transactions": [
    {
      "tx_hash": "0x...",
      "from": "0x...",
      "to": "0x...",
      "amount_usd": 1000.0,
      "timestamp": "2024-01-01T00:00:00Z",
      ...
    }
  ],
  "transactions_3hop": [
    // 3-hop까지의 거래 데이터 (MPOCryptoML용)
    // 백엔드에서 제공
  ],
  "analysis_type": "hybrid"  // "basic", "rule_only", "hybrid"
}
```

**Response:**
```json
{
  "target_address": "0xabc123...",
  "risk_score": 75.5,
  "risk_level": "high",
  "rule_score": 70.0,
  "ml_score": 85.0,
  "ml_details": {
    "ppr_score": 0.15,
    "pattern_score": 45.0,
    "nts_score": 12.0,
    "nws_score": 8.0,
    "detected_patterns": ["fan_in", "stack"]
  },
  "risk_tags": ["mixer_inflow", "ml_pattern_fan_in"],
  "fired_rules": [...],
  "explanation": "...",
  "completed_at": "2024-01-01T00:00:00Z"
}
```

### Python 코드 사용

```python
from core.scoring.hybrid_address_analyzer import HybridAddressAnalyzer

# 분석기 초기화
analyzer = HybridAddressAnalyzer(
    rule_weight=0.7,  # Rule-based 가중치
    ml_weight=0.3,    # MPOCryptoML 가중치
    use_ml=True       # MPOCryptoML 사용 여부
)

# 분석 수행
result = analyzer.analyze_address(
    address="0xabc123...",
    chain="ethereum",
    transactions=direct_transactions,      # 직접 거래
    transactions_3hop=transactions_3hop,    # 3-hop 거래
    analysis_type="hybrid"
)

print(f"최종 점수: {result.risk_score}")
print(f"Rule-based: {result.rule_score}")
print(f"MPOCryptoML: {result.ml_score}")
print(f"탐지된 패턴: {result.ml_details.get('detected_patterns', [])}")
```

---

## 📊 MPOCryptoML 점수 구성

### 1. PPR 점수 (30%)
- Multi-source Personalized PageRank
- 제재 주소/믹서와의 연결성
- 소스 노드에서의 랜덤 워크 점수

### 2. 패턴 점수 (40%)
- **Fan-in**: 여러 주소에서 하나로 집중
- **Fan-out**: 하나에서 여러 주소로 분산
- **Gather-scatter**: Fan-in + Fan-out 조합
- **Stack**: 선형 경로 패턴
- **Bipartite**: 이분 그래프 구조

### 3. Timestamp 정규화 (15%)
- Nθ(vi): 시간적 비대칭성
- 세탁 계정은 유입 후 빠른 유출

### 4. Weight 정규화 (15%)
- Nω(vi): 금액 불균형
- 유입/유출 금액 분포 차이

---

## 🔧 설정

### 가중치 조정

```python
analyzer = HybridAddressAnalyzer(
    rule_weight=0.8,  # Rule-based 비중 증가
    ml_weight=0.2     # MPOCryptoML 비중 감소
)
```

### 분석 타입 선택

- **`"basic"`**: Rule-based만 사용 (빠름, 1-2초)
- **`"rule_only"`**: Rule-based만 사용
- **`"hybrid"`**: Rule-based + MPOCryptoML (기본값, 3-10초)

---

## 📝 데이터 요구사항

### 필수 데이터
- `transactions`: 주소의 직접 거래 히스토리
  - `from`, `to`, `amount_usd`, `timestamp` 필수

### 선택 데이터 (MPOCryptoML 활성화)
- `transactions_3hop`: 3-hop까지의 거래 데이터
  - 백엔드에서 제공 가능
  - 그래프 구조 분석에 사용

---

## 🎯 장점

1. **Rule-based 즉시 사용**: 기존 룰 기반 점수는 항상 계산
2. **MPOCryptoML 보완**: 그래프 패턴으로 추가 탐지
3. **점진적 통합**: 3-hop 데이터가 없어도 Rule-based만으로 동작
4. **유연한 가중치**: Rule-based와 MPOCryptoML 비중 조정 가능

---

## 🔗 관련 파일

- `core/aggregation/mpocryptml_normalizer.py`: Timestamp/Weight 정규화
- `core/aggregation/mpocryptml_scorer.py`: MPOCryptoML 점수 계산
- `core/aggregation/mpocryptml_patterns.py`: 그래프 패턴 탐지
- `core/aggregation/ppr_connector.py`: Multi-source PPR
- `core/scoring/hybrid_address_analyzer.py`: 하이브리드 분석기
- `api/routes/hybrid_address_analysis.py`: API 엔드포인트

---

## 📚 참고

- **논문**: MPOCryptoML: Multi-Pattern based Off-Chain Crypto Money Laundering Detection
- **Table V**: Baseline 모델 성능 비교
- **Algorithm 1**: Multi-source Personalized PageRank
- **Section IV**: Problem Definition

---

## 🚧 향후 개선

1. **Logistic Regression 모델**: 패턴 피처 → 점수 변환 (논문 방식)
2. **하이퍼파라미터 튜닝**: PPR damping factor, 가중치 최적화
3. **성능 최적화**: 대규모 그래프 처리 개선
4. **평가 메트릭**: Precision@K, Recall@K, F1-score 추가

