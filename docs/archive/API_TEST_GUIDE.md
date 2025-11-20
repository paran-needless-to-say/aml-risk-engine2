# API 테스트 가이드

API를 테스트하는 여러 방법을 안내합니다.

## 방법 1: Swagger UI (가장 쉬움) ⭐

### Swagger UI란?

- 브라우저에서 API를 테스트할 수 있는 웹 페이지
- 코드 작성 없이 버튼 클릭으로 테스트 가능

### 사용 방법

1. **서버 실행**

   ```bash
   python3 run_server.py
   ```

2. **브라우저에서 접속**

   ```
   http://localhost:5001/api-docs
   ```

   (또는 5002, 서버가 실행 중인 포트)

3. **화면 설명**

   - 왼쪽: API 목록
   - 오른쪽: 각 API의 상세 정보

4. **API 테스트**
   - 왼쪽에서 `POST /api/score/transaction` 클릭
   - "Try it out" 버튼 클릭
   - Request body에 아래 JSON 입력:
   ```json
   {
     "tx_hash": "0x123...",
     "chain_id": 1,
     "timestamp": "2025-11-19T10:00:00Z",
     "block_height": 21039493,
     "target_address": "0xabc123...",
     "counterparty_address": "0xdef456...",
     "label": "mixer",
     "is_sanctioned": true,
     "is_known_scam": false,
     "is_mixer": true,
     "is_bridge": false,
     "amount_usd": 500000.0,
     "asset_contract": "0xETH"
   }
   ```
   - "Execute" 버튼 클릭
   - 결과 확인

---

## 방법 2: curl (터미널)

### 단일 트랜잭션 스코어링

```bash
curl -X POST http://localhost:5001/api/score/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0x123...",
    "chain_id": 1,
    "timestamp": "2025-11-19T10:00:00Z",
    "block_height": 21039493,
    "target_address": "0xabc123...",
    "counterparty_address": "0xdef456...",
    "label": "mixer",
    "is_sanctioned": true,
    "is_known_scam": false,
    "is_mixer": true,
    "is_bridge": false,
    "amount_usd": 500000.0,
    "asset_contract": "0xETH"
  }'
```

### 주소 분석

```bash
curl -X POST http://localhost:5001/api/analyze/address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xabc123...",
    "chain_id": 1,
    "transactions": [
      {
        "tx_hash": "0x123...",
        "chain_id": 1,
        "timestamp": "2025-11-19T10:00:00Z",
        "block_height": 21039493,
        "target_address": "0xabc123...",
        "counterparty_address": "0xdef456...",
        "label": "mixer",
        "is_sanctioned": true,
        "is_known_scam": false,
        "is_mixer": true,
        "is_bridge": false,
        "amount_usd": 500000.0,
        "asset_contract": "0xETH"
      }
    ],
    "analysis_type": "basic"
  }'
```

### Health Check (GET 요청)

```bash
curl http://localhost:5001/health
```

---

## 방법 3: Python 코드

```python
import requests

# 단일 트랜잭션 스코어링
url = "http://localhost:5001/api/score/transaction"
data = {
    "tx_hash": "0x123...",
    "chain_id": 1,
    "timestamp": "2025-11-19T10:00:00Z",
    "block_height": 21039493,
    "target_address": "0xabc123...",
    "counterparty_address": "0xdef456...",
    "label": "mixer",
    "is_sanctioned": True,
    "is_known_scam": False,
    "is_mixer": True,
    "is_bridge": False,
    "amount_usd": 500000.0,
    "asset_contract": "0xETH"
}

response = requests.post(url, json=data)
print(response.json())
```

---

## 방법 4: Postman (GUI 도구)

1. Postman 설치: https://www.postman.com/downloads/
2. 새 Request 생성
3. Method: POST 선택
4. URL: `http://localhost:5001/api/score/transaction`
5. Headers: `Content-Type: application/json`
6. Body → raw → JSON 선택
7. JSON 데이터 입력
8. Send 클릭

---

## 💡 추천

- **처음 사용**: Swagger UI (방법 1) - 가장 쉬움
- **빠른 테스트**: curl (방법 2)
- **프로그래밍**: Python 코드 (방법 3)
- **고급 사용자**: Postman (방법 4)

---

## ❓ 문제 해결

### Swagger UI가 안 열릴 때

1. 서버가 실행 중인지 확인

   ```bash
   curl http://localhost:5001/health
   ```

2. 포트 확인

   - 서버 실행 시 출력된 포트 번호 확인
   - `http://localhost:5001/api-docs` 또는 `http://localhost:5002/api-docs`

3. 브라우저 캐시 삭제 후 새로고침 (Ctrl+F5)

### "Method Not Allowed" 에러

- 브라우저 주소창에 직접 입력하지 마세요
- Swagger UI에서 "Try it out" 버튼을 사용하세요
- 또는 curl/Python으로 POST 요청을 보내세요
