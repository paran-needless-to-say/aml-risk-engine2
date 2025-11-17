# 🏗️ AML Risk Engine 프로젝트 구조 (재구성)

## 📋 목표

- **룰 베이스드 + AI 집계** 방식의 AML 스코어링 엔진
- GOG 관련 파일은 별도 폴더로 분리 (보류 상태)
- 백엔드 API 통합 준비

---

## 📂 제안하는 새로운 구조

```
aml-risk-engine2/
│
├── 📡 api/                          # API 엔드포인트
│   ├── app.py                       # Flask/FastAPI 서버
│   ├── score_transaction.py        # 트랜잭션 스코어링 API
│   ├── routes/                      # API 라우트
│   │   ├── __init__.py
│   │   ├── scoring.py              # 스코어링 엔드포인트
│   │   └── health.py                # 헬스체크
│   └── test_scoring.py              # 테스트
│
├── 🧠 core/                         # 핵심 로직
│   ├── __init__.py
│   ├── scoring/                     # 스코어링 엔진
│   │   ├── __init__.py
│   │   ├── engine.py                # 메인 스코어링 엔진
│   │   ├── risk_calculator.py       # 리스크 점수 계산
│   │   └── level_determiner.py      # Risk Level 결정
│   │
│   ├── rules/                       # 룰 평가
│   │   ├── __init__.py
│   │   ├── evaluator.py             # 룰 평가기
│   │   ├── matcher.py               # 조건 매칭
│   │   └── rule_loader.py            # 룰북 로더
│   │
│   ├── aggregation/                 # AI 집계 (향후)
│   │   ├── __init__.py
│   │   ├── aggregator.py            # 집계 로직
│   │   └── model.py                 # AI 모델 (보류)
│   │
│   └── data/                        # 데이터 처리
│       ├── __init__.py
│       ├── lists.py                 # SDN, CEX, Mixer 리스트 로더
│       └── transformers.py          # 데이터 변환
│
├── 📜 rules/                        # 룰북 정의
│   ├── tracex_rules.yaml            # TRACE-X 룰북
│   └── custom_rules.yaml            # 커스텀 룰 (선택)
│
├── 📊 data/                         # 데이터 (필요시)
│   ├── lists/                       # 블랙리스트/화이트리스트
│   │   ├── sdn_addresses.json
│   │   ├── cex_addresses.json
│   │   ├── bridge_contracts.json
│   │   └── mixer_addresses.json
│   └── cache/                       # 캐시 데이터
│
├── 🧪 tests/                         # 테스트
│   ├── __init__.py
│   ├── test_scoring.py
│   ├── test_rules.py
│   └── fixtures/                    # 테스트 데이터
│
├── 📚 docs/                         # 문서
│   ├── API_SPEC.md
│   ├── SCORING_API.md
│   └── RULES.md
│
├── 🔧 scripts/                      # 유틸리티 스크립트
│   ├── build_lists.py               # 리스트 빌드
│   └── precompute_hops.py          # SDN hop 계산
│
├── 🗄️ legacy/                       # GOG 관련 (보류)
│   ├── README.md                    # GOG 관련 설명
│   ├── gog/                         # GOG 분석 코드
│   │   ├── multi_classification/
│   │   ├── link_prediction/
│   │   └── fraud_detection/
│   ├── analysis/                    # 그래프 분석
│   │   ├── global.py
│   │   └── cross_chain_analysis.py
│   ├── dataset/                    # GOG 데이터셋 준비
│   │   ├── gog.py
│   │   └── get_deepwalk_embedding/
│   └── data/                        # GOG 데이터
│       └── global_graph/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔄 마이그레이션 계획

### 1단계: GOG 파일 분리

```bash
# GOG 관련 폴더 생성
mkdir -p legacy/gog
mkdir -p legacy/analysis
mkdir -p legacy/dataset
mkdir -p legacy/data

# 이동할 파일들
mv multi_classification/graph_of_graph legacy/gog/
mv link_prediction/graph_of_graph legacy/gog/
mv fraud_detection/graph_of_graph legacy/gog/
mv analysis/global.py legacy/analysis/
mv analysis/cross_chain_analysis.py legacy/analysis/
mv dataset/gog.py legacy/dataset/
mv dataset/get_deepwalk_embedding legacy/dataset/
mv data/global_graph legacy/data/
```

### 2단계: Core 구조 생성

```bash
mkdir -p core/scoring
mkdir -p core/rules
mkdir -p core/aggregation
mkdir -p core/data
```

### 3단계: 파일 재구성

- `rules_engine.py` → `core/rules/evaluator.py`
- `api/score_transaction.py` → `core/scoring/engine.py` + `api/routes/scoring.py`
- `dataset/*.json` → `data/lists/`
- `scripts/` → 유지 (리스트 빌드용)

---

## 📝 주요 모듈 설명

### `core/scoring/engine.py`

- 백엔드 JSON을 받아서 스코어링 수행
- 룰 평가 + AI 집계 (향후)

### `core/rules/evaluator.py`

- 룰북 기반 룰 평가
- TRACE-X 룰 적용

### `core/aggregation/aggregator.py`

- 여러 트랜잭션의 스코어를 집계
- AI 모델 활용 (향후)

### `api/routes/scoring.py`

- REST API 엔드포인트
- Request/Response 처리

---

## 🎯 다음 단계

1. ✅ 구조 설계 완료
2. ⏳ 파일 이동 및 재구성
3. ⏳ Core 모듈 구현
4. ⏳ API 통합
5. ⏳ 테스트 작성
