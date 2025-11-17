# 사용자 시나리오: 기본 스코어링 vs 심층 분석

## 🎯 핵심 시나리오

**사용자가 주소를 조회하면 기본 스코어링으로 빠르게 결과를 보여주고, 필요 시 "심층 분석" 버튼을 클릭하여 고급 분석을 수행합니다.**

---

## 📱 시나리오 1: 수동 탐지 (주소 조사)

### 1단계: 주소 입력 및 기본 스코어링

**사용자 액션**:

1. 프론트엔드에서 주소 입력: `0xABC123...`
2. "분석하기" 버튼 클릭

**백엔드 요청**:

```http
POST /api/analyze/address
Content-Type: application/json

{
  "address": "0xABC123...",
  "chain": "ethereum",
  "transactions": [
    // 1홉 데이터만 (빠른 응답을 위해)
    {"from": "0xABC123", "to": "0xDEF456", ...},
    {"from": "0xABC123", "to": "0xGHI789", ...}
  ]
}
```

**백엔드 응답** (1-2초):

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
  "explanation": "제재 대상과 거래, 믹서 직접 노출 패턴 감지로 인해 medium 리스크로 분류됨.",
  "analysis_type": "basic"
}
```

**프론트엔드 표시**:

- ✅ 빠른 응답 (1-2초)
- 리스크 스코어: 45점 (medium)
- 발동된 룰: 2개
- "심층 분석" 버튼 표시

---

### 2단계: 심층 분석 요청

**사용자 액션**:

1. "심층 분석" 버튼 클릭
2. 로딩 표시 (5-30초 예상)

**백엔드 요청**:

```http
POST /api/analyze/address/advanced
Content-Type: application/json

{
  "address": "0xABC123...",
  "chain": "ethereum",
  "transactions": [
    // 3홉 데이터 (그래프 구조 분석을 위해)
    // 0홉
    {"from": "0xABC123", "to": "0xDEF456", ...},
    // 1홉
    {"from": "0xDEF456", "to": "0xGHI789", ...},
    {"from": "0xDEF456", "to": "0xJKL012", ...},
    // 2홉
    {"from": "0xGHI789", "to": "0xMNO345", ...},
    // 3홉
    {"from": "0xMNO345", "to": "0xPQR678", ...}
  ]
}
```

**백엔드 응답** (5-30초):

```json
{
  "target_address": "0xABC123...",
  "risk_score": 78,
  "risk_level": "high",
  "risk_tags": [
    "mixer_inflow",
    "sanction_exposure",
    "layering_chain",
    "cycle_pattern"
  ],
  "fired_rules": [
    { "rule_id": "C-001", "score": 30 },
    { "rule_id": "E-101", "score": 15 },
    { "rule_id": "B-201", "score": 25 }, // 그래프 구조 분석 결과
    { "rule_id": "B-202", "score": 30 } // 그래프 구조 분석 결과
  ],
  "explanation": "제재 대상과 거래, 믹서 직접 노출, 레이어링 체인, 순환 패턴 감지로 인해 high 리스크로 분류됨.",
  "analysis_type": "advanced"
}
```

**프론트엔드 표시**:

- ⚠️ 느린 응답 (5-30초)
- 리스크 스코어 업데이트: 45점 → 78점 (medium → high)
- 발동된 룰 업데이트: 2개 → 4개
- 추가된 룰: B-201 (Layering Chain), B-202 (Cycle)
- 그래프 시각화 표시 (선택사항)

---

## 📱 시나리오 2: 실시간 탐지 (CEX 입출금)

### 1단계: 입출금 주소 자동 분석

**시스템 액션**:

1. CEX에서 입출금 주소 감지
2. 자동으로 기본 스코어링 요청

**백엔드 요청**:

```http
POST /api/analyze/address
Content-Type: application/json

{
  "address": "0xXYZ789...",
  "chain": "ethereum",
  "transactions": [
    // 1홉 데이터만 (빠른 응답)
    {"from": "0xXYZ789", "to": "0xCEX001", ...}
  ]
}
```

**백엔드 응답** (1-2초):

```json
{
  "target_address": "0xXYZ789...",
  "risk_score": 85,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow", "sanction_exposure", "high_value_transfer"],
  "fired_rules": [
    { "rule_id": "C-001", "score": 30 },
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "C-003", "score": 30 }
  ],
  "explanation": "제재 대상과 거래, 믹서 직접 노출, 고액 거래 패턴 감지로 인해 high 리스크로 분류됨.",
  "analysis_type": "basic"
}
```

**시스템 처리**:

- ✅ 빠른 응답 (1-2초)
- 리스크 스코어 85점 (high) → **자동 알림 생성**
- 대시보드에 표시
- 심층 분석은 수동으로 요청 가능

---

### 2단계: 수동 심층 분석 (선택사항)

**사용자 액션**:

1. 대시보드에서 알림 클릭
2. "심층 분석" 버튼 클릭

**백엔드 요청**:

```http
POST /api/analyze/address/advanced
Content-Type: application/json

{
  "address": "0xXYZ789...",
  "chain": "ethereum",
  "transactions": [
    // 3홉 데이터
    ...
  ]
}
```

**백엔드 응답** (5-30초):

```json
{
  "target_address": "0xXYZ789...",
  "risk_score": 95,
  "risk_level": "critical",
  "risk_tags": [
    "mixer_inflow",
    "sanction_exposure",
    "high_value_transfer",
    "layering_chain",
    "cycle_pattern"
  ],
  "fired_rules": [
    { "rule_id": "C-001", "score": 30 },
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "C-003", "score": 30 },
    { "rule_id": "B-201", "score": 25 },
    { "rule_id": "B-202", "score": 30 }
  ],
  "explanation": "...",
  "analysis_type": "advanced"
}
```

**시스템 처리**:

- 리스크 스코어 업데이트: 85점 → 95점 (high → critical)
- **즉시 차단 조치** 또는 **수동 검토 요청**

---

## 📱 시나리오 3: 대시보드 (오늘의 알림)

### 1단계: 대시보드 로딩

**사용자 액션**:

1. 대시보드 페이지 접속
2. "오늘의 알림" 목록 요청

**백엔드 요청** (각 주소마다):

```http
POST /api/analyze/address
Content-Type: application/json

{
  "address": "0xALERT1...",
  "chain": "ethereum",
  "transactions": [...]
}
```

**백엔드 응답** (각 주소마다 1-2초):

```json
{
  "target_address": "0xALERT1...",
  "risk_score": 60,
  "risk_level": "high",
  "risk_tags": ["mixer_inflow"],
  "fired_rules": [
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "C-003", "score": 35 }
  ],
  "explanation": "...",
  "analysis_type": "basic"
}
```

**프론트엔드 표시**:

- ✅ 빠른 로딩 (여러 주소 병렬 처리)
- 알림 목록 표시
- 각 알림에 "심층 분석" 버튼

---

### 2단계: 알림 상세 보기

**사용자 액션**:

1. 알림 클릭
2. 상세 페이지로 이동
3. "심층 분석" 버튼 클릭 (선택사항)

**백엔드 요청**:

```http
POST /api/analyze/address/advanced
...
```

**프론트엔드 표시**:

- 상세 정보 표시
- 그래프 시각화 (선택사항)
- 추가된 룰 (B-201, B-202) 표시

---

## 🔄 시나리오 4: API 옵션 사용 (하이브리드)

### 기본 스코어링 + 옵션

**사용자 액션**:

1. 주소 입력
2. "분석하기" 버튼 클릭
3. 옵션에서 `analysis_type: "advanced"` 선택

**백엔드 요청**:

```http
POST /api/analyze/address
Content-Type: application/json

{
  "address": "0xABC123...",
  "chain": "ethereum",
  "transactions": [...],
  "analysis_type": "advanced"  // 옵션으로 고급 분석 요청
}
```

**백엔드 응답**:

- `analysis_type: "basic"`이면 기본 스코어링 (1-2초)
- `analysis_type: "advanced"`이면 고급 분석 (5-30초)

---

## 📊 성능 비교

| 시나리오          | 엔드포인트                      | 응답 시간 | 평가 룰   | 사용 사례             |
| ----------------- | ------------------------------- | --------- | --------- | --------------------- |
| **기본 스코어링** | `/api/analyze/address`          | 1-2초     | 기본 룰만 | 실시간 탐지, 대시보드 |
| **심층 분석**     | `/api/analyze/address/advanced` | 5-30초    | 모든 룰   | 수동 탐지, 상세 조사  |

---

## 💡 프론트엔드 구현 가이드

### 1. 기본 스코어링 UI

```javascript
// 주소 입력 후 기본 스코어링
async function analyzeAddress(address) {
  const response = await fetch("/api/analyze/address", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      address: address,
      chain: "ethereum",
      transactions: transactions, // 1홉 데이터
    }),
  });

  const result = await response.json();

  // 빠른 응답 표시
  displayBasicResult(result);

  // 심층 분석 버튼 표시
  showDeepAnalysisButton();
}
```

### 2. 심층 분석 UI

```javascript
// 심층 분석 버튼 클릭
async function performDeepAnalysis(address) {
  // 로딩 표시
  showLoadingSpinner();

  const response = await fetch("/api/analyze/address/advanced", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      address: address,
      chain: "ethereum",
      transactions: transactions, // 3홉 데이터
    }),
  });

  const result = await response.json();

  // 결과 업데이트
  updateResult(result);

  // 그래프 시각화 (선택사항)
  visualizeGraph(result);
}
```

### 3. UI 상태 관리

```javascript
// 상태 관리
const analysisState = {
  basic: null, // 기본 스코어링 결과
  advanced: null, // 심층 분석 결과
  loading: false, // 로딩 상태
};

// 기본 스코어링 완료 후
analysisState.basic = result;
analysisState.loading = false;

// 심층 분석 진행 중
analysisState.loading = true;

// 심층 분석 완료 후
analysisState.advanced = result;
analysisState.loading = false;
```

---

## ✅ 권장 사항

### 1. 기본 스코어링 사용

- ✅ 실시간 탐지 (CEX 입출금)
- ✅ 대시보드 알림 목록
- ✅ 빠른 주소 조회

### 2. 심층 분석 사용

- ✅ 수동 탐지 (주소 조사)
- ✅ 상세 분석 필요 시
- ✅ 그래프 구조 분석 필요 시

### 3. 사용자 경험

- ✅ 기본 스코어링은 항상 빠르게 (1-2초)
- ✅ 심층 분석은 선택적으로 (5-30초)
- ✅ 로딩 표시 명확히
- ✅ 결과 비교 표시 (기본 vs 심층)

---

## 📋 API 호출 예시

### 기본 스코어링

```bash
curl -X POST http://localhost:5000/api/analyze/address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xABC123...",
    "chain": "ethereum",
    "transactions": [...]
  }'
```

### 심층 분석

```bash
curl -X POST http://localhost:5000/api/analyze/address/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xABC123...",
    "chain": "ethereum",
    "transactions": [...]
  }'
```
