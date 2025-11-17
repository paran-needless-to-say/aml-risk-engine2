# 성능 최적화 전략: 기능 분리

## 🚨 문제점

### 현재 구조의 성능 이슈

**시나리오**: 주소 A 분석

1. **데이터 수집**: 3홉까지 거래 데이터 조회
   - 0홉: A의 직접 거래 (예: 100개)
   - 1홉: 연결된 주소들의 거래 (예: 1,000개)
   - 2홉: 2단계 연결 거래 (예: 10,000개)
   - 3홉: 3단계 연결 거래 (예: 100,000개)
   - **총 거래 수**: 111,100개

2. **룰 평가 과정**:
   - 기본 룰 평가 (C-001, C-003, C-004, E-101, B-101, B-102 등)
   - **그래프 구조 분석** (B-201, B-202)
     - 111,100개 거래로 그래프 구축
     - DFS로 경로 탐색
     - 순환 구조 탐지
   - **예상 시간**: 수 초 ~ 수십 초

3. **문제**:
   - 사용자는 빠른 응답을 기대 (1-2초)
   - 그래프 구조 분석은 매우 느림
   - 모든 룰을 한 번에 평가하면 성능 저하

---

## 💡 해결 방안: 기능 분리

### 방안 1: API 엔드포인트 분리 (추천)

#### 기본 스코어링 (빠름)

**엔드포인트**: `POST /api/analyze/address`

**특징**:
- 기본 룰만 평가 (그래프 구조 분석 제외)
- 빠른 응답 (1-2초)
- 실시간 탐지에 적합

**평가하는 룰**:
- ✅ C-001: Sanction Direct Touch
- ✅ C-003: High-Value Single Transfer
- ✅ C-004: High-Value Repeated Transfer
- ✅ E-101: Mixer Direct Exposure
- ✅ E-102: Indirect Sanctions Exposure (PPR)
- ✅ B-101: Burst (10m)
- ✅ B-102: Rapid Sequence (1m)
- ✅ B-103: Inter-arrival Std High

**제외하는 룰**:
- ❌ B-201: Layering Chain (그래프 구조 분석)
- ❌ B-202: Cycle (그래프 구조 분석)

#### 고급 분석 (느림)

**엔드포인트**: `POST /api/analyze/address/advanced`

**특징**:
- 모든 룰 평가 (그래프 구조 분석 포함)
- 느린 응답 (5-30초)
- 수동 탐지/심층 분석에 적합

**평가하는 룰**:
- 기본 룰 + 그래프 구조 분석 룰
- ✅ B-201: Layering Chain
- ✅ B-202: Cycle

---

### 방안 2: 옵션 플래그 방식

**엔드포인트**: `POST /api/analyze/address`

**요청 예시**:
```json
{
  "address": "0xABC...",
  "chain": "ethereum",
  "transactions": [...],
  "options": {
    "include_topology": false,  // 기본값: false (빠름)
    "include_ppr": true,        // PPR 분석 포함
    "max_hops": 1               // 기본값: 1 (1홉만)
  }
}
```

**동작**:
- `include_topology: false` → 기본 룰만 평가 (빠름)
- `include_topology: true` → 그래프 구조 분석 포함 (느림)
- `max_hops: 1` → 1홉만 조회 (빠름)
- `max_hops: 3` → 3홉까지 조회 (느림)

---

### 방안 3: 비동기 처리

**엔드포인트**:
- `POST /api/analyze/address` → 즉시 기본 스코어 반환
- `POST /api/analyze/address/async` → 작업 큐에 추가, 나중에 결과 조회

**동작 흐름**:
1. 클라이언트: `/api/analyze/address` 호출
2. 서버: 기본 스코어 즉시 반환 (1-2초)
3. 서버: 백그라운드에서 그래프 구조 분석 시작
4. 클라이언트: `/api/analyze/address/{job_id}/status`로 상태 확인
5. 클라이언트: 완료되면 `/api/analyze/address/{job_id}/result`로 결과 조회

**장점**:
- 빠른 초기 응답
- 복잡한 분석은 백그라운드 처리
- 사용자 경험 향상

**단점**:
- 큐 시스템 필요 (Redis, Celery 등)
- 구현 복잡도 증가

---

## 🎯 추천 방안: 하이브리드 접근

### 1단계: 기본 스코어링 (즉시)

**엔드포인트**: `POST /api/analyze/address`

**특징**:
- 기본 룰만 평가
- 1홉 데이터만 사용
- 빠른 응답 (1-2초)

**응답 예시**:
```json
{
  "target_address": "0xABC...",
  "risk_score": 45,
  "risk_level": "medium",
  "fired_rules": [
    {"rule_id": "C-001", "score": 30},
    {"rule_id": "E-101", "score": 15}
  ],
  "analysis_type": "basic",
  "advanced_analysis_available": true
}
```

### 2단계: 고급 분석 (옵션)

**엔드포인트**: `POST /api/analyze/address/advanced`

**특징**:
- 모든 룰 평가
- 3홉 데이터 사용
- 느린 응답 (5-30초)

**응답 예시**:
```json
{
  "target_address": "0xABC...",
  "risk_score": 78,
  "risk_level": "high",
  "fired_rules": [
    {"rule_id": "C-001", "score": 30},
    {"rule_id": "E-101", "score": 15},
    {"rule_id": "B-201", "score": 25},  // 그래프 구조 분석
    {"rule_id": "B-202", "score": 30}   // 그래프 구조 분석
  ],
  "analysis_type": "advanced",
  "topology_patterns": {
    "layering_chains": [...],
    "cycles": [...]
  }
}
```

---

## 📊 성능 비교

### 시나리오: 주소 A 분석 (3홉 데이터 111,100개 거래)

| 방식 | 응답 시간 | 평가 룰 | 사용 사례 |
|------|----------|---------|-----------|
| **현재 (모든 룰)** | 10-30초 | 모든 룰 | ❌ 너무 느림 |
| **기본 스코어링** | 1-2초 | 기본 룰만 | ✅ 실시간 탐지 |
| **고급 분석** | 5-30초 | 모든 룰 | ✅ 수동 탐지/심층 분석 |
| **비동기** | 즉시 + 나중에 | 모든 룰 | ✅ 대용량 분석 |

---

## 🔧 구현 방안

### 1. AddressAnalyzer 분리

```python
class AddressAnalyzer:
    def analyze_address(
        self,
        address: str,
        chain: str,
        transactions: List[Dict],
        analysis_type: str = "basic"  # "basic" or "advanced"
    ) -> AddressAnalysisResult:
        if analysis_type == "basic":
            return self._analyze_basic(address, chain, transactions)
        else:
            return self._analyze_advanced(address, chain, transactions)
    
    def _analyze_basic(self, ...):
        # 기본 룰만 평가
        # B-201, B-202 제외
        pass
    
    def _analyze_advanced(self, ...):
        # 모든 룰 평가
        # B-201, B-202 포함
        pass
```

### 2. RuleEvaluator 분리

```python
class RuleEvaluator:
    def evaluate_single_transaction(
        self,
        tx_data: Dict,
        include_topology: bool = False  # 기본값: False
    ) -> List[Dict]:
        # ...
        if not include_topology:
            # B-201, B-202 건너뛰기
            if rule_id in ["B-201", "B-202"]:
                continue
        # ...
```

### 3. API 라우트 분리

```python
# 기본 스코어링
@address_analysis_bp.route("/address", methods=["POST"])
def analyze_address():
    # analysis_type = "basic"
    # include_topology = False
    pass

# 고급 분석
@address_analysis_bp.route("/address/advanced", methods=["POST"])
def analyze_address_advanced():
    # analysis_type = "advanced"
    # include_topology = True
    pass
```

---

## 📋 사용 사례별 권장사항

### 1. 실시간 탐지 (CEX 입출금)

**사용**: 기본 스코어링
- 빠른 응답 필요 (1-2초)
- 기본 룰만으로도 충분
- 그래프 구조 분석 불필요

### 2. 수동 탐지 (주소 조사)

**사용**: 고급 분석
- 정확도 중요
- 시간 여유 있음 (5-30초)
- 그래프 구조 분석 필요

### 3. 대시보드 (오늘의 알림)

**사용**: 기본 스코어링
- 빠른 로딩 필요
- 기본 룰만으로 충분
- 고급 분석은 클릭 시 별도 요청

---

## ✅ 결론

**추천 방안**: **하이브리드 접근**

1. **기본 스코어링** (`/api/analyze/address`)
   - 빠른 응답 (1-2초)
   - 기본 룰만 평가
   - 실시간 탐지에 적합

2. **고급 분석** (`/api/analyze/address/advanced`)
   - 느린 응답 (5-30초)
   - 모든 룰 평가
   - 수동 탐지에 적합

**장점**:
- 사용 사례별 최적화
- 빠른 기본 응답
- 필요 시 심층 분석 가능
- 구현 간단

