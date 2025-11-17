# 프로젝트 구조 재구성 가이드

## 📋 목표

- GOG 관련 파일을 `legacy/` 폴더로 분리 (보류 상태)
- 룰 베이스드 + AI 집계 구조로 재구성
- 백엔드 API 통합 준비

---

## 🔄 재구성 단계

### 1단계: 폴더 구조 생성

```bash
bash restructure.sh
```

이미 실행 완료되었습니다.

### 2단계: GOG 파일 이동

```bash
bash move_gog_to_legacy.sh
```

**이동되는 파일/폴더:**

- `multi_classification/graph_of_graph/` → `legacy/gog/`
- `link_prediction/graph_of_graph/` → `legacy/gog/`
- `fraud_detection/graph_of_graph/` → `legacy/gog/`
- `dataset/gog.py` → `legacy/dataset/`
- `dataset/get_deepwalk_embedding/` → `legacy/dataset/`
- `analysis/global.py` → `legacy/analysis/`
- `analysis/cross_chain_analysis.py` → `legacy/analysis/`
- `data/global_graph/` → `legacy/data/`
- `GoG/` → `legacy/gog_data/`

### 3단계: 데이터 파일 정리

```bash
# JSON 파일을 data/lists/로 복사
cp dataset/*.json data/lists/
```

### 4단계: Core 모듈 구현

✅ 완료:

- `core/scoring/engine.py` - 스코어링 엔진
- `core/rules/evaluator.py` - 룰 평가기
- `core/rules/loader.py` - 룰북 로더
- `core/data/lists.py` - 리스트 로더

### 5단계: API 구조 정리

✅ 완료:

- `api/app.py` - Flask 서버 (Blueprint 사용)
- `api/routes/scoring.py` - 스코어링 엔드포인트

---

## 📂 최종 구조

```
aml-risk-engine2/
│
├── 📡 api/                    # API 엔드포인트
│   ├── app.py                # Flask 서버
│   ├── routes/               # API 라우트
│   │   ├── __init__.py
│   │   └── scoring.py        # 스코어링 엔드포인트
│   └── test_scoring.py       # 테스트
│
├── 🧠 core/                   # 핵심 로직
│   ├── __init__.py
│   ├── scoring/              # 스코어링 엔진
│   │   ├── __init__.py
│   │   └── engine.py         # 메인 엔진
│   ├── rules/                # 룰 평가
│   │   ├── __init__.py
│   │   ├── evaluator.py      # 룰 평가기
│   │   └── loader.py         # 룰북 로더
│   ├── aggregation/          # AI 집계 (향후)
│   │   └── __init__.py
│   └── data/                 # 데이터 로더
│       ├── __init__.py
│       └── lists.py          # 리스트 관리
│
├── 📜 rules/                  # 룰북 정의
│   └── tracex_rules.yaml     # TRACE-X 룰북
│
├── 📊 data/                   # 데이터
│   └── lists/                 # 블랙리스트/화이트리스트
│       ├── sdn_addresses.json
│       ├── cex_addresses.json
│       └── bridge_contracts.json
│
├── 🗄️ legacy/                 # GOG 관련 (보류)
│   ├── README.md
│   ├── gog/                  # GOG 분석 코드
│   ├── analysis/             # 그래프 분석
│   ├── dataset/              # GOG 데이터셋 준비
│   └── data/                 # GOG 데이터
│
├── 📚 docs/                   # 문서
│   ├── API_SPEC.md
│   ├── SCORING_API.md
│   └── RESTRUCTURE_GUIDE.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🎯 주요 변경사항

### Before (기존)

- GOG와 룰 베이스드가 혼재
- `rules_engine.py`가 루트에 있음
- API가 단일 파일

### After (재구성)

- GOG는 `legacy/`로 분리
- Core 모듈로 구조화
- API는 Blueprint로 분리
- 룰북 기반 평가 + AI 집계 준비

---

## ✅ 체크리스트

- [x] 폴더 구조 생성
- [x] Core 모듈 구현
- [x] API 구조 정리
- [ ] GOG 파일 이동 (스크립트 실행 필요)
- [ ] 데이터 파일 이동 (완료)
- [ ] 테스트 실행
- [ ] GitHub에 푸시

---

## 🚀 다음 단계

1. `bash move_gog_to_legacy.sh` 실행
2. 테스트 실행: `python api/test_scoring.py`
3. 서버 실행: `python api/app.py`
4. GitHub에 푸시
