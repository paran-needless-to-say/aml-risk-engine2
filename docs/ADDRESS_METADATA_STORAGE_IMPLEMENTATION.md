# 주소 메타데이터 저장소 구현 가이드

## 📋 개요

주소 상태 관리 룰(B-401, B-402, B-403A, B-403B)을 구현하기 위한 메타데이터 저장소 구축 가이드입니다.

---

## 🎯 구현 목표

주소별로 다음 정보를 저장하고 관리:

- `first_seen_ts`: 주소가 처음 발견된 시간
- `last_seen_ts`: 마지막 거래 시간
- `first7d_usd`: 첫 7일간 총 거래액
- `first7d_tx_count`: 첫 7일간 거래 수
- `total_usd_total`: 총 거래액
- `tx_count_total`: 총 거래 수
- `age_days`: 주소 나이 (동적 계산)
- `inactive_days`: 비활성 기간 (동적 계산)

---

## 🏗️ 구현 방법

### 방법 1: 메모리 캐시 (간단, 개발/테스트용)

**장점**:

- 구현 간단
- 추가 의존성 없음
- 빠름

**단점**:

- 서버 재시작 시 데이터 손실
- 메모리 사용량 증가
- 멀티 프로세스 환경에서 동기화 문제

**구현 위치**: `core/data/address_metadata.py`

---

### 방법 2: Redis (프로덕션 권장)

**장점**:

- 영속성 (서버 재시작해도 데이터 유지)
- 빠름 (인메모리 DB)
- 분산 환경에서도 작동
- TTL 설정 가능

**단점**:

- Redis 서버 필요
- 네트워크 지연 (로컬이면 무시 가능)

**구현 위치**: `core/data/address_metadata.py` (Redis 클라이언트 사용)

---

### 방법 3: SQLite/PostgreSQL (영구 저장)

**장점**:

- 완전한 영속성
- 복잡한 쿼리 가능
- 데이터 백업/복구 용이

**단점**:

- 구현 복잡
- 상대적으로 느림
- DB 서버 관리 필요

**구현 위치**: `core/data/address_metadata.py` (SQLAlchemy 사용)

---

## 💻 구현 예시: 메모리 캐시 버전

### 1. 메타데이터 저장소 모듈 생성

**파일**: `core/data/address_metadata.py`

```python
"""
주소 메타데이터 저장소

주소별 상태 정보를 저장하고 관리
"""
from __future__ import annotations

from typing import Dict, Optional, Any
from datetime import datetime
from collections import defaultdict
import time


class AddressMetadataStore:
    """주소별 메타데이터 저장소 (메모리 캐시)"""

    def __init__(self):
        """초기화"""
        # 주소별 메타데이터 저장
        # key: address.lower(), value: metadata dict
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def update(self, address: str, tx: Dict[str, Any]) -> None:
        """
        새 거래로 메타데이터 업데이트

        Args:
            address: 주소
            tx: 거래 데이터 (timestamp, amount_usd 포함)
        """
        address_key = address.lower()
        tx_ts = self._get_timestamp(tx)
        tx_amount = float(tx.get('amount_usd', tx.get('usd_value', 0)))

        if address_key not in self._metadata:
            # 첫 거래 - 초기화
            self._metadata[address_key] = {
                'first_seen_ts': tx_ts,
                'last_seen_ts': tx_ts,
                'first7d_usd': tx_amount,
                'first7d_tx_count': 1,
                'total_usd_total': tx_amount,
                'tx_count_total': 1,
                'tx_amounts': [tx_amount],  # 중앙값 계산용
            }
        else:
            # 기존 주소 업데이트
            meta = self._metadata[address_key]

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
            meta['tx_amounts'].append(tx_amount)

            # 메모리 최적화: 오래된 거래 금액은 제거 (최근 1000개만 유지)
            if len(meta['tx_amounts']) > 1000:
                meta['tx_amounts'] = meta['tx_amounts'][-1000:]

    def get(self, address: str) -> Dict[str, Any]:
        """
        주소 메타데이터 조회

        Args:
            address: 주소

        Returns:
            메타데이터 딕셔너리 (없으면 빈 딕셔너리)
        """
        address_key = address.lower()

        if address_key not in self._metadata:
            return {}

        meta = self._metadata[address_key].copy()
        current_ts = int(time.time())

        # 동적 계산
        meta['age_days'] = (current_ts - meta['first_seen_ts']) / 86400
        meta['inactive_days'] = (current_ts - meta['last_seen_ts']) / 86400

        # 중앙값 계산 (30일, 전체)
        tx_amounts = meta.get('tx_amounts', [])
        if tx_amounts:
            sorted_amounts = sorted(tx_amounts)
            n = len(sorted_amounts)
            if n % 2 == 0:
                median = (sorted_amounts[n//2 - 1] + sorted_amounts[n//2]) / 2
            else:
                median = sorted_amounts[n//2]
            meta['median_usd_total'] = median
        else:
            meta['median_usd_total'] = 0.0

        # 30일간 통계는 별도 계산 필요 (거래 히스토리 필요)
        # 여기서는 기본값만 제공
        meta['tx_count_30d'] = meta.get('tx_count_30d', 0)
        meta['median_usd_30d'] = meta.get('median_usd_30d', 0.0)

        # 내부 필드 제거
        meta.pop('tx_amounts', None)

        return meta

    def batch_update(self, address: str, transactions: list[Dict[str, Any]]) -> None:
        """
        여러 거래를 한 번에 업데이트

        Args:
            address: 주소
            transactions: 거래 리스트
        """
        for tx in transactions:
            self.update(address, tx)

    def _get_timestamp(self, tx: Dict[str, Any]) -> int:
        """타임스탬프 추출"""
        timestamp = tx.get('timestamp')
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return int(dt.timestamp())
            except:
                return 0
        return int(timestamp) if timestamp else 0

    def clear(self, address: Optional[str] = None) -> None:
        """
        메타데이터 삭제

        Args:
            address: 주소 (None이면 전체 삭제)
        """
        if address:
            address_key = address.lower()
            self._metadata.pop(address_key, None)
        else:
            self._metadata.clear()

    def get_all_addresses(self) -> list[str]:
        """모든 주소 리스트 반환"""
        return list(self._metadata.keys())
```

---

### 2. AddressAnalyzer에 통합

**파일**: `core/scoring/address_analyzer.py`

```python
# 기존 import에 추가
from ..data.address_metadata import AddressMetadataStore

class AddressAnalyzer:
    """주소 기반 리스크 분석기"""

    def __init__(self, rules_path: str = "rules/tracex_rules.yaml"):
        # ... 기존 코드 ...

        # 메타데이터 저장소 추가
        self.metadata_store = AddressMetadataStore()

    def analyze_address(
        self,
        address: str,
        chain: str,
        transactions: List[Dict[str, Any]],
        time_range: Optional[Dict[str, str]] = None,
        analysis_type: str = "basic"
    ) -> AddressAnalysisResult:
        # ... 기존 코드 ...

        # 1. 트랜잭션을 시간순 정렬
        sorted_txs = sorted(
            transactions,
            key=lambda tx: self._get_timestamp(tx)
        )

        # 2. 메타데이터 업데이트
        self.metadata_store.batch_update(address, sorted_txs)

        # 3. 메타데이터 조회
        metadata = self.metadata_store.get(address)

        # 4. 각 트랜잭션에 대해 룰 평가 (메타데이터 포함)
        for tx in sorted_txs:
            tx_data = self._convert_transaction(tx, address)

            # 메타데이터를 tx_data에 추가
            tx_data.update(metadata)

            # 룰 평가
            fired_rules = self.rule_evaluator.evaluate_single_transaction(
                tx_data,
                include_topology=include_topology
            )
            # ... 나머지 코드 ...
```

---

### 3. RuleEvaluator에서 state 룰 평가

**파일**: `core/rules/evaluator.py`

```python
def evaluate_single_transaction(
    self,
    tx_data: Dict[str, Any],
    include_topology: bool = False
) -> List[Dict[str, Any]]:
    # ... 기존 코드 ...

    for rule in rules:
        rule_id = rule.get("id")

        # state 룰 처리
        if "state" in rule:
            # state 필드가 tx_data에 있는지 확인
            required_fields = rule.get("state", {}).get("required", [])
            if not all(field in tx_data for field in required_fields):
                continue  # 필수 필드가 없으면 건너뜀

            # 조건 확인
            if not self._check_conditions(tx_data, rule, lists):
                continue

            # 예외 확인
            if self._check_exceptions(tx_data, rule, lists):
                continue

            # 룰 발동
            score = rule.get("score", 0)
            fired_rules.append({
                "rule_id": rule_id,
                "score": float(score),
                "axis": rule.get("axis", "B"),
                "name": rule.get("name", rule_id),
                "severity": rule.get("severity", "MEDIUM")
            })
            continue
```

---

## 🔄 Redis 버전 구현 (프로덕션)

### 1. Redis 클라이언트 설정

**파일**: `core/data/address_metadata.py`

```python
import redis
import json
from typing import Dict, Optional, Any

class RedisAddressMetadataStore:
    """주소별 메타데이터 저장소 (Redis)"""

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """
        Args:
            redis_host: Redis 호스트
            redis_port: Redis 포트
            redis_db: Redis DB 번호
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.key_prefix = "address_metadata:"

    def _get_key(self, address: str) -> str:
        """Redis 키 생성"""
        return f"{self.key_prefix}{address.lower()}"

    def update(self, address: str, tx: Dict[str, Any]) -> None:
        """새 거래로 메타데이터 업데이트"""
        key = self._get_key(address)
        tx_ts = self._get_timestamp(tx)
        tx_amount = float(tx.get('amount_usd', tx.get('usd_value', 0)))

        # 기존 메타데이터 조회
        existing = self.redis_client.get(key)
        if existing:
            meta = json.loads(existing)
        else:
            # 첫 거래 - 초기화
            meta = {
                'first_seen_ts': tx_ts,
                'last_seen_ts': tx_ts,
                'first7d_usd': tx_amount,
                'first7d_tx_count': 1,
                'total_usd_total': tx_amount,
                'tx_count_total': 1,
            }

        # 메타데이터 업데이트
        meta['last_seen_ts'] = max(meta['last_seen_ts'], tx_ts)

        first7d_ts = meta['first_seen_ts'] + (7 * 86400)
        if tx_ts <= first7d_ts:
            meta['first7d_usd'] += tx_amount
            meta['first7d_tx_count'] += 1

        meta['total_usd_total'] += tx_amount
        meta['tx_count_total'] += 1

        # Redis에 저장 (TTL: 90일)
        self.redis_client.setex(
            key,
            90 * 24 * 3600,  # 90일
            json.dumps(meta)
        )

    def get(self, address: str) -> Dict[str, Any]:
        """주소 메타데이터 조회"""
        key = self._get_key(address)
        existing = self.redis_client.get(key)

        if not existing:
            return {}

        meta = json.loads(existing)
        current_ts = int(time.time())

        # 동적 계산
        meta['age_days'] = (current_ts - meta['first_seen_ts']) / 86400
        meta['inactive_days'] = (current_ts - meta['last_seen_ts']) / 86400

        return meta

    # ... 나머지 메서드는 메모리 버전과 동일 ...
```

---

## 📝 사용 예시

### 1. 주소 분석 시 자동 업데이트

```python
analyzer = AddressAnalyzer()
result = analyzer.analyze_address(
    address="0xabc...",
    chain="ethereum",
    transactions=txs  # 백엔드에서 받은 거래 히스토리
)

# 메타데이터가 자동으로 업데이트됨
metadata = analyzer.metadata_store.get("0xabc...")
print(metadata['age_days'])  # 주소 나이
print(metadata['first7d_usd'])  # 첫 7일간 거래액
```

### 2. 단일 트랜잭션 스코어링 시

```python
# TransactionScorer에도 통합 필요
scorer = TransactionScorer()
scorer.metadata_store.update(tx_input.target_address, tx_data)
metadata = scorer.metadata_store.get(tx_input.target_address)

# tx_data에 메타데이터 추가 후 룰 평가
tx_data.update(metadata)
result = scorer.score_transaction(tx_input)
```

---

## 🚀 다음 단계

1. **메타데이터 저장소 모듈 생성** (`core/data/address_metadata.py`)
2. **AddressAnalyzer에 통합**
3. **TransactionScorer에 통합** (단일 트랜잭션 스코어링용)
4. **RuleEvaluator에서 state 룰 평가 활성화**
5. **테스트 작성**

---

## ⚠️ 주의사항

1. **메모리 관리**: 메모리 버전은 주소 수가 많아지면 메모리 사용량 증가
2. **동시성**: 멀티 프로세스 환경에서는 Redis 사용 권장
3. **데이터 정확성**: 첫 7일간 거래는 정확한 타임스탬프 필요
4. **30일 통계**: 30일간 통계는 별도 계산 필요 (거래 히스토리 필터링)

---

## 📚 참고

- `docs/WHY_ADDRESS_METADATA_STORAGE.md`: 메타데이터 저장소가 필요한 이유
- `docs/RISK_SCORING_IMPLEMENTATION_STATUS.md`: 룰 구현 현황
- `rules/tracex_rules.yaml`: B-401, B-402, B-403A, B-403B 룰 정의
