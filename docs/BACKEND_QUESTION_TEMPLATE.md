# 백엔드 팀에게 보낼 질문 템플릿

## 📧 간단한 질문 (슬랙/채팅용)

````
안녕하세요! 리스크 스코어링 API 파라미터 형식 확인 부탁드립니다.

현재 API는 다음과 같은 형식으로 데이터를 받습니다:

**주소 분석 API** (`POST /api/analyze/address`):
```json
{
  "address": "0xabc123...",
  "chain_id": 1,  // 숫자 (1=Ethereum, 42161=Arbitrum 등)
  "transactions": [
    {
      "tx_hash": "0x123...",
      "chain_id": 1,  // 숫자
      "timestamp": "2025-11-19T10:00:00Z",
      "target_address": "0xabc123...",
      "counterparty_address": "0xdef456...",
      "label": "mixer",
      "is_sanctioned": true,
      "is_known_scam": false,
      "is_mixer": true,
      "is_bridge": false,
      "amount_usd": 500000.0,
      "asset_contract": "0xETH",
      "block_height": 21039493
    }
  ]
}
````

**질문**:

1. 이 형식으로 데이터를 보내주실 수 있나요?
2. `chain_id`를 숫자로 보내주실 수 있나요? (예: 1, 42161, 43114)
3. `transactions` 배열 내부의 각 트랜잭션에도 `chain_id`가 필요한데, 이것도 숫자로 가능한가요?

Swagger UI: http://localhost:5002/api-docs
문서: docs/API_DOCUMENTATION.md

테스트해보시고 문제 있으면 알려주세요!

```

---

## 📝 상세한 질문 (이메일/문서용)

```

제목: 리스크 스코어링 API 파라미터 형식 확인 요청

안녕하세요!

리스크 스코어링 API 통합을 위해 파라미터 형식을 확인하고 싶습니다.

## 현재 API 스펙

### 1. 주소 분석 API

**엔드포인트**: `POST /api/analyze/address`

**요청 형식**:

```json
{
  "address": "0xabc123...",
  "chain_id": 1, // 숫자 (1=Ethereum Mainnet)
  "transactions": [
    {
      "tx_hash": "0x123...",
      "chain_id": 1, // 숫자
      "timestamp": "2025-11-19T10:00:00Z",
      "block_height": 21039493,
      "target_address": "0xabc123...",
      "counterparty_address": "0xdef456...",
      "label": "mixer", // mixer|bridge|cex|dex|defi|unknown
      "is_sanctioned": true,
      "is_known_scam": false,
      "is_mixer": true,
      "is_bridge": false,
      "amount_usd": 500000.0,
      "asset_contract": "0xETH"
    }
  ],
  "analysis_type": "basic" // 선택사항: "basic" 또는 "advanced"
}
```

### 2. 단일 트랜잭션 스코어링

**엔드포인트**: `POST /api/score/transaction`

**요청 형식**: 위의 `transactions` 배열 내부 객체와 동일

## 확인 사항

1. **chain_id 형식**:

   - 현재는 숫자로 받습니다 (예: 1, 42161, 43114)
   - 백엔드에서 이 형식으로 보내주실 수 있나요?

2. **transactions 배열**:

   - 각 트랜잭션 객체에도 `chain_id`가 필요합니다
   - 이것도 숫자로 가능한가요?

3. **데이터 소스**:

   - 트랜잭션 데이터는 어디서 오나요? (Etherscan? 블록체인 노드?)
   - `label`, `is_sanctioned` 등은 어떻게 결정되나요?

4. **호출 시나리오**:
   - 언제 이 API를 호출하나요? (실시간? 사용자 조회 시?)
   - 성능 요구사항이 있나요? (응답 시간, 동시 요청 수)

## 테스트 방법

1. 서버 실행:

   ```bash
   python3 run_server.py
   ```

2. Swagger UI 접속:

   ```
   http://localhost:5002/api-docs
   ```

3. API 테스트:
   - "Try it out" 버튼으로 직접 테스트 가능
   - 또는 curl/Python으로 테스트

## 참고 문서

- API 문서: `docs/API_DOCUMENTATION.md`
- 입출력 명세: `docs/RISK_SCORING_IO.md`
- 배포 가이드: `docs/DEPLOYMENT_GUIDE.md`

테스트해보시고 피드백 주시면 반영하겠습니다!

감사합니다.

```

---

## 💬 더 간단한 버전 (한 문장)

```

안녕하세요! 리스크 스코어링 API에서 chain_id를 숫자로 받는데 (예: 1=Ethereum, 42161=Arbitrum),
백엔드에서 이 형식으로 보내주실 수 있나요?
Swagger UI: http://localhost:5002/api-docs

```

---

## ✅ 추천

**가장 효과적인 방법**:
1. Swagger UI 링크 공유
2. 간단한 예시 JSON 제공
3. 핵심 질문만 명확하게

위의 "간단한 질문" 템플릿을 사용하시면 됩니다!

```
