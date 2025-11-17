# MPOCryptoML 통합 전략

## 🎯 MPOCryptoML 핵심 구성 요소

### 입력 데이터 구조

```
G = (V, E, W, T)
- V: Vertices (주소들)
- E: Edges (트랜잭션들)
- W: Weights (거래 금액, usd_value)
- T: Timestamps
```

### 탐지 패턴

1. **구조적 패턴** (Structural Patterns)

   - Fan-out: 하나에서 여러 주소로 분산
   - Fan-in: 여러 주소에서 하나로 집중
   - Gather-scatter: Fan-in + Fan-out
   - Random: 거래 발생의 무작위성
   - Stack: 방향성 경로 (directed path)
   - Bipartite: 두 레이어 구조

2. **시간/금액 패턴** (Temporal/Value Patterns)

   - NTS (Node Temporal Score?): 노드 시간 특성
   - NWS (Node Weight Score?): 노드 가중치 특성

3. **오프체인 연결성** (Off-chain Connectivity)
   - PPR (Personalized PageRank): 개인화된 페이지랭크
   - 오프체인 거래 흐름 추적

### 최종 스코어링

```
리스크 스코어 = 구조적 패턴 점수 + 시간/금액 패턴 점수 + PPR 연결성 점수
```

---

## 🔗 우리 프로젝트와의 통합 방안

### 현재 우리 프로젝트 구조

```
TRACE-X 룰 기반 스코어링
├── 단일 트랜잭션 룰 (C-001, C-003, E-101)
├── 윈도우 기반 룰 (C-004, B-101, B-102)
├── 버킷 기반 룰 (B-203, B-204)
└── 최종 리스크 스코어 = Σ(발동된 룰 점수)
```

### 통합 전략 1: 하이브리드 스코어링 (추천)

**아키텍처**:

```
최종 리스크 스코어 =
    TRACE-X 룰 점수 (70%) +
    MPOCryptoML 패턴 점수 (20%) +
    PPR 연결성 점수 (10%)
```

**구현 방법**:

1. **TRACE-X 룰 점수** (기존)

   - 규제 준수, 노출, 행동 패턴 기반
   - 0~100점 스케일

2. **MPOCryptoML 패턴 점수** (신규)

   - 구조적 패턴 탐지 결과를 점수로 변환
   - 각 패턴별 가중치 부여

3. **PPR 연결성 점수** (신규)
   - 오프체인 거래 그래프에서 PPR 계산
   - 제재 주소, 믹서 등과의 연결성 측정

**장점**:

- 규제 기반 룰의 명확성 유지
- 구조적 패턴의 강점 활용
- 오프체인 연결성 고려

---

### 통합 전략 2: 패턴 기반 룰 보강

**아키텍처**:

```
TRACE-X 룰 평가
├── 기존 룰 평가
└── MPOCryptoML 패턴 탐지 결과를 룰 점수에 반영
    ├── Fan-in/Fan-out 패턴 → B-203, B-204 점수 조정
    ├── Stack 패턴 → B-201 룰 발동
    ├── Bipartite 패턴 → 추가 점수 부여
    └── PPR 연결성 → E-102 룰 보강
```

**구현 방법**:

1. **기존 룰 점수 조정**

   ```python
   # B-203 (Fan-out) 룰
   base_score = 20
   if mpocryptml_patterns.detect_fan_out_pattern(address):
       # 패턴이 강하게 탐지되면 점수 증가
       adjusted_score = base_score * 1.5  # 30점
   ```

2. **새로운 룰 추가**
   - B-205: Strong Gather-Scatter Pattern
   - B-206: Bipartite Structure Detected
   - E-104: High PPR Connection to Sanctioned Addresses

**장점**:

- 기존 룰 시스템과 자연스럽게 통합
- 패턴 탐지 결과를 명시적으로 룰로 표현
- 해석 가능성 유지

---

### 통합 전략 3: 2단계 스코어링

**아키텍처**:

```
1단계: TRACE-X 룰 기반 스크리닝
   → 규제 준수, 명확한 위험 패턴 탐지

2단계: MPOCryptoML 패턴 분석 (선택적)
   → 1단계에서 높은 점수 나온 주소만
   → 구조적 패턴 + PPR 연결성 분석
   → 최종 스코어 조정
```

**구현 방법**:

1. **1단계**: 기존 TRACE-X 룰 평가
2. **2단계**:
   - 리스크 스코어 >= 50인 주소만 선택
   - MPOCryptoML 패턴 분석 수행
   - PPR 연결성 계산
   - 최종 스코어 조정

**장점**:

- 성능 최적화 (높은 리스크 주소만 상세 분석)
- 계산 비용 절감
- 단계별 해석 가능

---

## 🛠️ 구체적 구현 계획

### Phase 1: 구조적 패턴 통합 (현재 진행 중)

**완료**:

- ✅ Fan-in/Fan-out 패턴 탐지 (`MPOCryptoMLPatternDetector`)
- ✅ B-203, B-204 룰 구현 (버킷 기반)

**진행 중**:

- 🚧 Stack 패턴 → B-201 룰 구현
- 🚧 Bipartite 패턴 → 새 룰 추가 검토

### Phase 2: 시간/금액 패턴 통합

**필요한 것**:

- NTS (Node Temporal Score) 계산 로직
- NWS (Node Weight Score) 계산 로직

**구현 방법**:

```python
class TemporalPatternAnalyzer:
    def calculate_nts(self, address: str, graph: nx.DiGraph) -> float:
        """노드 시간 특성 점수"""
        # 거래 간격, 시간대 분포 등 분석
        pass

    def calculate_nws(self, address: str, graph: nx.DiGraph) -> float:
        """노드 가중치 특성 점수"""
        # 거래 금액 분포, 평균/중앙값 등 분석
        pass
```

### Phase 3: PPR 연결성 통합

**필요한 것**:

- Personalized PageRank 알고리즘 구현
- 오프체인 거래 그래프 구축
- 제재 주소/믹서와의 연결성 측정

**구현 방법**:

```python
class PPRConnector:
    def calculate_ppr(
        self,
        target_address: str,
        source_addresses: List[str],  # 제재 주소, 믹서 등
        graph: nx.DiGraph
    ) -> float:
        """PPR 연결성 점수 계산"""
        # NetworkX의 pagerank 활용
        # 또는 커스텀 PPR 구현
        pass
```

### Phase 4: 통합 스코어링

**구현 방법**:

```python
class HybridScorer:
    def __init__(self):
        self.rule_evaluator = RuleEvaluator()
        self.pattern_detector = MPOCryptoMLPatternDetector()
        self.ppr_connector = PPRConnector()

    def calculate_final_score(
        self,
        address: str,
        transactions: List[Dict]
    ) -> Dict[str, Any]:
        # 1. TRACE-X 룰 점수
        rule_score = self.rule_evaluator.evaluate(...)

        # 2. MPOCryptoML 패턴 점수
        pattern_score = self.pattern_detector.analyze_address_patterns(address)

        # 3. PPR 연결성 점수
        ppr_score = self.ppr_connector.calculate_ppr(address, ...)

        # 4. 통합 점수
        final_score = (
            rule_score * 0.7 +
            pattern_score * 0.2 +
            ppr_score * 0.1
        )

        return {
            "final_score": final_score,
            "rule_score": rule_score,
            "pattern_score": pattern_score,
            "ppr_score": ppr_score,
            "breakdown": {...}
        }
```

---

## 📋 통합 우선순위

### 높은 우선순위 (즉시 구현 가능)

1. **Stack 패턴 → B-201 룰** ⭐⭐⭐

   - `detect_stack_pattern()` 활용
   - 토큰 필터링 추가
   - 예상 시간: 반나절

2. **Bipartite 패턴 → 새 룰 추가** ⭐⭐
   - `detect_bipartite_pattern()` 활용
   - 예상 시간: 반나절

### 중간 우선순위 (구조 개선 필요)

3. **PPR 연결성 계산** ⭐⭐⭐

   - NetworkX pagerank 활용
   - 제재 주소/믹서와의 연결성 측정
   - 예상 시간: 1일

4. **시간/금액 패턴 (NTS, NWS)** ⭐⭐⭐
   - 논문에서 정확한 정의 확인 필요
   - 예상 시간: 1일

### 낮은 우선순위 (복잡한 구조 필요)

5. **하이브리드 스코어링 시스템** ⭐⭐⭐⭐
   - 전체 아키텍처 재설계
   - 예상 시간: 2-3일

---

## 💡 추천 통합 방식

**전략 1 (하이브리드 스코어링) + 전략 2 (패턴 기반 룰 보강) 조합**

1. **기존 룰 시스템 유지** (규제 준수, 명확성)
2. **MPOCryptoML 패턴을 보조 지표로 활용**
   - 룰 점수 조정
   - 새 룰 추가
3. **PPR 연결성을 추가 점수로 반영**
   - E-102 룰 보강
   - 새 룰 추가 (E-104 등)

**장점**:

- 기존 시스템과 자연스러운 통합
- 점진적 개선 가능
- 해석 가능성 유지
- 성능과 정확도 균형

---

## 🔍 다음 단계

1. **논문 재검토**: NTS, NWS, PPR의 정확한 정의 확인
2. **프로토타입 구현**: Stack 패턴 → B-201 룰
3. **PPR 알고리즘 구현**: 오프체인 연결성 측정
4. **통합 테스트**: 하이브리드 스코어링 검증
