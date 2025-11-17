# AML Risk Engine

CEX를 위한 주소 추적 및 리스크 스코어링 시스템

룰 베이스드 + AI 집계 방식의 AML (Anti-Money Laundering) 스코어링 엔진

---

## 📋 프로젝트 개요

이 프로젝트는 중앙화 거래소(CEX)를 위한 AML 리스크 스코어링 시스템입니다. 블록체인 주소의 거래 히스토리를 분석하여 리스크를 평가하고, TRACE-X 룰북 기반으로 점수를 계산합니다.

### 주요 기능

- ✅ **주소 기반 리스크 분석**: 주소의 거래 히스토리를 분석하여 리스크 스코어 계산
- ✅ **기본 스코어링**: 빠른 응답 (1-2초), 기본 룰만 평가
- ✅ **심층 분석**: 느린 응답 (5-30초), 모든 룰 평가 (그래프 구조 분석 포함)
- ✅ **TRACE-X 룰북 기반**: Compliance, Exposure, Behavior 3축 룰 평가
- ✅ **OFAC SDN 리스트 통합**: 제재 대상 주소 자동 탐지
- ⏳ **AI 집계**: 향후 룰 가중치 학습 및 최적화 (계획)

---

## 📁 프로젝트 구조

```
aml-risk-engine2/
│
├── 📡 api/                          # API 엔드포인트
│   ├── app.py                      # Flask 서버
│   ├── routes/                     # API 라우트
│   │   ├── address_analysis.py     # 주소 분석 API
│   │   └── scoring.py              # 트랜잭션 스코어링 API
│   └── test_*.py                   # 테스트 파일
│
├── 🧠 core/                         # 핵심 로직
│   ├── scoring/                    # 스코어링 엔진
│   │   ├── engine.py               # 단일 트랜잭션 스코어링
│   │   └── address_analyzer.py     # 주소 기반 분석
│   ├── rules/                      # 룰 평가
│   │   ├── evaluator.py           # 룰 평가기
│   │   └── loader.py              # 룰북 로더
│   ├── aggregation/                # 집계 모듈
│   │   ├── window.py              # 윈도우 기반 집계
│   │   ├── bucket.py              # 버킷 기반 집계
│   │   ├── topology.py            # 그래프 구조 분석
│   │   ├── ppr_connector.py       # PPR 연결성 분석
│   │   ├── stats.py               # 통계 계산
│   │   └── mpocryptml_patterns.py # MPOCryptoML 패턴 탐지
│   └── data/                       # 데이터 로더
│       └── lists.py               # 리스트 관리 (SDN, CEX, Mixer 등)
│
├── 📜 rules/                        # 룰북 정의
│   └── tracex_rules.yaml          # TRACE-X 룰북 (19개 룰)
│
├── 📊 data/                         # 데이터
│   └── lists/                      # 블랙리스트/화이트리스트
│       ├── sdn_addresses.json     # OFAC SDN 리스트
│       ├── cex_addresses.json     # CEX 주소 리스트
│       └── bridge_contracts.json  # Bridge/Mixer 컨트랙트
│
├── 🧪 demo/                          # 데모 데이터 및 스크립트
│   ├── addresses.json              # 데모 주소 목록
│   ├── transactions/               # 데모 거래 데이터
│   └── demo_runner.py              # 데모 실행 스크립트
│
├── 🗄️ legacy/                       # GOG 관련 (보류)
│   └── ...                         # 기존 GOG 코드 및 데이터
│
└── 📚 docs/                         # 문서
    ├── API_DOCUMENTATION.md        # API 명세서
    ├── RULE_IMPLEMENTATION_STATUS.md # 룰 구현 현황
    ├── USER_SCENARIOS.md           # 사용자 시나리오
    └── ...
```

---

## 🚀 시작하기

### 1. 설치

```bash
# Python 3.10+ 필요
pip install -r requirements.txt
```

### 2. OFAC SDN 리스트 업데이트 (선택사항)

```bash
python scripts/update_sdn_list.py
```

### 3. 서버 실행

```bash
python api/app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

### 4. API 문서 확인

브라우저에서 `http://localhost:5000/api-docs` 접속 (Swagger UI)

---

## 📡 API 사용

### 주소 분석 (기본 스코어링)

```bash
POST /api/analyze/address
```

**Request:**

```json
{
  "address": "0xABC123...",
  "chain": "ethereum",
  "transactions": [...],
  "analysis_type": "basic"  // 기본값: "basic"
}
```

**Response:**

```json
{
  "target_address": "0xABC123...",
  "risk_score": 45,
  "risk_level": "medium",
  "risk_tags": ["mixer_inflow", "sanction_exposure"],
  "fired_rules": [
    { "rule_id": "C-001", "score": 30 },
    { "rule_id": "E-101", "score": 15 }
  ],
  "explanation": "..."
}
```

### 주소 분석 (심층 분석)

```bash
POST /api/analyze/address
```

**Request:**

```json
{
  "address": "0xABC123...",
  "chain": "ethereum",
  "transactions": [...],  // 3홉 데이터 포함 권장
  "analysis_type": "advanced"  // 심층 분석
}
```

**Response:**

```json
{
  "target_address": "0xABC123...",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "sanction_exposure", "layering_chain"],
  "fired_rules": [
    { "rule_id": "C-001", "score": 30 },
    { "rule_id": "E-101", "score": 15 },
    { "rule_id": "B-201", "score": 25 }, // 그래프 구조 분석 결과
    { "rule_id": "B-202", "score": 30 }
  ],
  "explanation": "..."
}
```

### 단일 트랜잭션 스코어링

```bash
POST /api/score/transaction
```

자세한 내용은 `docs/API_DOCUMENTATION.md` 참고

---

## 📊 TRACE-X 룰 구현 현황

**총 룰 수**: 19개

### ✅ 구현 완료 (11개)

#### Compliance (C) - 3개

- **C-001**: Sanction Direct Touch ✅
- **C-003**: High-Value Single Transfer ✅
- **C-004**: High-Value Repeated Transfer (24h) ✅

#### Exposure (E) - 2개

- **E-101**: Mixer Direct Exposure ✅
- **E-102**: Indirect Sanctions Exposure (PPR 기반) ✅

#### Behavior (B) - 6개

- **B-101**: Burst (10m) ✅
- **B-102**: Rapid Sequence (1m) ✅
- **B-103**: Inter-arrival Std High ✅
- **B-201**: Layering Chain (3홉 데이터 필요) ✅
- **B-202**: Cycle (3홉 데이터 필요) ✅
- **B-203**: Fan-out (10m bucket) ✅
- **B-204**: Fan-in (10m bucket) ✅

### 🚧 부분 구현 (2개)

- **C-002**: High-Risk Jurisdiction VASP (백엔드 데이터 필요)
- **E-103**: Counterparty Quality Risk (커스터마이징 항목, 백엔드 데이터 필요)

### ❌ 미구현 (4개)

- **B-401**: First 7 Days Burst (주소 상태 관리 필요)
- **B-402**: Reactivation (주소 상태 관리 필요)
- **B-501**: High-Value Buckets (동적 점수 할당 필요)
- **B-502**: Structuring Pattern (복합 집계 필요)

**자세한 내용**: `docs/RULE_IMPLEMENTATION_STATUS.md` 참고

---

## 🔧 주요 기능

### 1. 기본 스코어링 (빠름)

- 응답 시간: 1-2초
- 기본 룰만 평가 (B-201, B-202 제외)
- 실시간 탐지, 대시보드에 적합

### 2. 심층 분석 (느림)

- 응답 시간: 5-30초
- 모든 룰 평가 (B-201, B-202 포함)
- 수동 탐지, 상세 조사에 적합

### 3. 윈도우 기반 집계

- 시간 윈도우 내 거래 집계
- C-004, B-101, B-102 룰 지원

### 4. 버킷 기반 집계

- 시간 버킷으로 그룹화
- B-203, B-204 룰 지원

### 5. 그래프 구조 분석

- 3홉 데이터 기반 경로 탐색
- B-201 (Layering Chain), B-202 (Cycle) 룰 지원

### 6. PPR 연결성 분석

- Personalized PageRank 기반
- E-102 (Indirect Sanctions Exposure) 룰 지원

---

## 🤖 AI 활용 계획

### 1단계: 룰 가중치 학습 (우선순위: 높음)

- **목적**: 각 룰의 가중치를 학습하여 최적의 스코어 계산
- **방법**: 과거 데이터로 룰 조합과 실제 리스크의 상관관계 학습
- **활용 위치**: `core/aggregation/` 모듈

### 2단계: 룰 조합 최적화

- **목적**: 여러 룰이 동시에 발동될 때 최적의 점수 계산
- **방법**: 앙상블 학습 또는 메타 학습
- **활용 위치**: `core/scoring/engine.py`

### 3단계: 이상 패턴 탐지

- **목적**: 룰북에 없는 새로운 패턴 탐지
- **방법**: 비지도 학습 (클러스터링, 이상 탐지)
- **활용 위치**: `core/aggregation/` 모듈

### 4단계: 컨텍스트 기반 점수 조정

- **목적**: 주소의 컨텍스트(나이, 거래 패턴 등)를 고려한 점수 조정
- **방법**: 시계열 분석, 그래프 임베딩
- **활용 위치**: `core/scoring/address_analyzer.py`

**자세한 내용**: `docs/AI_INTEGRATION_PLAN.md` 참고

---

## 📋 앞으로 해야 할 것

### 우선순위 높음

1. **백엔드 연동**

   - 주소의 거래 히스토리 가져오기 API 연동
   - 3홉 거래 데이터 가져오기 (심층 분석용)

2. **주소 상태 관리 시스템**

   - 주소 메타데이터 저장소 구축
   - B-401, B-402 룰 구현

3. **동적 점수 할당**
   - 금액에 따른 동적 점수 계산
   - B-501 룰 구현

### 우선순위 중간

4. **복합 집계 로직**

   - 그룹화 및 그룹별 분석
   - B-502 룰 구현

5. **성능 최적화**
   - 그래프 분석 최적화
   - 캐싱 전략 수립

### 우선순위 낮음

6. **AI 통합**
   - 룰 가중치 학습
   - 이상 패턴 탐지

---

## 📚 문서

- **`docs/API_DOCUMENTATION.md`** - API 상세 명세
- **`docs/RULE_IMPLEMENTATION_STATUS.md`** - 룰 구현 현황
- **`docs/USER_SCENARIOS.md`** - 사용자 시나리오
- **`docs/PERFORMANCE_OPTIMIZATION.md`** - 성능 최적화 전략
- **`docs/THREE_HOP_IMPLEMENTATION.md`** - 3홉 데이터 기반 구현
- **`docs/AI_INTEGRATION_PLAN.md`** - AI 통합 계획

---

## 🔗 관련 레포지토리

- **프론트엔드**: https://github.com/paran-needless-to-say/frontend
- **백엔드**: (백엔드 팀 레포지토리)

---

## 📝 라이선스

MIT License

---

## 👥 기여

이 프로젝트는 CEX를 위한 AML 리스크 스코어링 시스템입니다.
