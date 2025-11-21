# 빠른 시작: Multi-Hop 리스크 스코어링

## 🎯 최종 Request 형식 (간단 요약)

### 기본 모드 (1-hop, 빠름)

```bash
POST /api/analyze/address

{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [...]  // 프론트엔드가 제공
}
```

**응답 시간**: 1-2초

---

### Multi-hop 모드 (3-hop, 정밀) ⭐️ 권장

```bash
POST /api/analyze/address

{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3,  // 백엔드가 자동 수집
  "analysis_type": "advanced"
}
```

**응답 시간**: 3-8초 (캐싱 시)

---

## 📊 비교표

| 항목          | 기본 모드           | Multi-hop 모드               |
| ------------- | ------------------- | ---------------------------- |
| **Request**   | `transactions` 제공 | `max_hops` 지정              |
| **수집 주체** | 프론트엔드          | 백엔드                       |
| **응답 시간** | 1-2초               | 3-8초                        |
| **홉 수**     | 1-hop               | 3-hop                        |
| **패턴 탐지** | 기본                | 고급 (Layering Chain, Cycle) |
| **정확도**    | 기본                | 30-50% 향상                  |
| **사용 예시** | 실시간 대시보드     | 수동 조사                    |

---

## 🚀 cURL 예시

### 기본 모드

```bash
curl -X POST http://localhost:5001/api/analyze/address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xTarget",
    "chain_id": 1,
    "transactions": [
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
    ]
  }'
```

### Multi-hop 모드

```bash
curl -X POST http://localhost:5001/api/analyze/address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0xTarget",
    "chain_id": 1,
    "max_hops": 3,
    "analysis_type": "advanced"
  }'
```

---

## 📝 백엔드 팀에게 전달할 내용

### 핵심 요청

> Multi-hop 거래 수집 구현 필요:
>
> - `max_hops` 파라미터 지원
> - Target + Counterparty 주소들의 거래 수집
> - 각 거래에 `hop_level`, `from`, `to` 필드 추가

### 구현 우선순위

1. **Phase 1** (1주): 기본 구현

   - `max_hops` 파라미터 처리
   - 재귀적 거래 수집 로직

2. **Phase 2** (1주): 최적화
   - 캐싱 구현 (Redis)
   - 병렬 처리

### 예상 효과

- 리스크 탐지 정확도: **30-50% 향상**
- 새로운 룰 활성화: B-201 (Layering Chain), B-202 (Cycle)
- 복잡한 세탁 패턴 탐지 가능

---

## 📚 상세 문서

1. **FINAL_API_SPEC.md** - 최종 API 스펙 (읽어보세요!)
2. **BACKEND_REQUEST_MULTI_HOP.md** - 백엔드 구현 가이드
3. **SIMPLE_COMPARISON_1HOP_VS_MULTIHOP.md** - 간단 비교
4. **MULTI_HOP_REQUIREMENT.md** - 상세 요구사항
5. **ELEVATOR_PITCH_MULTIHOP.md** - 엘리베이터 피치

---

## ❓ FAQ

### Q: 왜 Multi-hop이 필요한가요?

**A**: 현재 시스템은 1-hop만 분석 → 복잡한 세탁 패턴 탐지 불가능

- B-201 (Layering Chain) 룰: **전혀 작동 안 함**
- B-202 (Cycle) 룰: **전혀 작동 안 함**

### Q: 기존 API가 깨지나요?

**A**: 아니요, 완전 하위 호환:

- `max_hops` 없으면 기존대로 1-hop만 수집
- 기존 request 형식 그대로 작동

### Q: 성능은 괜찮나요?

**A**: 캐싱 쓰면 3-8초로 단축 가능

- `analysis_type="basic"` → 기존 속도 유지 (1-2초)
- `analysis_type="advanced"` → Multi-hop 활성화 (3-8초)

---

**작성일**: 2025-11-21  
**상태**: Final Spec
