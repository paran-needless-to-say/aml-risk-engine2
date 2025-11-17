# HTTP 메서드: GET vs POST

## 📚 기본 개념

HTTP 메서드는 클라이언트가 서버에 요청할 때 **어떤 작업을 수행할지**를 나타냅니다.

## 🔍 GET vs POST 비교

### GET (읽기)

**특징:**

- 데이터를 **조회**할 때 사용
- 요청 데이터를 **URL 파라미터**로 전송
- **멱등성(Idempotent)**: 같은 요청을 여러 번 해도 결과가 동일
- **캐싱 가능**: 브라우저나 프록시에서 캐시 가능
- **안전(Safe)**: 서버의 상태를 변경하지 않음

**예시:**

```
GET /health
GET /api/users?page=1&limit=10
GET /api/address/0xabc123...
```

**우리 프로젝트에서:**

```python
@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인 - 데이터 변경 없음"""
    return jsonify({"status": "ok"}), 200
```

### POST (생성/처리)

**특징:**

- 데이터를 **생성**하거나 **처리**할 때 사용
- 요청 데이터를 **Request Body**로 전송
- **멱등성 없음**: 같은 요청을 여러 번 하면 다른 결과가 나올 수 있음
- **캐싱 불가**: 브라우저가 캐시하지 않음
- **안전하지 않음**: 서버의 상태를 변경함

**예시:**

```
POST /api/analyze/address
POST /api/score/transaction
POST /api/users (새 사용자 생성)
```

**우리 프로젝트에서:**

```python
@address_analysis_bp.route("/address", methods=["POST"])
def analyze_address():
    """주소 분석 - 서버에서 계산 작업 수행"""
    data = request.get_json()  # Request Body에서 데이터 받음
    # ... 분석 로직 ...
    return jsonify(result), 200
```

## 📊 비교표

| 항목                  | GET                          | POST                           |
| --------------------- | ---------------------------- | ------------------------------ |
| **용도**              | 데이터 조회                  | 데이터 생성/처리               |
| **데이터 전송 위치**  | URL 파라미터                 | Request Body                   |
| **데이터 크기 제한**  | URL 길이 제한 (약 2048자)    | 제한 없음 (일반적으로 더 큼)   |
| **캐싱**              | 가능                         | 불가능                         |
| **멱등성**            | 있음 (같은 요청 = 같은 결과) | 없음 (같은 요청 ≠ 같은 결과)   |
| **안전성**            | 안전 (서버 상태 변경 없음)   | 안전하지 않음 (서버 상태 변경) |
| **브라우저 히스토리** | 저장됨                       | 저장되지 않음                  |
| **북마크**            | 가능                         | 불가능                         |

## 💡 실제 사용 예시

### GET 예시: 주소 정보 조회 (가정)

```python
# GET: 주소의 기본 정보만 조회
GET /api/address/0xabc123
# Response: {"address": "0xabc123", "balance": "100 ETH", ...}
```

### POST 예시: 주소 분석 (실제 구현)

```python
# POST: 주소를 분석하여 리스크 스코어 계산
POST /api/analyze/address
# Request Body: {"address": "0xabc123", "transactions": [...]}
# Response: {"risk_score": 78, "risk_level": "high", ...}
```

## 🤔 왜 우리 프로젝트에서 POST를 사용하나?

### 1. `/api/analyze/address` - POST 사용 이유

- **많은 데이터 전송**: 거래 히스토리 배열을 전송해야 함
- **서버에서 계산 작업**: 리스크 스코어 계산은 서버의 CPU/메모리 사용
- **멱등성 없음**: 같은 주소를 여러 번 분석해도 시간에 따라 결과가 달라질 수 있음

### 2. `/api/score/transaction` - POST 사용 이유

- **복잡한 데이터 구조**: 트랜잭션 정보가 많음
- **서버에서 처리**: 룰 평가 및 스코어링 작업

### 3. `/health` - GET 사용 이유

- **단순 조회**: 서버 상태만 확인
- **데이터 변경 없음**: 서버 상태를 변경하지 않음
- **캐싱 가능**: 모니터링 시스템에서 주기적으로 호출 가능

## 📝 요약

- **GET**: 데이터를 **읽을 때** 사용 (조회, 검색)
- **POST**: 데이터를 **만들거나 처리할 때** 사용 (생성, 분석, 계산)

우리 프로젝트에서는:

- **GET /health**: 서버 상태 확인 (읽기)
- **POST /api/analyze/address**: 주소 분석 (처리)
- **POST /api/score/transaction**: 트랜잭션 스코어링 (처리)
