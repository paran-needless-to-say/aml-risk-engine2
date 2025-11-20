# 주소 메타데이터 저장소가 필요한 이유

## 🤔 질문: 왜 메타데이터 저장소가 필요한가?

현재 시스템은 `address_analyzer.py`에서 **백엔드로부터 거래 히스토리(`transactions` 리스트)를 받아서** 분석합니다.

그렇다면 메타데이터 저장소 없이도 계산할 수 있지 않을까요?

---

## ✅ 메타데이터 저장소 없이도 가능한 경우

### 현재 시스템 구조

```python
# address_analyzer.py
def analyze_address(
    self,
    address: str,
    chain: str,
    transactions: List[Dict[str, Any]],  # 백엔드에서 제공
    ...
):
    # 1. 트랜잭션을 시간순 정렬
    sorted_txs = sorted(transactions, key=lambda tx: self._get_timestamp(tx))

    # 여기서 필요한 정보를 계산할 수 있음:
    # - first_seen_ts: sorted_txs[0]['timestamp']
    # - last_seen_ts: sorted_txs[-1]['timestamp']
    # - age_days: (현재 시간 - first_seen_ts) / 86400
    # - tx_count_total: len(sorted_txs)
    # - first7d_usd: 첫 7일간 거래 합계 계산
```

### 계산 가능한 정보

백엔드가 **전체 거래 히스토리**를 제공한다면:

| 필요한 정보        | 계산 방법                             |
| ------------------ | ------------------------------------- |
| `first_seen_ts`    | `sorted_txs[0]['timestamp']`          |
| `last_seen_ts`     | `sorted_txs[-1]['timestamp']`         |
| `age_days`         | `(현재 시간 - first_seen_ts) / 86400` |
| `tx_count_total`   | `len(sorted_txs)`                     |
| `first7d_usd`      | 첫 7일간 거래 합계 계산               |
| `first7d_tx_count` | 첫 7일간 거래 수 계산                 |
| `inactive_days`    | `(현재 시간 - last_seen_ts) / 86400`  |
| `total_usd_total`  | 전체 거래 합계                        |
| `median_usd_total` | 전체 거래 중앙값                      |

**결론**: 백엔드가 전체 히스토리를 제공한다면 **메타데이터 저장소 없이도 구현 가능**합니다!

---

## ❌ 메타데이터 저장소가 필요한 경우

### 1. 백엔드가 전체 히스토리를 제공하지 않는 경우

**문제 시나리오**:

- 백엔드가 "최근 100개 거래"만 제공
- 주소가 1년 전에 생성되었고, 총 500개 거래가 있음
- 하지만 백엔드는 최근 100개만 제공

**결과**:

- `first_seen_ts`를 정확히 알 수 없음 (최근 100개 중 첫 번째 ≠ 실제 첫 번째)
- `age_days` 계산 불가
- `first7d_usd` 계산 불가 (첫 7일 거래가 최근 100개에 없을 수 있음)

**해결책**: 메타데이터 저장소에 주소별 정보 저장

---

### 2. 성능 최적화가 필요한 경우

**문제 시나리오**:

- 주소가 10,000개 거래를 가지고 있음
- 새로운 거래가 들어올 때마다 전체 10,000개를 다시 분석
- 매번 `first7d_usd`, `total_usd_total` 등을 다시 계산

**결과**:

- 매우 느림 (수 초 ~ 수십 초)
- 불필요한 반복 계산

**해결책**: 메타데이터 저장소에 누적 정보 저장

- 새로운 거래가 들어오면 기존 값에 더하기만 하면 됨
- 전체 재계산 불필요

---

### 3. 실시간 평가가 필요한 경우

**문제 시나리오**:

- 단일 트랜잭션 스코어링 API (`/api/score/transaction`)
- 새로운 거래 하나만 들어옴
- 하지만 B-401 룰을 평가하려면 "첫 7일간 거래" 정보 필요

**결과**:

- 단일 거래만으로는 주소의 전체 히스토리를 알 수 없음
- 백엔드에서 전체 히스토리를 매번 요청해야 함 (비효율적)

**해결책**: 메타데이터 저장소에 주소별 정보 저장

- 단일 거래만 들어와도 저장된 메타데이터로 룰 평가 가능

---

## 💡 실제 구현 방법 비교

### 방법 1: 메타데이터 저장소 없이 구현 (간단)

```python
# address_analyzer.py에 추가
def _calculate_address_metadata(self, sorted_txs: List[Dict]) -> Dict:
    """거래 히스토리에서 주소 메타데이터 계산"""
    if not sorted_txs:
        return {}

    first_seen_ts = self._get_timestamp(sorted_txs[0])
    last_seen_ts = self._get_timestamp(sorted_txs[-1])
    current_ts = int(time.time())

    age_days = (current_ts - first_seen_ts) / 86400

    # 첫 7일간 거래 계산
    first7d_ts = first_seen_ts + (7 * 86400)
    first7d_txs = [tx for tx in sorted_txs
                   if self._get_timestamp(tx) <= first7d_ts]
    first7d_usd = sum(tx.get('amount_usd', 0) for tx in first7d_txs)
    first7d_tx_count = len(first7d_txs)

    # 비활성 기간 계산
    inactive_days = (current_ts - last_seen_ts) / 86400

    # 총 거래 통계
    total_usd = sum(tx.get('amount_usd', 0) for tx in sorted_txs)
    tx_count_total = len(sorted_txs)

    return {
        'first_seen_ts': first_seen_ts,
        'last_seen_ts': last_seen_ts,
        'age_days': age_days,
        'first7d_usd': first7d_usd,
        'first7d_tx_count': first7d_tx_count,
        'inactive_days': inactive_days,
        'total_usd_total': total_usd,
        'tx_count_total': tx_count_total,
    }
```

**장점**:

- 구현 간단
- 추가 저장소 불필요
- 백엔드가 전체 히스토리를 제공하면 작동

**단점**:

- 매번 전체 히스토리 재계산 (느림)
- 백엔드가 전체 히스토리를 제공하지 않으면 작동 안 함
- 단일 트랜잭션 스코어링에서는 사용 불가

---

### 방법 2: 메타데이터 저장소 구축 (복잡하지만 효율적)

```python
# core/data/address_metadata.py
class AddressMetadataStore:
    """주소별 메타데이터 저장소"""

    def __init__(self):
        # 메모리 캐시 또는 DB
        self._metadata: Dict[str, Dict] = {}

    def update(self, address: str, tx: Dict):
        """새 거래로 메타데이터 업데이트"""
        if address not in self._metadata:
            # 첫 거래
            self._metadata[address] = {
                'first_seen_ts': self._get_timestamp(tx),
                'last_seen_ts': self._get_timestamp(tx),
                'first7d_usd': tx.get('amount_usd', 0),
                'first7d_tx_count': 1,
                'total_usd_total': tx.get('amount_usd', 0),
                'tx_count_total': 1,
            }
        else:
            # 기존 주소 업데이트
            meta = self._metadata[address]
            tx_ts = self._get_timestamp(tx)
            tx_amount = tx.get('amount_usd', 0)

            # 마지막 거래일 업데이트
            meta['last_seen_ts'] = max(meta['last_seen_ts'], tx_ts)

            # 첫 7일간 거래 업데이트
            first7d_ts = meta['first_seen_ts'] + (7 * 86400)
            if tx_ts <= first7d_ts:
                meta['first7d_usd'] += tx_amount
                meta['first7d_tx_count'] += 1

            # 총 거래 통계 업데이트
            meta['total_usd_total'] += tx_amount
            meta['tx_count_total'] += 1

    def get(self, address: str) -> Dict:
        """주소 메타데이터 조회"""
        if address not in self._metadata:
            return {}

        meta = self._metadata[address].copy()
        current_ts = int(time.time())

        # 동적 계산
        meta['age_days'] = (current_ts - meta['first_seen_ts']) / 86400
        meta['inactive_days'] = (current_ts - meta['last_seen_ts']) / 86400

        return meta
```

**장점**:

- 빠름 (누적 정보만 업데이트)
- 단일 트랜잭션 스코어링에서도 사용 가능
- 백엔드가 전체 히스토리를 제공하지 않아도 작동

**단점**:

- 구현 복잡
- 저장소 관리 필요 (메모리/DB)
- 상태 동기화 문제 (서버 재시작 시 데이터 손실 가능)

---

## 🎯 결론 및 권장사항

### 메타데이터 저장소가 필요한 경우

1. ✅ **백엔드가 전체 히스토리를 제공하지 않는 경우**
2. ✅ **성능 최적화가 중요한 경우** (수천~수만 개 거래)
3. ✅ **단일 트랜잭션 스코어링에서도 룰 평가가 필요한 경우**

### 메타데이터 저장소 없이도 되는 경우

1. ✅ **백엔드가 항상 전체 히스토리를 제공하는 경우**
2. ✅ **주소당 거래 수가 적은 경우** (수백 개 이하)
3. ✅ **주소 분석 API만 사용하는 경우** (단일 트랜잭션 스코어링 불필요)

---

## 💡 실제 구현 권장안

### 시나리오 1: 간단한 구현 (권장)

**조건**: 백엔드가 전체 히스토리를 제공하고, 주소 분석 API만 사용

**구현**: 메타데이터 저장소 없이 `address_analyzer.py`에서 직접 계산

```python
# address_analyzer.py에 메서드 추가
def _calculate_address_metadata(self, sorted_txs):
    # 위의 방법 1 코드 사용
```

**장점**: 구현 간단, 추가 저장소 불필요

---

### 시나리오 2: 효율적인 구현

**조건**: 성능이 중요하거나, 단일 트랜잭션 스코어링에서도 룰 평가 필요

**구현**: 메타데이터 저장소 구축 (메모리 캐시 또는 Redis)

**장점**: 빠름, 모든 시나리오에서 작동

---

## 📝 최종 답변

**질문**: 주소별 메타데이터 저장소 구축이 왜 필요한가?

**답변**:

1. **필수는 아님**: 백엔드가 전체 히스토리를 제공한다면 저장소 없이도 구현 가능
2. **하지만 효율적**: 저장소가 있으면 성능 향상 및 단일 트랜잭션 스코어링에서도 사용 가능
3. **권장**: 간단한 구현을 원한다면 저장소 없이 구현해도 됨 (백엔드가 전체 히스토리 제공 시)

**결론**: **메타데이터 저장소는 "필수"가 아니라 "성능 최적화"를 위한 것입니다.**
