# API 테스트 예시 파일

이 폴더에는 API 테스트에 사용할 수 있는 예시 JSON 파일들이 있습니다.

## 파일 목록

- `test_api.json` - 주소 분석 API 테스트용 예시
- `test_single_transaction.json` - 단일 트랜잭션 스코어링 API 테스트용 예시

## 사용 방법

### 주소 분석 API 테스트

```bash
curl -X POST http://localhost:5002/api/analyze/address \
  -H "Content-Type: application/json" \
  -d @docs/examples/test_api.json
```

### 단일 트랜잭션 스코어링 테스트

```bash
curl -X POST http://localhost:5002/api/score/transaction \
  -H "Content-Type: application/json" \
  -d @docs/examples/test_single_transaction.json
```

또는 Swagger UI에서 이 파일들의 내용을 복사해서 사용할 수 있습니다.

## 참고

- 모든 `chain_id`는 숫자 형식입니다 (예: 1, 42161)
- `transactions` 배열 내부의 각 트랜잭션에도 `chain_id`가 필요합니다
- 자세한 입력 형식은 `docs/CORRECT_INPUT_FORMAT.md`를 참고하세요
