# API 응답 예쁘게 공유하는 방법

백엔드 팀처럼 API 응답을 예쁘게 포맷팅해서 공유하는 방법입니다.

## 방법 1: 브라우저에서 직접 보기 (가장 쉬움) ⭐

### 1. API 호출

브라우저 주소창에 직접 입력:

```
http://localhost:5002/api/analyze/address
```

또는 GET 요청:

```
http://localhost:5002/health
```

### 2. JSON 포맷터 확장 프로그램 설치

**Chrome 확장 프로그램**:

- **JSON Formatter** (추천)
- **JSON Viewer**
- **Pretty JSON**

설치 후 자동으로 JSON이 예쁘게 포맷팅됩니다!

### 3. Pretty Print 체크

일부 브라우저나 도구에서는 "pretty print" 체크박스를 체크하면 됩니다.

---

## 방법 2: 온라인 JSON 포맷터 사용

### 추천 사이트

1. **JSON Formatter & Validator**

   - https://jsonformatter.org/
   - JSON 붙여넣기 → Format 클릭

2. **JSONLint**

   - https://jsonlint.com/
   - Validate & Format

3. **JSON Pretty Print**
   - https://jsonprettyprint.com/

### 사용 방법

1. API 응답 복사 (원본 JSON)
2. 위 사이트 중 하나 접속
3. JSON 붙여넣기
4. Format/Beautify 클릭
5. 포맷팅된 결과 복사
6. 톡방에 공유

---

## 방법 3: 터미널에서 포맷팅

### curl + jq 사용

```bash
curl -X POST http://localhost:5002/api/analyze/address \
  -H "Content-Type: application/json" \
  -d @docs/examples/test_api.json | jq .
```

`jq` 설치:

```bash
# macOS
brew install jq

# Linux
sudo apt-get install jq
```

### Python 사용

```bash
curl -X POST http://localhost:5002/api/analyze/address \
  -H "Content-Type: application/json" \
  -d @docs/examples/test_api.json | python3 -m json.tool
```

---

## 방법 4: Talend API Tester에서 공유

### 1. API 테스트

Talend API Tester에서 API 호출

### 2. 응답 복사

- Response 탭에서 응답 JSON 복사
- 또는 "Copy" 버튼 클릭

### 3. 포맷팅

- 온라인 JSON 포맷터에 붙여넣기
- 또는 JSON Formatter 확장 프로그램 사용

### 4. 공유

포맷팅된 JSON을 톡방에 공유

---

## 방법 5: 코드로 포맷팅

### Python 스크립트

```python
import json
import requests

# API 호출
response = requests.post(
    "http://localhost:5002/api/analyze/address",
    json={
        "address": "0xhigh_risk_mixer_sanctioned",
        "chain_id": 1,
        "transactions": [...]
    }
)

# 예쁘게 포맷팅
formatted = json.dumps(response.json(), indent=2, ensure_ascii=False)
print(formatted)
```

---

## 방법 6: Swagger UI에서 스크린샷

### 1. Swagger UI 접속

```
http://localhost:5002/api-docs
```

### 2. API 테스트

- "Try it out" 클릭
- Request body 입력
- "Execute" 클릭

### 3. 응답 확인

- Response Body가 자동으로 포맷팅되어 표시됨
- 스크린샷 찍기
- 또는 응답 복사

---

## 💡 추천 방법

### 빠른 공유 (톡방)

1. **JSON Formatter 확장 프로그램 설치** (Chrome)
2. API 호출 (브라우저 또는 Talend)
3. 응답 복사
4. 톡방에 붙여넣기 (자동 포맷팅)

### 상세 공유 (문서/이메일)

1. API 호출
2. 응답 복사
3. 온라인 JSON 포맷터 사용
4. 포맷팅된 결과 복사
5. 공유

---

## 📝 예시

### 원본 (한 줄)

```json
{
  "target_address": "0xabc123...",
  "risk_score": 98,
  "risk_level": "critical",
  "chain_id": 1,
  "timestamp": "2025-11-20T16:32:47Z",
  "value": 16000.0,
  "fired_rules": [{ "rule_id": "E-101", "score": 32 }],
  "risk_tags": ["mixer_inflow", "sanction_exposure"]
}
```

### 포맷팅 후 (예쁘게)

```json
{
  "target_address": "0xabc123...",
  "risk_score": 98,
  "risk_level": "critical",
  "chain_id": 1,
  "timestamp": "2025-11-20T16:32:47Z",
  "value": 16000.0,
  "fired_rules": [
    {
      "rule_id": "E-101",
      "score": 32
    }
  ],
  "risk_tags": ["mixer_inflow", "sanction_exposure"]
}
```

---

## 🔧 JSON Formatter 확장 프로그램 설치

### Chrome Web Store

1. Chrome 웹스토어 접속
2. "JSON Formatter" 검색
3. 설치
4. 완료! 이제 JSON이 자동으로 예쁘게 표시됩니다.

---

**가장 쉬운 방법**: JSON Formatter 확장 프로그램 설치 → API 호출 → 응답 복사 → 톡방에 붙여넣기!
