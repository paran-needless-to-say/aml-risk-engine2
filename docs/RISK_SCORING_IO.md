# 리스크 스코어링 엔진 입출력 명세

## 📥 입력 (Input)

리스크 스코어링 API는 **2가지 모드**를 지원합니다:

### 모드 1: 기본 모드 (1-hop, 빠름)

프론트엔드가 `transactions` 배열 제공:

```json
POST /api/analyze/address

{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [...],  // TransactionInput 배열
  "analysis_type": "basic"
}
```

### 모드 2: Multi-hop 모드 (3-hop, 정밀) ⭐️ 권장

백엔드가 `transactions` 자동 수집:

```json
POST /api/analyze/address

{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3,  // 최대 홉 수 (1~3)
  "analysis_type": "advanced"
}
```

---

### TransactionInput (거래 데이터 구조)

#### 기존 필드 (모드 1, 하위 호환성)

```python
@dataclass
class TransactionInput:
    tx_hash: str                    # 트랜잭션 해시
    chain_id: int                   # 체인 ID (예: 1=Ethereum, 42161=Arbitrum, 43114=Avalanche)
    timestamp: str                  # ISO8601 UTC 형식 (예: "2025-11-17T12:34:56Z")
    block_height: int               # 블록 높이 (정렬용)
    target_address: str             # 스코어링 대상 주소 (점수를 매기려는 기준 주소)
    counterparty_address: str        # 상대방 주소 (target_address와 거래한 주소)
    label: str                      # 엔티티 라벨: "mixer" | "bridge" | "cex" | "dex" | "defi" | "unknown"
    is_sanctioned: bool             # OFAC/제재 리스트 매핑 결과 (팩트)
    is_known_scam: bool             # Scam/phishing 블랙리스트 매핑 (팩트)
    is_mixer: bool                  # label에서 파생되는 사실 정보
    is_bridge: bool                 # label에서 파생되는 사실 정보
    amount_usd: float               # 시세 기반 환산 금액 (USD)
    asset_contract: str             # 자산 종류 (Ethereum native, ERC-20 등)
```

#### 신규 필드 (모드 2, Multi-hop)

```python
@dataclass
class TransactionInputMultiHop:
    # 기존 필드 모두 포함 +
    hop_level: int                  # 🆕 몇 번째 홉인지 (1, 2, 3)
    from_address: str               # 🆕 송신자 (명확)
    to_address: str                 # 🆕 수신자 (명확)
```

### JSON 요청 예시 - 기존 방식

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

### JSON 요청 예시 - Multi-hop 방식

```json
{
  "tx_hash": "0x123...",
  "chain_id": 1,
  "timestamp": "2025-11-17T12:34:56Z",
  "block_height": 21039493,
  "hop_level": 1, // 🆕
  "from": "0xTarget", // 🆕
  "to": "0xMixer1", // 🆕
  "label": "mixer",
  "is_sanctioned": false,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 5000.0,
  "asset_contract": "0xETH"
}
```

---

## 📤 출력 (Output)

### ScoringResult

리스크 스코어링 엔진은 다음 정보를 반환합니다.

```python
@dataclass
class ScoringResult:
    target_address: str             # 스코어링 대상 주소
    risk_score: float               # 리스크 점수 (0~100)
    risk_level: str                 # 리스크 레벨: "low" | "medium" | "high" | "critical"
    risk_tags: List[str]            # 리스크 태그 목록
    fired_rules: List[FiredRule]   # 발동된 룰 목록
    explanation: str                # 설명 텍스트
    completed_at: str               # 스코어링 완료 시각 (ISO8601 UTC)
    # 백엔드 요구 필드
    timestamp: str                  # 트랜잭션 타임스탬프 (ISO8601 UTC)
    chain_id: int                   # 체인 ID (예: 1=Ethereum, 42161=Arbitrum)
    value: float                    # 거래 금액 (USD, amount_usd와 동일)
```

### FiredRule

```python
@dataclass
class FiredRule:
    rule_id: str                    # 룰 ID (예: "E-101", "C-001")
    score: float                     # 해당 룰이 기여한 점수
```

### JSON 응답 예시

```json
{
  "target_address": "0xabc123...",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "sanction_exposure", "high_value_transfer"],
  "fired_rules": [
    {
      "rule_id": "E-101",
      "score": 25
    },
    {
      "rule_id": "C-001",
      "score": 30
    }
  ],
  "explanation": "1-hop sanctioned mixer에서 1,000USD 이상 유입된 거래로, 세탁 자금 유입 패턴에 해당하여 high로 분류됨.",
  "completed_at": "2025-11-17T12:34:56Z",
  "timestamp": "2025-11-19T10:00:00Z",
  "chain_id": 1,
  "value": 500000.0
}
```

---

## 🎯 리스크 레벨 매핑

리스크 점수에 따른 레벨 분류:

- **Low**: 0-29
- **Medium**: 30-59
- **High**: 60-79
- **Critical**: 80-100

---

## 📋 Risk Tags 종류

가능한 리스크 태그들:

- `mixer_inflow` - 믹서에서 유입
- `sanction_exposure` - 제재 대상과 거래
- `scam_exposure` - 사기 주소와 거래
- `high_value_transfer` - 고액 거래
- `bridge_large_transfer` - 브릿지를 통한 대규모 거래
- `cex_inflow` - 중앙화 거래소 유입

---

## 🔄 처리 흐름

1. **입력 검증**: 필수 필드 확인
2. **룰 평가**: TRACE-X 룰북 기반 규칙 평가
3. **점수 계산**: 발동된 룰들의 점수 합산 (0~100 범위)
4. **레벨 결정**: 점수 기반 리스크 레벨 결정
5. **태그 생성**: 발동된 룰 기반 리스크 태그 생성
6. **설명 생성**: 사용자 친화적 설명 텍스트 생성
7. **결과 반환**: JSON 형식으로 결과 반환

---

## 📡 API 엔드포인트

### 단일 트랜잭션 스코어링

```
POST /api/score/transaction
```

입력: TransactionInput 객체

---

### 주소 분석 (다중 트랜잭션)

```
POST /api/analyze/address
```

#### 모드 1: 기본 모드 (1-hop)

입력:

- `address` (필수): 분석 대상 주소
- `chain_id` (필수, 숫자): 체인 ID
- `transactions[]` (필수): TransactionInput 배열
- `analysis_type` (선택): "basic" (기본값)

#### 모드 2: Multi-hop 모드 (3-hop) ⭐️

입력:

- `address` (필수): 분석 대상 주소
- `chain_id` (필수, 숫자): 체인 ID
- `max_hops` (필수): 최대 홉 수 (1~3)
- `analysis_type` (필수): "advanced"
- `time_window_hours` (선택): 최근 N시간 거래만 수집

---

## 💡 참고사항

- `risk_score`는 0~100 사이의 연속값입니다 (정수로 반환)
- `timestamp`와 `completed_at`은 ISO8601 UTC 형식을 사용합니다
- `label`은 백엔드에서 사전 라벨링된 정보입니다
- `is_sanctioned`, `is_known_scam` 등은 팩트 정보로, 룰 평가에 직접 사용됩니다
- `value`는 `amount_usd`와 동일한 값입니다 (거래 금액 USD)
- `chain_id`는 숫자로 받으며, 내부적으로 체인 이름으로 변환됩니다:
  - `1` → "ethereum" (Ethereum Mainnet)
  - `42161` → "arbitrum" (Arbitrum One)
  - `43114` → "avalanche" (Avalanche C-Chain)
  - `8453` → "base" (Base Mainnet)
  - `137` → "polygon" (Polygon Mainnet)
  - `56` → "bsc" (BSC Mainnet)
  - 기타: 기본값 "ethereum"

### Multi-hop 모드 추가 정보

- **모드 선택**:

  - 기본 모드 (1-hop): 빠름 (1-2초), 실시간 대시보드 적합
  - Multi-hop 모드 (3-hop): 정밀 (3-8초), 수동 조사 적합

- **Multi-hop 장점**:

  - 복잡한 세탁 패턴 탐지 (Layering Chain, Cycle)
  - 리스크 탐지 정확도 30-50% 향상
  - B-201, B-202 룰 활성화

- **백엔드 구현 필요**:
  - Multi-hop 거래 수집 로직
  - `hop_level`, `from`, `to` 필드 추가
  - 캐싱 구현 (권장)

자세한 내용은 다음 문서를 참고하세요:

- `FINAL_API_SPEC.md` - 최종 API 스펙 (Multi-hop 지원)
- `MULTI_HOP_REQUIREMENT.md` - Multi-hop 요구사항
- `BACKEND_REQUEST_MULTI_HOP.md` - 백엔드 구현 가이드
