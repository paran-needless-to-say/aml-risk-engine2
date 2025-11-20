# Swagger UI 사용 가이드

Swagger UI에서 API를 테스트하는 방법입니다.

## 🚀 접속 방법

### 1. 서버 실행 확인

먼저 서버가 실행 중인지 확인:

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

### 2. Swagger UI 접속

브라우저에서 다음 URL로 접속:

```
http://localhost:5002/api-docs
```

또는

```
http://localhost:5001/api-docs
```

(포트는 서버 실행 시 표시된 포트를 사용)

---

## 📖 Swagger UI 사용법

### 1. API 목록 확인

Swagger UI 메인 페이지에서 다음 API들을 볼 수 있습니다:

- **POST /api/analyze/address** - 주소 분석
- **POST /api/score/transaction** - 단일 트랜잭션 스코어링
- **GET /health** - 헬스 체크

### 2. API 테스트하기

#### 주소 분석 API 테스트

1. **POST /api/analyze/address** 클릭

2. **"Try it out"** 버튼 클릭 (오른쪽 상단)

3. **Request body**에 JSON 입력:

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

4. **"Execute"** 버튼 클릭

5. **응답 확인**:
   - **Response Code**: 200 (성공)
   - **Response Body**: JSON 형식의 분석 결과

#### 단일 트랜잭션 스코어링 테스트

1. **POST /api/score/transaction** 클릭

2. **"Try it out"** 버튼 클릭

3. **Request body**에 JSON 입력:

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

4. **"Execute"** 버튼 클릭

---

## 🔍 입력 포맷 확인 방법

### Swagger UI에서 스키마 확인

1. API 엔드포인트 클릭 (예: `POST /api/analyze/address`)

2. **"Model"** 탭 클릭 (Example value 옆)

3. 스키마 구조 확인:
   - **필수 필드**: `required` 섹션에 표시
   - **필드 타입**: `type` 확인 (예: `integer`, `string`, `array`)
   - **예시 값**: `example` 확인

### Parameters 섹션 확인

1. **"Parameters"** 섹션에서:

   - **Required**: 필수 필드 표시
   - **Type**: 필드 타입 (예: `integer`, `string`)
   - **Description**: 필드 설명

2. **Schema** 섹션에서:
   - 전체 JSON 구조 확인
   - 중첩된 객체 구조 확인

---

## ✅ 입력 포맷 체크리스트

Swagger UI에서 확인할 사항:

- [ ] `chain_id`가 `integer` 타입인지 확인
- [ ] `transactions`가 `array` 타입인지 확인
- [ ] `transactions` 배열 내부 객체도 `chain_id`가 `integer`인지 확인
- [ ] 필수 필드가 모두 포함되어 있는지 확인

---

## 💡 팁

### 1. 예시 값 사용

Swagger UI의 **"Example value"** 탭을 클릭하면 예시 JSON을 볼 수 있습니다.

### 2. 스키마 검증

Swagger UI는 자동으로 입력 형식을 검증합니다:

- 필수 필드 누락 시 에러 표시
- 타입 불일치 시 에러 표시

### 3. 응답 확인

**Response** 섹션에서:

- **Response Code**: 200 (성공), 400 (잘못된 요청), 500 (서버 오류)
- **Response Body**: 실제 응답 데이터
- **Response Headers**: 응답 헤더 정보

---

## 🐛 문제 해결

### "Method Not Allowed" 에러

- **원인**: GET 요청으로 POST 엔드포인트 접근
- **해결**: Swagger UI에서 "Try it out" 버튼 사용

### "Missing required field" 에러

- **원인**: 필수 필드 누락
- **해결**: Swagger UI의 "Model" 탭에서 필수 필드 확인

### "chain_id must be an integer" 에러

- **원인**: `chain_id`를 문자열로 전송
- **해결**: `chain_id`를 숫자로 변경 (예: `1`)

---

## 📝 빠른 테스트

프로젝트 루트의 `test_api.json` 파일 내용을 복사해서 Swagger UI에 붙여넣으면 됩니다!

```bash
# 파일 내용 확인
cat test_api.json
```

이 내용을 Swagger UI의 Request body에 붙여넣고 "Execute" 클릭!

---

**Swagger UI**: http://localhost:5002/api-docs
