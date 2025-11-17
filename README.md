# AML Risk Engine

룰 베이스드 + AI 집계 방식의 AML (Anti-Money Laundering) 스코어링 엔진

## 📋 프로젝트 구조

```
aml-risk-engine2/
│
├── 📡 api/                    # API 엔드포인트
│   ├── app.py                # Flask 서버
│   ├── routes/               # API 라우트
│   │   └── scoring.py        # 스코어링 엔드포인트
│   └── test_scoring.py       # 테스트
│
├── 🧠 core/                   # 핵심 로직
│   ├── scoring/              # 스코어링 엔진
│   │   └── engine.py         # 메인 엔진
│   ├── rules/                # 룰 평가
│   │   ├── evaluator.py      # 룰 평가기
│   │   └── loader.py         # 룰북 로더
│   ├── aggregation/          # AI 집계 (향후)
│   └── data/                 # 데이터 로더
│       └── lists.py          # 리스트 관리
│
├── 📜 rules/                  # 룰북 정의
│   └── tracex_rules.yaml     # TRACE-X 룰북
│
├── 📊 data/                   # 데이터
│   └── lists/                 # 블랙리스트/화이트리스트
│
├── 🗄️ legacy/                 # GOG 관련 (보류)
│   └── README.md             # GOG 설명
│
└── 📚 docs/                   # 문서
```

## 🚀 시작하기

### 설치

```bash
pip install -r requirements.txt
```

### 서버 실행

```bash
python api/app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## 📡 API 사용

### 트랜잭션 스코어링

```bash
POST /api/score/transaction
```

**Request:**

```json
{
  "tx_hash": "0x...",
  "chain": "ethereum",
  "timestamp": "2025-11-17T12:34:56Z",
  "block_height": 21039493,
  "target_address": "0x...",
  "counterparty_address": "0x...",
  "entity_type": "mixer",
  "is_sanctioned": true,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 1234.56,
  "asset_contract": "0x..."
}
```

**Response:**

```json
{
  "target_address": "0x...",
  "risk_score": 78.0,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "sanction_exposure"],
  "fired_rules": [
    { "rule_id": "MIXER_INFLOW_1HOP", "score": 50 },
    { "rule_id": "SANCTIONED_ENTITY", "score": 40 }
  ],
  "explanation": "..."
}
```

## 🔧 주요 기능

- ✅ 룰 베이스드 스코어링 (TRACE-X 룰북 기반)
- ✅ Risk Score 계산 (0~100)
- ✅ Risk Level 결정 (low/medium/high/critical)
- ✅ Risk Tags 생성
- ✅ Fired Rules 목록
- ⏳ AI 집계 (향후 구현)

## 📝 참고

- GOG 관련 코드는 `legacy/` 폴더에 보관되어 있습니다.
- 룰북은 `rules/tracex_rules.yaml`에 정의되어 있습니다.
- 자세한 구조는 `docs/STRUCTURE_SUMMARY.md`를 참고하세요.

## 📚 문서

- `docs/SCORING_API.md` - API 상세 명세
- `docs/STRUCTURE_SUMMARY.md` - 프로젝트 구조 요약
- `docs/RESTRUCTURE_GUIDE.md` - 재구성 가이드
- `docs/NEW_PROJECT_STRUCTURE.md` - 새 구조 상세 설명
