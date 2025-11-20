# Talend API Tester 사용 가이드

크롬 익스텐션 Talend API Tester로 API를 테스트하는 방법입니다.

## ✅ 올바른 설정

### 1. Method

```
POST
```

### 2. URL

```
http://localhost:5002/api/analyze/address
```

(또는 서버가 실행 중인 포트)

### 3. Headers

```
Content-Type: application/json
```

### 4. Body (중요!)

**Body 타입**: `Text` 또는 `JSON` 선택

**Body 내용**:

```json
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
    }
  ],
  "analysis_type": "basic"
}
```

## ⚠️ 주의사항

### 1. Body가 비어있으면 안 됩니다!

- Body 섹션에 반드시 JSON 데이터를 입력해야 합니다
- `length: 0 byte`가 나오면 안 됩니다
- Body 타입을 `Text` 또는 `JSON`으로 설정하세요

### 2. Content-Type 헤더 확인

- `Content-Type: application/json`이 설정되어 있는지 확인
- 체크박스가 체크되어 있는지 확인

### 3. chain_id는 숫자

```json
{
  "chain_id": 1, // ✅ 숫자
  "transactions": [
    {
      "chain_id": 1 // ✅ 숫자
    }
  ]
}
```

❌ 잘못된 예:

```json
{
  "chain_id": "1", // ❌ 문자열
  "chain_id": "ETH" // ❌ 문자열
}
```

## 🔍 500 에러 해결 방법

### 1. 서버 실행 확인

```bash
curl http://localhost:5002/health
```

응답:

```json
{
  "status": "ok",
  "service": "aml-risk-engine"
}
```

### 2. Body 확인

- Body가 비어있지 않은지 확인
- JSON 형식이 올바른지 확인 (쉼표, 따옴표 등)
- `chain_id`가 숫자인지 확인

### 3. 필수 필드 확인

최소 필수 필드:

- `address`
- `chain_id` (숫자)
- `transactions` (배열)
  - 각 트랜잭션에: `tx_hash`, `chain_id`, `timestamp`, `block_height`, `target_address`, `counterparty_address`, `label`, `is_sanctioned`, `is_known_scam`, `is_mixer`, `is_bridge`, `amount_usd`, `asset_contract`

### 4. 예시 파일 사용

프로젝트의 `docs/examples/test_api.json` 파일 내용을 복사해서 Body에 붙여넣으세요.

## 📝 단계별 테스트

### Step 1: 서버 실행

```bash
python3 run_server.py
```

### Step 2: Talend API Tester 설정

1. Method: `POST`
2. URL: `http://localhost:5002/api/analyze/address`
3. Headers: `Content-Type: application/json` 추가
4. Body: 위의 JSON 예시 복사/붙여넣기

### Step 3: Send 클릭

### Step 4: 응답 확인

**성공 시 (200)**:

```json
{
  "target_address": "0xhigh_risk_mixer_sanctioned",
  "risk_score": 98,
  "risk_level": "critical",
  "chain_id": 1,
  "timestamp": "...",
  "value": 16000.0,
  ...
}
```

**에러 시**:

- 400: 요청 형식 오류 (필수 필드 누락, 타입 오류)
- 500: 서버 내부 오류 (서버 로그 확인 필요)

## 💡 팁

1. **예시 파일 사용**: `docs/examples/test_api.json` 내용을 그대로 복사
2. **JSON 검증**: Body 입력 후 JSON 형식이 올바른지 확인
3. **서버 로그 확인**: 500 에러 시 서버 터미널에서 에러 메시지 확인

## 🔗 참고

- 상세 입력 형식: `docs/CORRECT_INPUT_FORMAT.md`
- 빠른 테스트 가이드: `docs/QUICK_TEST_GUIDE.md`
- API 문서: `docs/API_DOCUMENTATION.md`
