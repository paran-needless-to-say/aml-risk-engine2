# 📁 프로젝트 구조 요약

## 🎯 목표

**룰 베이스드 + AI 집계** 방식의 AML 스코어링 엔진

- ✅ 룰 베이스드: TRACE-X 룰북 기반
- ⏳ AI 집계: 향후 구현 예정
- 🗄️ GOG 관련: `legacy/` 폴더로 분리 (보류)

---

## 📂 최종 구조

```
aml-risk-engine2/
│
├── 📡 api/                          # API 엔드포인트
│   ├── app.py                      # Flask 서버
│   ├── routes/
│   │   ├── __init__.py
│   │   └── scoring.py              # POST /api/score/transaction
│   └── test_scoring.py
│
├── 🧠 core/                         # 핵심 로직
│   ├── __init__.py
│   ├── scoring/                    # 스코어링 엔진
│   │   ├── __init__.py
│   │   └── engine.py               # TransactionScorer
│   ├── rules/                      # 룰 평가
│   │   ├── __init__.py
│   │   ├── evaluator.py            # RuleEvaluator (TRACE-X 룰북)
│   │   └── loader.py               # RuleLoader
│   ├── aggregation/                # AI 집계 (향후)
│   │   └── __init__.py
│   └── data/                       # 데이터 로더
│       ├── __init__.py
│       └── lists.py                # SDN, CEX, Mixer 리스트
│
├── 📜 rules/                        # 룰북 정의
│   └── tracex_rules.yaml           # TRACE-X 룰북
│
├── 📊 data/                         # 데이터
│   └── lists/                      # 블랙리스트/화이트리스트
│       ├── sdn_addresses.json
│       ├── cex_addresses.json
│       └── bridge_contracts.json
│
├── 🗄️ legacy/                       # GOG 관련 (보류)
│   ├── README.md
│   ├── gog/                        # GOG 분석 코드
│   ├── analysis/                   # 그래프 분석
│   ├── dataset/                    # GOG 데이터셋 준비
│   └── data/                       # GOG 데이터
│
├── 📚 docs/                         # 문서
│   ├── API_SPEC.md
│   ├── SCORING_API.md
│   ├── NEW_PROJECT_STRUCTURE.md
│   └── RESTRUCTURE_GUIDE.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔄 데이터 흐름

```
백엔드 JSON
    ↓
api/routes/scoring.py
    ↓
core/scoring/engine.py (TransactionScorer)
    ↓
core/rules/evaluator.py (RuleEvaluator)
    ↓
rules/tracex_rules.yaml (룰북)
    ↓
core/data/lists.py (SDN, CEX, Mixer 리스트)
    ↓
스코어링 결과 반환
```

---

## 📝 주요 모듈

### `core/scoring/engine.py`

- `TransactionScorer`: 메인 스코어링 엔진
- 백엔드 JSON → 스코어링 결과 변환

### `core/rules/evaluator.py`

- `RuleEvaluator`: TRACE-X 룰북 기반 룰 평가
- 단일 트랜잭션에 대한 룰 평가

### `core/rules/loader.py`

- `RuleLoader`: 룰북 YAML 파일 로드

### `core/data/lists.py`

- `ListLoader`: SDN, CEX, Mixer 리스트 관리

---

## 🚀 사용 방법

### 1. 서버 실행

```bash
python api/app.py
```

### 2. API 호출

```bash
curl -X POST http://localhost:5000/api/score/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0x...",
    "chain": "ethereum",
    ...
  }'
```

---

## ✅ 다음 단계

1. `bash move_gog_to_legacy.sh` 실행 (GOG 파일 이동)
2. 테스트 실행
3. GitHub에 푸시: `https://github.com/paran-needless-to-say/aml-risk-engine2.git`
