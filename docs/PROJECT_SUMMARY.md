# 프로젝트 요약

## 📊 룰셋 구현 현황

### 총 룰 수: 19개

#### ✅ 구현 완료 (11개)

**Compliance (C) - 3개**

- C-001: Sanction Direct Touch ✅
- C-003: High-Value Single Transfer ✅
- C-004: High-Value Repeated Transfer (24h) ✅

**Exposure (E) - 2개**

- E-101: Mixer Direct Exposure ✅
- E-102: Indirect Sanctions Exposure (PPR 기반) ✅

**Behavior (B) - 6개**

- B-101: Burst (10m) ✅
- B-102: Rapid Sequence (1m) ✅
- B-103: Inter-arrival Std High ✅
- B-201: Layering Chain (3홉 데이터 필요) ✅
- B-202: Cycle (3홉 데이터 필요) ✅
- B-203: Fan-out (10m bucket) ✅
- B-204: Fan-in (10m bucket) ✅

#### 🚧 부분 구현 (2개)

- **C-002**: High-Risk Jurisdiction VASP (백엔드 데이터 필요)
- **E-103**: Counterparty Quality Risk (커스터마이징 항목, 백엔드 데이터 필요)

#### ❌ 미구현 (4개)

- **B-401**: First 7 Days Burst (주소 상태 관리 필요)
- **B-402**: Reactivation (주소 상태 관리 필요)
- **B-501**: High-Value Buckets (동적 점수 할당 필요)
- **B-502**: Structuring Pattern (복합 집계 필요)

---

## 📋 앞으로 해야 할 것

### 우선순위 높음

1. **백엔드 연동**

   - 주소의 거래 히스토리 가져오기 API 연동
   - 3홉 거래 데이터 가져오기 (심층 분석용)
   - 체인 선택 기능 추가

2. **주소 상태 관리 시스템**

   - 주소 메타데이터 저장소 구축 (DB 또는 캐시)
   - 주소 생성일, 마지막 거래일, 총 거래 수 등 추적
   - B-401, B-402 룰 구현

3. **동적 점수 할당**
   - 금액에 따른 동적 점수 계산 로직
   - B-501 룰 구현

### 우선순위 중간

4. **복합 집계 로직**

   - 그룹화 및 그룹별 분석
   - B-502 룰 구현

5. **성능 최적화**
   - 그래프 분석 최적화
   - 캐싱 전략 수립
   - 병렬 처리

### 우선순위 낮음

6. **AI 통합**
   - 룰 가중치 학습
   - 이상 패턴 탐지
   - 컨텍스트 기반 점수 조정

---

## 🤖 AI 활용 방안

### 1단계: 룰 가중치 학습 (우선순위: 높음)

**목적**: 각 룰의 가중치를 학습하여 최적의 스코어 계산

**방법**:

- 과거 데이터로 룰 조합과 실제 리스크의 상관관계 학습
- 지도 학습 (Supervised Learning)
- 룰 점수와 실제 위험도의 상관관계 분석

**활용 위치**: `core/aggregation/` 모듈

**예시**:

```python
# 현재: 고정 가중치
risk_score = sum(rule.score for rule in fired_rules)

# AI 적용 후: 학습된 가중치
risk_score = sum(learned_weights[rule.id] * rule.score for rule in fired_rules)
```

---

### 2단계: 룰 조합 최적화

**목적**: 여러 룰이 동시에 발동될 때 최적의 점수 계산

**방법**:

- 앙상블 학습 (Ensemble Learning)
- 메타 학습 (Meta Learning)
- 룰 간 상호작용 모델링

**활용 위치**: `core/scoring/engine.py`

**예시**:

```python
# 현재: 단순 합산
risk_score = sum(rule.score for rule in fired_rules)

# AI 적용 후: 룰 조합 고려
risk_score = ensemble_model.predict(fired_rules)
```

---

### 3단계: 이상 패턴 탐지

**목적**: 룰북에 없는 새로운 패턴 탐지

**방법**:

- 비지도 학습 (Unsupervised Learning)
- 클러스터링 (Clustering)
- 이상 탐지 (Anomaly Detection)
- 그래프 임베딩 (Graph Embedding)

**활용 위치**: `core/aggregation/` 모듈

**예시**:

```python
# 새로운 패턴 탐지
anomaly_score = anomaly_detector.detect(transaction_pattern)
if anomaly_score > threshold:
    # 새로운 패턴으로 분류
    risk_score += anomaly_score
```

---

### 4단계: 컨텍스트 기반 점수 조정

**목적**: 주소의 컨텍스트(나이, 거래 패턴 등)를 고려한 점수 조정

**방법**:

- 시계열 분석 (Time Series Analysis)
- 그래프 임베딩 (Graph Embedding)
- 주소 임베딩 (Address Embedding)

**활용 위치**: `core/scoring/address_analyzer.py`

**예시**:

```python
# 주소 컨텍스트 임베딩
address_embedding = embedder.embed(address, transactions)
context_score = context_model.predict(address_embedding)

# 컨텍스트 기반 점수 조정
adjusted_score = base_score * context_score
```

---

## 📁 파일 구조 정리

### 핵심 파일

```
api/
├── app.py                          # Flask 서버
└── routes/
    ├── address_analysis.py         # 주소 분석 API (통합)
    └── scoring.py                 # 트랜잭션 스코어링 API

core/
├── scoring/
│   ├── engine.py                   # 단일 트랜잭션 스코어링
│   └── address_analyzer.py        # 주소 기반 분석
├── rules/
│   ├── evaluator.py               # 룰 평가기
│   └── loader.py                  # 룰북 로더
├── aggregation/
│   ├── window.py                  # 윈도우 기반 집계
│   ├── bucket.py                  # 버킷 기반 집계
│   ├── topology.py                # 그래프 구조 분석
│   ├── ppr_connector.py           # PPR 연결성 분석
│   ├── stats.py                   # 통계 계산
│   └── mpocryptml_patterns.py     # MPOCryptoML 패턴 탐지
└── data/
    └── lists.py                   # 리스트 관리

rules/
└── tracex_rules.yaml              # TRACE-X 룰북

data/
└── lists/                          # 블랙리스트/화이트리스트
    ├── sdn_addresses.json
    ├── cex_addresses.json
    └── bridge_contracts.json
```

### 문서

```
docs/
├── API_DOCUMENTATION.md            # API 명세서
├── RULE_IMPLEMENTATION_STATUS.md   # 룰 구현 현황
├── USER_SCENARIOS.md              # 사용자 시나리오
├── PERFORMANCE_OPTIMIZATION.md    # 성능 최적화
├── THREE_HOP_IMPLEMENTATION.md    # 3홉 데이터 기반 구현
├── AI_INTEGRATION_PLAN.md         # AI 통합 계획
└── ...
```

---

## 🔗 API 엔드포인트

### 통합된 엔드포인트

**POST /api/analyze/address**

- `analysis_type: "basic"` → 기본 스코어링 (1-2초)
- `analysis_type: "advanced"` → 심층 분석 (5-30초)

**POST /api/score/transaction**

- 단일 트랜잭션 스코어링

**GET /health**

- 서버 상태 확인

**GET /api-docs**

- Swagger API 문서

---

## 📚 참고 문서

- **`docs/RULE_IMPLEMENTATION_STATUS.md`** - 룰 구현 상세 현황
- **`docs/WHY_UNIMPLEMENTED_SIMPLE.md`** - 미구현 룰 이유 (쉬운 설명)
- **`docs/AI_INTEGRATION_PLAN.md`** - AI 통합 계획
- **`docs/USER_SCENARIOS.md`** - 사용자 시나리오
