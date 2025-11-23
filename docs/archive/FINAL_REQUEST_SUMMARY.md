# 최종 Request 형식 요약 (백엔드 팀용)

## 🎯 한 줄 요약

**리스크 스코어링 API가 2가지 모드를 지원합니다:**

1. **기본 모드** (1-hop): 프론트엔드가 `transactions` 제공 (빠름, 1-2초)
2. **Multi-hop 모드** (3-hop): 백엔드가 `transactions` 수집 (정밀, 3-8초)

---

## 📝 최종 Request 형식

### 옵션 A: 기본 모드 (기존 방식, 계속 지원)

```json
POST /api/analyze/address

{
  "address": "0xTarget",
  "chain_id": 1,
  "transactions": [...]  // 프론트엔드가 제공
}
```

### 옵션 B: Multi-hop 모드 (신규, 권장) ⭐️

```json
POST /api/analyze/address

{
  "address": "0xTarget",
  "chain_id": 1,
  "max_hops": 3,  // 백엔드가 자동 수집
  "analysis_type": "advanced"
}
```

---

## 🔧 백엔드 구현 필요 사항

### 1. API 파라미터 처리

```python
@app.route("/api/analyze/address", methods=["POST"])
def analyze_address():
    address = request.json.get("address")  # 필수
    chain_id = request.json.get("chain_id")  # 필수
    max_hops = request.json.get("max_hops", 1)  # 기본값: 1

    # 옵션 A: 프론트엔드가 제공
    if "transactions" in request.json:
        transactions = request.json["transactions"]

    # 옵션 B: 백엔드가 수집
    else:
        transactions = collect_multi_hop(address, chain_id, max_hops)

    # 분석 수행 (동일)
    result = analyze(address, chain_id, transactions)
    return jsonify(result)
```

### 2. Multi-hop 수집 로직

```python
def collect_multi_hop(address, chain_id, max_hops):
    all_txs = []
    visited = set()
    current_level = {address}

    for hop in range(1, max_hops + 1):
        next_level = set()

        for addr in current_level:
            if addr in visited:
                continue

            # Etherscan API 호출
            txs = fetch_transactions(addr, chain_id)

            for tx in txs:
                tx["hop_level"] = hop  # 🆕 추가
                tx["from"] = addr  # 🆕 명확히 설정
                tx["to"] = tx.get("counterparty")  # 🆕 명확히 설정
                all_txs.append(tx)

                next_level.add(tx["to"] if tx["from"] == addr else tx["from"])

            visited.add(addr)

        current_level = next_level

        if len(current_level) > 50:  # 성능 제한
            break

    return all_txs
```

---

## 📊 비교

| 항목      | 기본 모드           | Multi-hop 모드               |
| --------- | ------------------- | ---------------------------- |
| Request   | `transactions` 제공 | `max_hops` 지정              |
| 수집 주체 | 프론트엔드          | 백엔드                       |
| 응답 시간 | 1-2초               | 3-8초 (캐싱 시)              |
| 홉 수     | 1                   | 3                            |
| 정확도    | 기본                | 30-50% 향상                  |
| 패턴 탐지 | 기본                | 고급 (Layering Chain, Cycle) |
| 사용 예시 | 실시간 대시보드     | 수동 조사                    |

---

## 📈 예상 효과

- **리스크 탐지 정확도**: 30-50% 향상
- **새로운 룰 활성화**: B-201 (Layering Chain), B-202 (Cycle)
- **복잡한 패턴 탐지**: Mixer 경로, 순환 거래 등
- **False Positive 감소**: 20-30%

---

## 🚀 구현 스케줄

### Week 1: Phase 1 (기본 구현)

- [ ] `max_hops` 파라미터 처리
- [ ] 재귀적 거래 수집 로직
- [ ] `hop_level`, `from`, `to` 필드 추가

### Week 2: Phase 2 (최적화)

- [ ] 캐싱 구현 (Redis)
- [ ] 병렬 처리
- [ ] Rate limiting 처리

**예상 개발 기간**: 2주

---

## 📚 상세 문서

백엔드 팀이 읽어야 할 문서 (우선순위순):

1. **FINAL_API_SPEC.md** ⭐️ - 최종 API 스펙 (필독!)
2. **BACKEND_REQUEST_MULTI_HOP.md** - 구현 가이드
3. **SIMPLE_COMPARISON_1HOP_VS_MULTIHOP.md** - 간단 비교
4. **MULTI_HOP_REQUIREMENT.md** - 상세 요구사항

모든 문서는 `docs/` 폴더에 있습니다.

---

## ❓ 예상 질문

### Q: 왜 필요한가요?

**A**: 현재 시스템은 1-hop만 분석 → B-201, B-202 룰이 **전혀 작동 안 함**

### Q: 기존 API가 깨지나요?

**A**: 아니요, 완전 하위 호환. `max_hops` 없으면 기존대로 동작

### Q: 성능은?

**A**: 캐싱 쓰면 3-8초로 단축 가능

### Q: 우선순위?

**A**: **High**. 리스크 탐지의 30-50%가 누락되고 있음

---

## 📞 문의

- **문서**: `docs/FINAL_API_SPEC.md` 참고
- **질문**: Risk Scoring Team

---

**작성일**: 2025-11-21  
**버전**: 1.0 Final  
**상태**: 백엔드 구현 대기중
