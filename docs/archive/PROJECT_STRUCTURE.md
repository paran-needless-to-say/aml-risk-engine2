# 프로젝트 구조

## 📁 현재 프로젝트 구조

```
Cryptocurrency-Graphs-of-graphs/
│
├── 📡 api/                          # API 서버
│   ├── app.py                      # Flask 서버 메인
│   ├── routes/                     # API 라우트
│   │   ├── scoring.py              # POST /api/score/transaction
│   │   └── address_analysis.py     # POST /api/analyze/address
│   └── test_*.py                   # API 테스트
│
├── 🧠 core/                         # 핵심 로직
│   ├── scoring/                    # 스코어링 엔진
│   │   ├── engine.py               # 단일 트랜잭션 스코어링
│   │   ├── address_analyzer.py     # 주소 기반 분석
│   │   ├── ai_weight_learner.py    # AI 가중치 학습
│   │   ├── dataset_builder.py      # 데이터셋 구축
│   │   └── real_dataset_builder.py # 실제 데이터 수집
│   │
│   ├── rules/                      # 룰 평가
│   │   ├── evaluator.py            # 룰 평가기
│   │   └── loader.py               # 룰북 로더
│   │
│   ├── aggregation/                # 집계 모듈
│   │   ├── window.py               # 윈도우 기반 집계
│   │   ├── bucket.py               # 버킷 기반 집계
│   │   ├── topology.py             # 그래프 구조 분석
│   │   ├── ppr_connector.py        # PPR 연결성 분석
│   │   ├── stats.py                # 통계 계산
│   │   └── mpocryptml_patterns.py  # MPOCryptoML 패턴 탐지
│   │
│   └── data/                       # 데이터 로더
│       ├── lists.py                # 리스트 관리
│       └── etherscan_client.py     # Etherscan API 클라이언트
│
├── 📜 rules/                        # 룰북 정의
│   └── tracex_rules.yaml           # TRACE-X 룰북
│
├── 📊 data/                         # 데이터
│   ├── lists/                      # 블랙리스트/화이트리스트
│   │   ├── sdn_addresses.json     # OFAC SDN 리스트
│   │   ├── cex_addresses.json     # CEX 주소 리스트
│   │   └── bridge_contracts.json  # Bridge 컨트랙트
│   ├── dataset/                    # 학습 데이터셋
│   │   └── real_balanced.json     # 수집된 데이터
│   └── cache/                      # 캐시 (자동 생성)
│
├── 🧪 demo/                          # 데모 데이터
│   ├── transactions/               # 데모 거래 데이터
│   └── demo_runner.py              # 데모 실행 스크립트
│
├── 🔧 scripts/                      # 유틸리티 스크립트
│   ├── collect_real_data.py        # 실제 데이터 수집
│   ├── split_dataset.py            # 데이터셋 분할
│   ├── train_ai_model.py            # AI 모델 학습
│   ├── check_data_status.py        # 데이터 상태 확인
│   └── update_sdn_list.py          # SDN 리스트 업데이트
│
├── 📚 docs/                         # 문서 (18개)
│   ├── README.md                   # 문서 가이드
│   ├── IMPLEMENTED_RULES_SUMMARY.md
│   ├── AI_WEIGHT_LEARNING.md
│   └── ...
│
├── 🗄️ legacy/                       # 레거시 코드 (보관용)
│   ├── fraud_detection/            # 사기 탐지 (레거시)
│   ├── multi_classification/       # 다중 분류 (레거시)
│   ├── link_prediction/            # 링크 예측 (레거시)
│   └── ...
│
├── run_server.py                    # 서버 실행 스크립트
├── requirements.txt                 # Python 의존성
└── README.md                        # 프로젝트 개요
```

---

## ✅ 핵심 파일 (필수)

### API 서버

- `api/app.py` - Flask 서버
- `api/routes/scoring.py` - 트랜잭션 스코어링 API
- `api/routes/address_analysis.py` - 주소 분석 API

### 스코어링 엔진

- `core/scoring/engine.py` - 단일 트랜잭션 스코어링
- `core/scoring/address_analyzer.py` - 주소 기반 분석
- `core/rules/evaluator.py` - 룰 평가기
- `core/rules/loader.py` - 룰북 로더

### 집계 모듈

- `core/aggregation/window.py` - 윈도우 집계
- `core/aggregation/bucket.py` - 버킷 집계
- `core/aggregation/topology.py` - 그래프 분석
- `core/aggregation/stats.py` - 통계 계산
- `core/aggregation/ppr_connector.py` - PPR 분석

### 데이터

- `core/data/lists.py` - 리스트 관리
- `core/data/etherscan_client.py` - Etherscan API
- `rules/tracex_rules.yaml` - 룰북

---

## 🗑️ 정리 완료

### 1. 미사용 모듈 제거 ✅

- `core/aggregation/temporal_patterns.py` - 삭제 완료
- `core/aggregation/__init__.py` - import 제거 완료

### 2. 빈 디렉토리 정리 ✅

- `demo/scenarios/` - 빈 디렉토리 삭제 완료

### 3. 문서 정리 ✅

- `docs/` - 47개 → 18개로 정리 완료 (이전 작업)

### 4. 프로젝트 구조 문서화 ✅

- `PROJECT_STRUCTURE.md` - 생성 완료
- `README.md` - 프로젝트 구조 업데이트 완료

### 5. 캐시 파일 정리 ✅

- `__pycache__/` 디렉토리 정리 완료
- `*.pyc` 파일 정리 완료

---

## 📋 유지되는 파일

### 설정 파일 (유지)

- `PORT_CONFLICT.md` - 포트 충돌 해결 가이드 (유용)
- `SETUP_BACKEND.md` - 백엔드 설정 가이드 (유용)

### 레거시 파일 (보관용)

- `legacy/` - 레거시 코드 및 데이터 (보관용, 삭제하지 않음)
- `MPOCryptoML.pdf` - 참고 논문 (보관용)

---

## ✅ 정리 결과

- **미사용 모듈**: 1개 제거
- **빈 디렉토리**: 1개 제거
- **캐시 파일**: 정리 완료
- **문서**: 이미 정리 완료 (47개 → 18개)
- **프로젝트 구조**: 문서화 완료
