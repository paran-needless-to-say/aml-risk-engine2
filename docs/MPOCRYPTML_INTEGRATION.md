# MPOCryptoML 통합 계획

## 🔍 발견된 그래프 분석 코드

`legacy/multi_classification/` 폴더에 그래프 분석 코드가 있습니다:

### 1. Graph Individual (개별 그래프 분석)

- **위치**: `legacy/multi_classification/graph_individual/`
- **기능**:
  - 트랜잭션 데이터를 NetworkX 그래프로 변환
  - GCN, GIN, GraphSAGE, GAT 등 GNN 모델 학습
  - 주소/컨트랙트 분류 (fraud/non-fraud)
- **사용 기술**: PyTorch Geometric, NetworkX

### 2. Graph of Graph (계층적 그래프 분석)

- **위치**: `legacy/multi_classification/graph_of_graph/`
- **기능**:
  - 계층적 그래프 구조 (macro graph + micro graphs)
  - SEAL, DVGGA, GOGNN 모델
  - 그래프 레벨 분류
- **사용 기술**: PyTorch Geometric, NetworkX

## 💡 미구현 룰 통합 방안

### 1. 토폴로지 룰 (B-201, B-202) - ⭐⭐⭐⭐

**현재 문제**: 그래프 구조 분석 필요

**MPOCryptoML 활용**:

```python
# legacy/multi_classification/graph_individual/dataloader.py 참고
def create_graph(transaction_df):
    graph = nx.DiGraph()
    # 주소를 노드로, 거래를 엣지로 변환
    for _, row in transaction_df.iterrows():
        graph.add_edge(row['from'], row['to'], weight=row['usd_value'])
    return graph
```

**구현 계획**:

1. 트랜잭션 히스토리를 NetworkX 그래프로 변환
2. B-201 (Layering Chain): 3홉 이상 경로 탐색
3. B-202 (Cycle): 순환 구조 탐지

**필요한 것**:

- `core/aggregation/topology.py` 모듈 생성
- NetworkX 그래프 구축 로직
- 경로 탐색 알고리즘 (DFS/BFS)

### 2. 버킷 기반 룰 (B-203, B-204) - ⭐⭐

**현재 문제**: 시간 버킷 그룹화 필요

**구현 계획**:

1. 윈도우 기반 로직 확장
2. 10분 버킷으로 트랜잭션 그룹화
3. 버킷별 distinct count, sum 계산

**필요한 것**:

- `core/aggregation/bucket.py` 모듈 생성
- 시간 버킷 생성 로직

### 3. 상태 기반 룰 (B-401~403) - ⭐⭐⭐

**현재 문제**: 주소 메타데이터 관리 필요

**MPOCryptoML 활용 가능성**:

- 그래프 분석으로 주소 라이프사이클 패턴 학습
- 주소 생성일, 거래 빈도 등 특성 추출

**구현 계획**:

1. 주소 메타데이터 저장소 (Redis 또는 DB)
2. 상태 업데이트 로직
3. 시간 기반 계산 (나이, 비활성 기간)

**필요한 것**:

- `core/data/address_metadata.py` 모듈 생성
- 상태 관리 시스템

### 4. 통계 기반 룰 (B-103) - ⭐

**현재 문제**: 통계 계산 필요

**구현 계획**:

1. 거래 간격(inter-arrival) 계산
2. 표준편차 계산
3. prerequisites 체크 (최소 10개 거래)

**필요한 것**:

- 통계 계산 함수 추가
- `core/aggregation/statistics.py` 모듈 생성

## 🛠️ 구체적인 통합 계획

### Phase 1: 그래프 분석 기반 토폴로지 룰 (B-201, B-202)

```python
# core/aggregation/topology.py (새로 생성)
from typing import List, Dict, Any
import networkx as nx

class TopologyAnalyzer:
    """그래프 토폴로지 분석"""

    def build_transaction_graph(self, transactions: List[Dict]) -> nx.DiGraph:
        """트랜잭션을 그래프로 변환"""
        graph = nx.DiGraph()
        for tx in transactions:
            from_addr = tx.get('from') or tx.get('counterparty_address')
            to_addr = tx.get('to') or tx.get('target_address')
            amount = tx.get('amount_usd', 0)
            token = tx.get('asset_contract', '')

            if from_addr and to_addr:
                graph.add_edge(
                    from_addr,
                    to_addr,
                    weight=amount,
                    token=token,
                    timestamp=tx.get('timestamp')
                )
        return graph

    def detect_layering_chain(self, graph: nx.DiGraph, min_hops: int = 3) -> List[List[str]]:
        """레이어링 체인 탐지 (B-201)"""
        # 3홉 이상 경로 찾기
        chains = []
        # TODO: 경로 탐색 알고리즘 구현
        return chains

    def detect_cycle(self, graph: nx.DiGraph, length_range: tuple = (2, 3)) -> List[List[str]]:
        """순환 구조 탐지 (B-202)"""
        cycles = []
        # TODO: 순환 탐지 알고리즘 구현
        return cycles
```

### Phase 2: 버킷 기반 룰 (B-203, B-204)

```python
# core/aggregation/bucket.py (새로 생성)
from typing import List, Dict, Any
from datetime import datetime, timedelta

class BucketAnalyzer:
    """시간 버킷 분석"""

    def create_buckets(self, transactions: List[Dict], bucket_size_sec: int = 600) -> Dict[str, List[Dict]]:
        """10분 버킷으로 그룹화"""
        buckets = {}
        for tx in transactions:
            timestamp = self._parse_timestamp(tx['timestamp'])
            bucket_key = self._get_bucket_key(timestamp, bucket_size_sec)

            if bucket_key not in buckets:
                buckets[bucket_key] = []
            buckets[bucket_key].append(tx)
        return buckets

    def analyze_fan_out(self, buckets: Dict[str, List[Dict]]) -> List[Dict]:
        """팬아웃 패턴 분석 (B-203)"""
        # 같은 from에서 여러 to로 송금
        pass

    def analyze_fan_in(self, buckets: Dict[str, List[Dict]]) -> List[Dict]:
        """팬인 패턴 분석 (B-204)"""
        # 여러 from에서 같은 to로 입금
        pass
```

### Phase 3: 상태 기반 룰 (B-401~403)

```python
# core/data/address_metadata.py (새로 생성)
from typing import Dict, Optional
from datetime import datetime

class AddressMetadata:
    """주소 메타데이터 관리"""

    def __init__(self):
        self._metadata: Dict[str, Dict] = {}

    def update_address(self, address: str, tx: Dict):
        """주소 메타데이터 업데이트"""
        if address not in self._metadata:
            self._metadata[address] = {
                'first_seen': tx['timestamp'],
                'last_seen': tx['timestamp'],
                'tx_count': 0,
                'total_volume_usd': 0,
            }

        meta = self._metadata[address]
        meta['last_seen'] = tx['timestamp']
        meta['tx_count'] += 1
        meta['total_volume_usd'] += tx.get('amount_usd', 0)

    def get_age_days(self, address: str) -> Optional[int]:
        """주소 나이 (일)"""
        if address not in self._metadata:
            return None
        first_seen = self._metadata[address]['first_seen']
        # TODO: 날짜 계산
        return None
```

## 📋 MPOCryptoML 확인 필요 사항

다음 정보를 알려주시면 더 구체적인 통합 계획을 제시하겠습니다:

1. **MPOCryptoML이 legacy 코드인가요?**

   - `legacy/multi_classification/`가 MPOCryptoML인가요?
   - 아니면 별도 프로젝트인가요?

2. **어떤 기능을 활용하고 싶으신가요?**

   - 그래프 분석?
   - 패턴 학습?
   - 주소 분류?

3. **통합 방식은?**

   - 기존 모델을 그대로 사용?
   - 새로운 모듈로 재구현?
   - API로 호출?

4. **데이터 형식은?**
   - 현재 트랜잭션 데이터 형식과 호환되나요?
   - 변환이 필요한가요?

## 🚀 빠른 시작: B-201 룰 구현 예시

MPOCryptoML의 그래프 분석 코드를 활용하면:

```python
# core/aggregation/topology.py
from legacy.multi_classification.graph_individual.dataloader import TransactionDataset
import networkx as nx

class TopologyRuleEvaluator:
    def evaluate_layering_chain(self, transactions: List[Dict], target_address: str):
        """B-201: Layering Chain 탐지"""
        # 1. 그래프 구축
        graph = self._build_graph(transactions)

        # 2. 3홉 이상 경로 찾기
        paths = self._find_paths(graph, target_address, min_hops=3)

        # 3. 같은 토큰, 금액 차이 <= 5% 확인
        valid_paths = []
        for path in paths:
            if self._check_same_token(path, transactions):
                if self._check_amount_delta(path, transactions, max_delta=0.05):
                    valid_paths.append(path)

        return len(valid_paths) > 0
```

이렇게 하면 MPOCryptoML의 그래프 분석 기능을 활용하여 토폴로지 룰을 구현할 수 있습니다!
