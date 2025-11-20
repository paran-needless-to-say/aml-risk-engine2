# AML Risk Engine

CEX를 위한 주소 추적 및 리스크 스코어링 시스템

룰 베이스드 + AI 집계 방식의 AML (Anti-Money Laundering) 스코어링 엔진

---

## 프로젝트 개요

이 프로젝트는 중앙화 거래소(CEX)를 위한 AML 리스크 스코어링 시스템입니다. 블록체인 주소의 거래 히스토리를 분석하여 리스크를 평가하고, TRACE-X 룰북 기반으로 점수를 계산합니다.

### 주요 기능

- 주소 기반 리스크 분석: 주소의 거래 히스토리를 분석하여 리스크 스코어 계산
- 기본 스코어링: 빠른 응답 (1-2초), 기본 룰만 평가
- 심층 분석: 느린 응답 (5-30초), 모든 룰 평가 (그래프 구조 분석 포함)
- TRACE-X 룰북 기반: Compliance, Exposure, Behavior 3축 룰 평가
- OFAC SDN 리스트 통합: 제재 대상 주소 자동 탐지

---

## 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/paran-needless-to-say/aml-risk-engine2.git
cd aml-risk-engine2
```

### 2. 의존성 설치

```bash
# Python 3.10+ 필요
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python3 run_server.py
```

서버가 `http://localhost:5001` 또는 `http://localhost:5002`에서 실행됩니다.

### 4. API 문서 확인

브라우저에서 `http://localhost:5001/api-docs` 접속 (Swagger UI)

---

## API 사용

### 주소 분석 API

**엔드포인트**: `POST /api/analyze/address`

**요청 예시**:

```json
{
  "address": "0xabc123...",
  "chain_id": 1,
  "transactions": [
    {
      "tx_hash": "0x123...",
      "chain_id": 1,
      "timestamp": "2025-11-17T12:34:56Z",
      "block_height": 21039493,
      "target_address": "0xabc123...",
      "counterparty_address": "0xdef456...",
      "label": "mixer",
      "is_sanctioned": true,
      "is_known_scam": false,
      "is_mixer": true,
      "is_bridge": false,
      "amount_usd": 5000.0,
      "asset_contract": "0xETH"
    }
  ],
  "analysis_type": "basic"
}
```

**응답 예시**:

```json
{
  "target_address": "0xabc123...",
  "risk_score": 98,
  "risk_level": "critical",
  "risk_tags": ["mixer_inflow", "sanction_exposure", "high_value_transfer"],
  "fired_rules": [
    {"rule_id": "E-101", "score": 32},
    {"rule_id": "C-001", "score": 30},
    {"rule_id": "C-003", "score": 25}
  ],
  "explanation": "...",
  "completed_at": "2025-11-20T16:32:47Z",
  "timestamp": "2025-11-15T00:57:17.865209Z",
  "chain_id": 1,
  "value": 16000.0
}
```

### 단일 트랜잭션 스코어링 API

**엔드포인트**: `POST /api/score/transaction`

**요청 예시**:

```json
{
  "tx_hash": "0x123...",
  "chain_id": 1,
  "timestamp": "2025-11-17T12:34:56Z",
  "block_height": 21039493,
  "target_address": "0xabc123...",
  "counterparty_address": "0xdef456...",
  "label": "mixer",
  "is_sanctioned": true,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 5000.0,
  "asset_contract": "0xETH"
}
```

**응답 예시**:

```json
{
  "target_address": "0xabc123...",
  "risk_score": 100,
  "risk_level": "critical",
  "risk_tags": ["mixer_inflow", "high_value_transfer"],
  "fired_rules": [
    {"rule_id": "E-101", "score": 32},
    {"rule_id": "C-003", "score": 25}
  ],
  "explanation": "...",
  "completed_at": "2025-11-20T16:32:47Z",
  "timestamp": "2025-11-17T12:34:56Z",
  "chain_id": 1,
  "value": 5000.0
}
```

### 중요 사항

1. **chain_id는 숫자 형식**: `1` (Ethereum), `42161` (Arbitrum), `43114` (Avalanche) 등
2. **transactions 배열 내부도 chain_id 숫자**: 각 트랜잭션 객체에도 `chain_id`가 필요하며 숫자 형식이어야 합니다
3. **필수 필드**: `address`, `chain_id`, `transactions` (주소 분석 API의 경우)
4. **선택 필드**: `analysis_type` (기본값: "basic"), `time_range`

자세한 내용은 `docs/API_DOCUMENTATION.md`와 `docs/CORRECT_INPUT_FORMAT.md`를 참고하세요.

---

## 프로젝트 구조

```
Cryptocurrency-Graphs-of-graphs/
│
├── api/                          # API 서버
│   ├── app.py                    # Flask 서버 메인
│   └── routes/                   # API 라우트
│       ├── scoring.py            # 단일 트랜잭션 스코어링
│       └── address_analysis.py  # 주소 분석
│
├── core/                         # 핵심 로직
│   ├── scoring/                  # 스코어링 엔진
│   │   ├── engine.py             # 단일 트랜잭션 스코어링
│   │   └── address_analyzer.py   # 주소 기반 분석
│   ├── rules/                    # 룰 평가
│   │   ├── evaluator.py          # 룰 평가기
│   │   └── loader.py             # 룰북 로더
│   ├── aggregation/              # 집계 모듈
│   │   ├── window.py             # 윈도우 기반 집계
│   │   ├── bucket.py             # 버킷 기반 집계
│   │   └── topology.py           # 그래프 구조 분석
│   └── data/                     # 데이터 로더
│       └── lists.py              # 리스트 관리
│
├── rules/                        # 룰북 정의
│   └── tracex_rules.yaml         # TRACE-X 룰북
│
├── data/                         # 데이터
│   ├── lists/                    # 블랙리스트/화이트리스트
│   │   ├── sdn_addresses.json    # OFAC SDN 리스트
│   │   └── cex_addresses.json    # CEX 주소 리스트
│   └── cache/                    # 캐시 (자동 생성)
│
├── docs/                         # 문서
│   ├── API_DOCUMENTATION.md      # API 상세 명세
│   ├── RISK_SCORING_IO.md        # 입출력 명세
│   ├── DEPLOYMENT_GUIDE.md       # 배포 가이드
│   └── examples/                 # API 테스트 예시
│
├── run_server.py                 # 서버 실행 스크립트
├── requirements.txt              # Python 의존성
└── README.md                     # 프로젝트 개요
```

---

## 주요 기능

### 1. 기본 스코어링 (빠름)

- 응답 시간: 1-2초
- 기본 룰만 평가
- 실시간 탐지, 대시보드에 적합
- `analysis_type: "basic"` 사용

### 2. 심층 분석 (느림)

- 응답 시간: 5-30초
- 모든 룰 평가 (그래프 구조 분석 포함)
- 수동 탐지, 상세 조사에 적합
- `analysis_type: "advanced"` 사용

### 3. TRACE-X 룰북 기반 평가

- Compliance (C): 제재, 고액 거래 관련 룰
- Exposure (E): Mixer, 제재 주소 노출 관련 룰
- Behavior (B): 거래 패턴, 그래프 구조 관련 룰

---

## 테스트

### Swagger UI 사용

1. 서버 실행: `python3 run_server.py`
2. 브라우저에서 `http://localhost:5001/api-docs` 접속
3. "Try it out" 버튼으로 API 테스트

### curl 사용

```bash
# 주소 분석
curl -X POST http://localhost:5001/api/analyze/address \
  -H "Content-Type: application/json" \
  -d @docs/examples/test_api.json

# 단일 트랜잭션 스코어링
curl -X POST http://localhost:5001/api/score/transaction \
  -H "Content-Type: application/json" \
  -d @docs/examples/test_single_transaction.json
```

### 테스트 예시 파일

- `docs/examples/test_api.json` - 주소 분석 테스트용
- `docs/examples/test_single_transaction.json` - 단일 트랜잭션 테스트용

자세한 테스트 방법은 `docs/QUICK_TEST_GUIDE.md`를 참고하세요.

---

## 문서

### 핵심 문서

- **API_DOCUMENTATION.md** - 전체 API 문서
- **RISK_SCORING_IO.md** - 리스크 스코어링 엔진 입출력 명세
- **DEPLOYMENT_GUIDE.md** - 배포 가이드 (백엔드 팀용)
- **CORRECT_INPUT_FORMAT.md** - 올바른 입력 포맷 가이드
- **QUICK_TEST_GUIDE.md** - 빠른 테스트 가이드

### 논문

- **PAPER_KR.md** - 논문 (한국어)
- **PAPER.md** - 논문 (영어)

### 프로젝트 소개

- **PROJECT_INTRODUCTION.md** - 프로젝트 상세 소개
- **SYSTEM_OVERVIEW.md** - 시스템 개요 및 아키텍처

모든 문서는 `docs/` 폴더에 있습니다. `docs/README.md`에서 문서 가이드를 확인할 수 있습니다.

---

## 체인 ID 매핑

| Chain ID | 체인 이름 |
|----------|----------|
| 1 | Ethereum Mainnet |
| 42161 | Arbitrum One |
| 43114 | Avalanche C-Chain |
| 8453 | Base Mainnet |
| 137 | Polygon Mainnet |
| 56 | BSC Mainnet |
| 250 | Fantom Opera |
| 10 | Optimism Mainnet |
| 81457 | Blast Mainnet |

---

## 라이선스

MIT License

---

## 기여

이 프로젝트는 CEX를 위한 AML 리스크 스코어링 시스템입니다.
