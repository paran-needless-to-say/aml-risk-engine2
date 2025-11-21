# AML Risk Engine

CEX를 위한 주소 추적 및 리스크 스코어링 시스템

룰 베이스드 + AI 집계 방식의 AML (Anti-Money Laundering) 스코어링 엔진

---

## 프로젝트 개요

이 프로젝트는 중앙화 거래소(CEX)를 위한 AML 리스크 스코어링 시스템입니다. 블록체인 주소의 거래 히스토리를 분석하여 리스크를 평가하고, TRACE-X 룰북 기반으로 점수를 계산합니다.

### 주요 기능

- **주소 기반 리스크 분석**: 주소의 거래 히스토리를 분석하여 리스크 스코어 계산
- **2가지 분석 모드**:
  - **기본 모드 (1-hop)**: 빠른 응답 (1-2초), 실시간 대시보드 적합
  - **Multi-hop 모드 (3-hop)**: 정밀 분석 (3-8초), 복잡한 패턴 탐지 (정확도 30-50% 향상)
- **TRACE-X 룰북 기반**: Compliance, Exposure, Behavior 3축 룰 평가
- **그래프 패턴 탐지**: Layering Chain, Cycle, Fan-in/Fan-out 등
- **OFAC SDN 리스트 통합**: 제재 대상 주소 자동 탐지

> 💡 **Multi-hop 모드 권장**: 복잡한 세탁 패턴 탐지를 위해 Multi-hop 모드 사용을 권장합니다. 자세한 내용은 `docs/FINAL_API_SPEC.md` 참고.

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

리스크 스코어링 API는 **2가지 모드**를 지원합니다:

#### 옵션 A: 기본 모드 (1-hop, 빠름)

**프론트엔드가 `transactions` 제공 (기존 방식)**:

```json
POST /api/analyze/address

{
  "address": "0xhigh_risk_mixer_sanctioned",
  "chain_id": 1,
  "transactions": [
    {
      "tx_hash": "0xtx1_mixer",
      "chain_id": 1,
      "timestamp": "2025-11-15T00:27:17.865209Z",
      "block_height": 1000,
      "target_address": "0xhigh_risk_mixer_sanctioned",
      "counterparty_address": "0xmixer_service_123",
      "label": "mixer",
      "is_sanctioned": false,
      "is_known_scam": false,
      "is_mixer": true,
      "is_bridge": false,
      "amount_usd": 5000.0,
      "asset_contract": "0xETH"
    },
    {
      "tx_hash": "0xtx2_sanctioned",
      "chain_id": 1,
      "timestamp": "2024-01-01T10:30:00Z",
      "block_height": 1001,
      "target_address": "0xhigh_risk_mixer_sanctioned",
      "counterparty_address": "0xsanctioned_address_ofac",
      "label": "unknown",
      "is_sanctioned": true,
      "is_known_scam": false,
      "is_mixer": false,
      "is_bridge": false,
      "amount_usd": 3000.0,
      "asset_contract": "0xETH"
    }
  ],
  "analysis_type": "basic"
}
```

**특징**:

- ✅ 응답 시간: 1-2초
- ✅ 실시간 대시보드에 적합
- ⚠️ 1-hop 분석만 가능 (단순 패턴만 탐지)

---

#### 옵션 B: Multi-hop 모드 (3-hop, 정밀) ⭐️ 권장

**백엔드가 `transactions` 자동 수집 (신규 방식)**:

```json
POST /api/analyze/address

{
  "address": "0xhigh_risk_mixer_sanctioned",
  "chain_id": 1,
  "max_hops": 3,
  "analysis_type": "advanced",
  "time_window_hours": 24
}
```

**특징**:

- ✅ 응답 시간: 3-8초 (캐싱 시)
- ✅ 복잡한 세탁 패턴 탐지 (Layering Chain, Cycle)
- ✅ 정확도 30-50% 향상
- ✅ 그래프 구조 분석 (B-201, B-202 룰 활성화)
- ⚠️ 백엔드 구현 필요 (Multi-hop 수집)

**응답 예시**:

```json
{
  "target_address": "0xhigh_risk_mixer_sanctioned",
  "risk_score": 98,
  "risk_level": "critical",
  "risk_tags": [
    "mixer_inflow",
    "sanction_exposure",
    "high_value_transfer",
    "suspicious_pattern"
  ],
  "fired_rules": [
    { "rule_id": "E-101", "score": 32 },
    { "rule_id": "C-001", "score": 30 },
    { "rule_id": "C-003", "score": 25 },
    { "rule_id": "C-004", "score": 20 },
    { "rule_id": "B-101", "score": 15 },
    { "rule_id": "B-501", "score": 6 }
  ],
  "explanation": "Mixer Direct Exposure 패턴 감지, Sanction Direct Touch 패턴 감지...",
  "completed_at": "2025-11-20T16:59:08Z",
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
  "tx_hash": "0xtx1_mixer",
  "chain_id": 1,
  "timestamp": "2025-11-15T00:27:17.865209Z",
  "block_height": 1000,
  "target_address": "0xhigh_risk_mixer_sanctioned",
  "counterparty_address": "0xmixer_service_123",
  "label": "mixer",
  "is_sanctioned": false,
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
  "target_address": "0xhigh_risk_mixer_sanctioned",
  "risk_score": 100,
  "risk_level": "critical",
  "risk_tags": ["mixer_inflow", "high_value_transfer"],
  "fired_rules": [
    { "rule_id": "E-101", "score": 32 },
    { "rule_id": "C-003", "score": 25 },
    { "rule_id": "C-004", "score": 20 },
    { "rule_id": "B-101", "score": 15 },
    { "rule_id": "B-501", "score": 6 }
  ],
  "explanation": "1-hop sanctioned mixer에서 5,000USD 이상 유입...",
  "completed_at": "2025-11-20T16:59:19Z",
  "timestamp": "2025-11-15T00:27:17.865209Z",
  "chain_id": 1,
  "value": 5000.0
}
```

### 필수 파라미터

| 파라미터   | 타입    | 설명                           |
| ---------- | ------- | ------------------------------ |
| `address`  | string  | 분석 대상 주소                 |
| `chain_id` | integer | 체인 ID (숫자, 예: 1=Ethereum) |

### 선택 파라미터

| 파라미터            | 타입    | 기본값  | 설명                              |
| ------------------- | ------- | ------- | --------------------------------- |
| `transactions`      | array   | -       | 거래 히스토리 (옵션 A에서 필수)   |
| `max_hops`          | integer | 1       | 최대 홉 수 (1~3, 옵션 B에서 필수) |
| `analysis_type`     | string  | "basic" | "basic" 또는 "advanced"           |
| `time_window_hours` | integer | -       | 최근 N시간 거래만 수집            |
| `time_range`        | object  | -       | 시간 범위 필터                    |

### 거래 데이터 구조 (옵션 A)

```json
{
  "tx_hash": "0x123...",
  "chain_id": 1,
  "timestamp": "2025-11-17T12:34:56Z",
  "block_height": 21039493,
  "target_address": "0xTarget",
  "counterparty_address": "0xMixer1",
  "label": "mixer",
  "is_sanctioned": false,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 5000.0,
  "asset_contract": "0xETH"
}
```

### 중요 사항

1. **chain_id는 숫자**: `1` (Ethereum), `42161` (Arbitrum), `43114` (Avalanche) 등
2. **2가지 모드 지원**:
   - **기본 모드**: `transactions` 제공 (빠름, 1-2초)
   - **Multi-hop 모드**: `max_hops` 제공, 백엔드가 수집 (정밀, 3-8초)
3. **Multi-hop 장점**: 복잡한 세탁 패턴 탐지 (Layering Chain, Cycle), 정확도 30-50% 향상

자세한 내용은 다음 문서를 참고하세요:

- `docs/FINAL_API_SPEC.md` - 최종 API 스펙 (Multi-hop 지원)
- `docs/CORRECT_INPUT_FORMAT.md` - 올바른 입력 포맷
- `docs/MULTI_HOP_REQUIREMENT.md` - Multi-hop 요구사항

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

- **FINAL_API_SPEC.md** ⭐️ - 최종 API 스펙 (Multi-hop 지원)
- **QUICK_START_MULTIHOP.md** - Multi-hop 빠른 시작 가이드
- **API_DOCUMENTATION.md** - 전체 API 문서
- **RISK_SCORING_IO.md** - 리스크 스코어링 엔진 입출력 명세
- **CORRECT_INPUT_FORMAT.md** - 올바른 입력 포맷 가이드
- **DEPLOYMENT_GUIDE.md** - 배포 가이드 (백엔드 팀용)
- **QUICK_TEST_GUIDE.md** - 빠른 테스트 가이드

### Multi-Hop 관련 문서 (백엔드 팀용)

- **MULTI_HOP_REQUIREMENT.md** - Multi-hop 요구사항 (상세)
- **BACKEND_REQUEST_MULTI_HOP.md** - 백엔드 구현 가이드
- **SIMPLE_COMPARISON_1HOP_VS_MULTIHOP.md** - 1-hop vs Multi-hop 비교
- **ELEVATOR_PITCH_MULTIHOP.md** - 엘리베이터 피치 (30초 요약)
- **PARAMETER_CHANGES_SUMMARY.md** - 파라미터 변경 요약

### 논문

- **PAPER_KR.md** - 논문 (한국어)
- **PAPER.md** - 논문 (영어)

### 프로젝트 소개

- **PROJECT_INTRODUCTION.md** - 프로젝트 상세 소개
- **SYSTEM_OVERVIEW.md** - 시스템 개요 및 아키텍처

모든 문서는 `docs/` 폴더에 있습니다. `docs/README.md`에서 문서 가이드를 확인할 수 있습니다.

---

## 체인 ID 매핑

| Chain ID | 체인 이름         |
| -------- | ----------------- |
| 1        | Ethereum Mainnet  |
| 42161    | Arbitrum One      |
| 43114    | Avalanche C-Chain |
| 8453     | Base Mainnet      |
| 137      | Polygon Mainnet   |
| 56       | BSC Mainnet       |
| 250      | Fantom Opera      |
| 10       | Optimism Mainnet  |
| 81457    | Blast Mainnet     |

---

## 라이선스

MIT License

---

## 기여

이 프로젝트는 CEX를 위한 AML 리스크 스코어링 시스템입니다.
