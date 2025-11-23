# TRACE-X 리스크 스코어링 룰북 (상세 설명)

## 📋 목차

1. [개요](#개요)
2. [룰 축(Axis) 설명](#룰-축axis-설명)
3. [C축 (Compliance) 룰](#c축-compliance-룰)
4. [E축 (Exposure) 룰](#e축-exposure-룰)
5. [B축 (Behavior) 룰](#b축-behavior-룰)
6. [미구현 룰](#미구현-룰)
7. [룰 평가 로직](#룰-평가-로직)

---

## 개요

TRACE-X 룰북은 블록체인 주소의 리스크를 평가하기 위한 22개의 룰로 구성되어 있습니다. 각 룰은 **C (Compliance)**, **E (Exposure)**, **B (Behavior)** 3가지 축으로 분류됩니다.

- **총 룰 수**: 22개
- **실제 구현**: 18개 (Basic), 20개 (Advanced)
- **미구현**: 4개 (State 룰)

---

## 룰 축(Axis) 설명

### C축 (Compliance) - 규정 준수
제재 리스트, 고액 거래 등 **규정 준수 관련 리스크**를 평가합니다.
- **목적**: AML 규정 위반 가능성 탐지
- **주요 요소**: SDN 리스트, 고액 거래, VASP 관할권

### E축 (Exposure) - 위험 노출
믹서, 브릿지, 사기 주소 등 **위험 요소에 대한 직접적/간접적 노출**을 평가합니다.
- **목적**: 세탁 도구나 불법 자금 노출 탐지
- **주요 요소**: Mixer, Bridge, Scam, 제재 주소 노출

### B축 (Behavior) - 행동 패턴
거래 패턴, 그래프 구조 등 **의심스러운 행동 패턴**을 평가합니다.
- **목적**: 머니 세탁 전형적 패턴 탐지
- **주요 요소**: Burst, Cycle, Layering Chain, Fan-in/out

---

## C축 (Compliance) 룰

### C-001: Sanction Direct Touch

**이름**: Sanction Direct Touch  
**축**: C (Compliance)  
**Severity**: HIGH  
**점수**: 30점  
**구현 상태**: ✅ 구현됨

#### 📝 설명
OFAC SDN (Specially Designated Nationals) 리스트에 등재된 주소와 **직접적인 거래**를 탐지합니다. 이는 가장 심각한 규정 위반 위험 신호입니다.

#### 🔍 발동 조건
1. **매칭 조건** (둘 중 하나):
   - `from` 주소가 `SDN_LIST`에 포함
   - `to` 주소가 `SDN_LIST`에 포함
2. **조건** (모두 만족):
   - 거래 금액 (`usd_value`) ≥ 1 USD

#### ⚠️ 예외 사항
다음 중 하나라도 해당되면 룰 발동 안 함:
- `from` 주소에 `CEX_INTERNAL` 태그가 true
- `to` 주소에 `CEX_INTERNAL` 태그가 true

**목적**: 거래소 내부 거래는 제외

#### 💻 구현 로직
```python
# evaluator.py _eval_single_match()
if list_name == "SDN_LIST":
    # 1. 리스트 직접 확인
    if value in target_list:
        return True
    # 2. 백엔드 플래그 확인
    if tx_data.get("is_sanctioned", False):
        return True
```

#### 📊 예시
```
거래: 0xSANCTIONED_ADDRESS → 0xTARGET_ADDRESS
금액: 5,000 USD
결과: C-001 발동 (30점) ✅
```

---

### C-002: High-Risk Jurisdiction VASP

**이름**: High-Risk Jurisdiction VASP  
**축**: C (Compliance)  
**Severity**: MEDIUM  
**점수**: 20점  
**구현 상태**: ✅ 구현됨 (조건부: 백엔드에서 counterparty 태그 필요)

#### 📝 설명
고위험 관할권(이란, 러시아, 북한)의 VASP(가상자산 서비스 제공자)와의 거래를 탐지합니다.

#### 🔍 발동 조건
1. **매칭 조건**:
   - `counterparty` 주소의 `country` 태그가 다음 중 하나:
     - `IR` (이란)
     - `RU` (러시아)
     - `KP` (북한)
2. **조건**:
   - `counterparty`의 `type` 태그가 `VASP`

#### ⚠️ 예외 사항
- `counterparty`에 `safe_vasp` 태그가 true면 발동 안 함

#### 💻 구현 로직
```python
# tag 기반 조건 평가
if tx_data.get("counterparty", {}).get("country") in ["IR", "RU", "KP"]:
    if tx_data.get("counterparty", {}).get("type") == "VASP":
        if not tx_data.get("counterparty", {}).get("safe_vasp"):
            # 룰 발동
```

#### 📊 예시
```
거래: 0xTARGET → 이란 거래소 주소
상대방 타입: VASP
상대방 국가: IR
결과: C-002 발동 (20점) ✅
```

---

### C-003: High-Value Single Transfer

**이름**: High-Value Single Transfer  
**축**: C (Compliance)  
**Severity**: MEDIUM  
**점수**: 25점  
**구현 상태**: ✅ 구현됨

#### 📝 설명
단일 거래에서 **고액 거래**를 탐지합니다. AML 규정상 고액 거래는 보고 대상입니다.

#### 🔍 발동 조건
- 거래 금액 (`usd_value`) ≥ 3,000 USD

#### ⚠️ 예외 사항
- `from` 또는 `to` 주소에 `CEX_INTERNAL` 태그가 true면 발동 안 함

#### 💻 구현 로직
```python
# 단일 트랜잭션 룰 평가
if float(tx_data.get("usd_value", 0)) >= 3000:
    if not (tx_data.get("from", {}).get("CEX_INTERNAL") or 
            tx_data.get("to", {}).get("CEX_INTERNAL")):
        # 룰 발동
```

#### 📊 예시
```
거래: 0xSENDER → 0xTARGET
금액: 5,000 USD (단일 거래)
결과: C-003 발동 (25점) ✅
```

---

### C-004: High-Value Repeated Transfer (24h)

**이름**: High-Value Repeated Transfer (24h)  
**축**: C (Compliance)  
**Severity**: MEDIUM  
**점수**: 20점  
**구현 상태**: ✅ 구현됨 (윈도우 룰)

#### 📝 설명
24시간 내에 **고액 거래가 반복**되는 패턴을 탐지합니다. Structuring (금액 분할) 의심 신호입니다.

#### 🔍 발동 조건
**윈도우**: 24시간 (86,400초)  
**그룹화**: 주소별

**집계 조건** (모두 만족):
- 거래 금액 합계 ≥ 5,000 USD
- 거래 횟수 ≥ 2회
- 각 거래 금액 ≥ 1,000 USD

#### ⚠️ 예외 사항
- 주소에 `MM_BOT` (Market Maker Bot) 태그가 true
- 주소에 `CEX_INTERNAL` 태그가 true

#### 💻 구현 로직
```python
# aggregation/window.py
window = WindowEvaluator()
# 24시간 윈도우에서 주소별 거래 그룹화
transactions = window.get_transactions_in_window(
    address, 
    duration_sec=86400
)
# 집계 조건 확인
total_usd = sum(tx["usd_value"] for tx in transactions)
count = len(transactions)
min_usd = min(tx["usd_value"] for tx in transactions)

if total_usd >= 5000 and count >= 2 and min_usd >= 1000:
    # 룰 발동
```

#### 📊 예시
```
주소: 0xTARGET
거래 1: +3,000 USD (2025-01-01 10:00)
거래 2: +2,500 USD (2025-01-01 18:00)
합계: 5,500 USD (2회, 모두 ≥ 1,000 USD)
결과: C-004 발동 (20점) ✅
```

---

## E축 (Exposure) 룰

### E-101: Mixer Direct Exposure

**이름**: Mixer Direct Exposure  
**축**: E (Exposure)  
**Severity**: HIGH  
**점수**: 32점  
**구현 상태**: ✅ 구현됨

#### 📝 설명
믹서(Mixer/Tumbler) 서비스에서 **직접 유입**된 자금을 탐지합니다. 믹서는 익명성 강화 도구로 세탁에 악용됩니다.

#### 🔍 발동 조건
1. **매칭 조건**:
   - `from` 주소가 `MIXER_LIST`에 포함 (또는 `is_mixer` 플래그가 true)
2. **조건**:
   - 거래 금액 (`usd_value`) ≥ 20 USD

#### ⚠️ 예외 사항
- 주소에 `REWARD_PAYOUT` 태그가 true (리워드 지급은 정상적일 수 있음)

#### 💻 구현 로직
```python
# evaluator.py _eval_single_match()
if list_name == "MIXER_LIST":
    # 1. 리스트 직접 확인
    if value in target_list:
        return True
    # 2. 백엔드 플래그 확인
    if tx_data.get("is_mixer", False):
        return True
```

#### 📊 예시
```
거래: 0xMIXER_SERVICE → 0xTARGET_ADDRESS
금액: 100 USD
결과: E-101 발동 (32점) ✅
```

---

### E-102: Indirect Sanctions Exposure (≤2 hops)

**이름**: Indirect Sanctions Exposure (≤2 hops)  
**축**: E (Exposure)  
**Severity**: HIGH  
**점수**: 39점 (가장 높은 점수)  
**구현 상태**: ✅ 구현됨 (PPR 기반)

#### 📝 설명
제재 주소와 **간접적으로 연결**된 경우를 탐지합니다. PPR (Personalized PageRank) 알고리즘으로 2-hop 이내 연결성을 계산합니다.

#### 🔍 발동 조건
1. **매칭 조건**:
   - PPR 값 ≥ 0.05 (간접 연결성 임계값)
2. **조건**:
   - 거래 금액 (`usd_value`) ≥ 40 USD

#### ⚠️ 예외 사항
- 주소에 `CEX_INTERNAL` 태그가 true

#### 💻 구현 로직
```python
# evaluator.py _evaluate_e102_with_ppr()
# 1. 트랜잭션 히스토리로 그래프 구축
graph = build_graph_from_history(address_history)

# 2. SDN 주소 리스트 준비
sdn_addresses = lists.get("SDN_LIST", set())

# 3. PPR 계산
ppr_result = ppr_connector.calculate_connection_risk(
    target_address,
    graph,
    sdn_addresses
)

# 4. 임계값 체크
if ppr_result["total_ppr"] >= 0.05:
    # 룰 발동
```

#### 📊 예시
```
경로: 0xSANCTIONED → 0xINTERMEDIARY → 0xTARGET
PPR 값: 0.08 (0.05 이상)
결과: E-102 발동 (39점) ✅
```

---

### E-103: Counterparty Quality Risk

**이름**: Counterparty Quality Risk  
**축**: E (Exposure)  
**Severity**: MEDIUM  
**점수**: 19점  
**구현 상태**: ⚠️ 조건부 (백엔드 데이터 필요)

#### 📝 설명
상대방 주소의 리스크 스코어가 높은 경우를 탐지합니다. 높은 리스크 주소와의 거래는 위험 신호입니다.

#### 🔍 발동 조건
- `counterparty.risk_score` ≥ 0.7 (70점 이상)

#### 💻 구현 로직
```python
# 백엔드에서 counterparty.risk_score 제공 필요
if tx_data.get("counterparty", {}).get("risk_score", 0) >= 0.7:
    # 룰 발동
```

#### 📊 예시
```
거래: 0xHIGH_RISK_ADDRESS (risk_score: 0.85) → 0xTARGET
결과: E-103 발동 (19점) ✅
```

**참고**: 현재는 백엔드에서 `counterparty.risk_score`를 제공해야 작동합니다.

---

### E-104: Bridge Direct Exposure

**이름**: Bridge Direct Exposure  
**축**: E (Exposure)  
**Severity**: MEDIUM  
**점수**: 19점  
**구현 상태**: ✅ 구현됨

#### 📝 설명
브릿지(Bridge) 컨트랙트와 직접 거래한 경우를 탐지합니다. 브릿지는 자금 이전 경로를 복잡하게 만듭니다.

#### 🔍 발동 조건
1. **매칭 조건** (둘 중 하나):
   - `from` 주소가 `BRIDGE_LIST`에 포함
   - `to` 주소가 `BRIDGE_LIST`에 포함
2. **조건**:
   - 거래 금액 (`usd_value`) ≥ 20 USD

#### ⚠️ 예외 사항
- `from` 또는 `to` 주소에 `CEX_INTERNAL` 태그가 true

#### 💻 구현 로직
```python
# BRIDGE_LIST에서 확인
if tx_data.get("from") in bridge_list or tx_data.get("to") in bridge_list:
    if float(tx_data.get("usd_value", 0)) >= 20:
        # 룰 발동
```

#### 📊 예시
```
거래: 0xBRIDGE_CONTRACT → 0xTARGET
금액: 50 USD
결과: E-104 발동 (19점) ✅
```

---

### E-105: Scam Direct Exposure

**이름**: Scam Direct Exposure  
**축**: E (Exposure)  
**Severity**: MEDIUM  
**점수**: 26점  
**구현 상태**: ✅ 구현됨

#### 📝 설명
사기 주소와 직접 거래한 경우를 탐지합니다.

#### 🔍 발동 조건
1. **매칭 조건** (둘 중 하나):
   - `from` 주소가 `SCAM_LIST`에 포함 (또는 `is_known_scam` 플래그가 true)
   - `to` 주소가 `SCAM_LIST`에 포함
2. **조건**:
   - 거래 금액 (`usd_value`) ≥ 200 USD

#### ⚠️ 예외 사항
- `from` 또는 `to` 주소에 `CEX_INTERNAL` 태그가 true

#### 💻 구현 로직
```python
# SCAM_LIST에서 확인
if tx_data.get("from") in scam_list or tx_data.get("to") in scam_list:
    if float(tx_data.get("usd_value", 0)) >= 200:
        # 룰 발동
```

#### 📊 예시
```
거래: 0xSCAM_ADDRESS → 0xTARGET
금액: 500 USD
결과: E-105 발동 (26점) ✅
```

---

## B축 (Behavior) 룰

### B-101: Burst (10m)

**이름**: Burst (10m)  
**축**: B (Behavior)  
**Severity**: MEDIUM  
**점수**: 15점  
**구현 상태**: ✅ 구현됨 (윈도우 룰)

#### 📝 설명
10분 내에 **2회 이상** 거래가 발생하는 패턴을 탐지합니다. 짧은 시간에 집중된 거래는 의심스러울 수 있습니다.

#### 🔍 발동 조건
**윈도우**: 10분 (600초)  
**그룹화**: 주소별  
**쿨다운**: 30분 (1,800초) - 같은 패턴 중복 발동 방지

**집계 조건**:
- 거래 횟수 ≥ 2회

#### ⚠️ 예외 사항
- 주소에 `CEX_INTERNAL` 또는 `MM_BOT` 태그가 true

#### 💻 구현 로직
```python
# aggregation/window.py
window = WindowEvaluator()
transactions = window.get_transactions_in_window(
    address,
    duration_sec=600,  # 10분
    cooldown_sec=1800  # 30분 쿨다운
)

if len(transactions) >= 2:
    # 룰 발동
```

#### 📊 예시
```
주소: 0xTARGET
거래 1: 2025-01-01 10:00:00
거래 2: 2025-01-01 10:05:00 (5분 후)
결과: B-101 발동 (15점) ✅
```

---

### B-102: Rapid Sequence (1m)

**이름**: Rapid Sequence (1m)  
**축**: B (Behavior)  
**Severity**: HIGH  
**점수**: 20점  
**구현 상태**: ✅ 구현됨 (윈도우 룰)

#### 📝 설명
1분 내에 **3회 이상** 거래가 발생하는 패턴을 탐지합니다. 매우 빠른 연속 거래는 봇이나 자동화된 거래를 나타낼 수 있습니다.

#### 🔍 발동 조건
**윈도우**: 1분 (60초)  
**그룹화**: 주소별  
**쿨다운**: 15분 (900초)

**집계 조건**:
- 거래 횟수 ≥ 3회

#### ⚠️ 예외 사항
- 주소에 `CEX_INTERNAL` 또는 `MM_BOT` 태그가 true

#### 📊 예시
```
주소: 0xTARGET
거래 1: 2025-01-01 10:00:00
거래 2: 2025-01-01 10:00:20 (20초 후)
거래 3: 2025-01-01 10:00:45 (45초 후)
결과: B-102 발동 (20점) ✅
```

---

### B-103: Inter-arrival Std High

**이름**: Inter-arrival Std High  
**축**: B (Behavior)  
**Severity**: LOW  
**점수**: 10점  
**구현 상태**: ✅ 구현됨 (통계 계산)

#### 📝 설명
거래 간격의 **표준편차가 높은** 경우를 탐지합니다. 불규칙한 거래 패턴은 의심스러울 수 있습니다.

#### 🔍 발동 조건
**Prerequisites** (전제 조건):
- 최소 5개 거래 필요

**조건** (모두 만족):
- 거래 간격 표준편차 (`interarrival_std`) ≥ 1.5
- 거래 금액 (`usd_value`) ≥ 20 USD

#### 💻 구현 로직
```python
# evaluator.py _evaluate_b103_with_stats()
# 1. Prerequisites 체크
if len(all_transactions) < 5:
    return False

# 2. 거래 간격 표준편차 계산
interarrival_std = stats_calculator.calculate_interarrival_std(
    all_transactions
)

# 3. 조건 확인
if interarrival_std >= 1.5 and tx_data.get("usd_value", 0) >= 20:
    # 룰 발동
```

#### 📊 예시
```
주소: 0xTARGET
거래 1: 10:00
거래 2: 10:30 (30분 후)
거래 3: 11:05 (35분 후)
거래 4: 14:00 (3시간 후)
거래 5: 14:10 (10분 후)
표준편차: 1.8 (높음)
결과: B-103 발동 (10점) ✅
```

---

### B-201: Layering Chain (same token)

**이름**: Layering Chain (same token)  
**축**: B (Behavior)  
**Severity**: HIGH  
**점수**: 25점  
**구현 상태**: ✅ 구현됨 (Advanced 모드 전용)

#### 📝 설명
**레이어링(Layering)** 패턴을 탐지합니다. 자금이 여러 주소를 거쳐 이동하면서 추적을 어렵게 만드는 세탁 기법입니다.

#### 🔍 발동 조건
**Topology 조건** (모두 만족):
- 같은 토큰 사용 (`same_token: true`)
- 체인 길이 ≥ 3-hop (`hop_length_gte: 3`)
- 각 홉 금액 변동 ≤ 5% (`hop_amount_delta_pct_lte: 5`)
- 최소 금액 ≥ 100 USD (`min_usd_value: 100`)

#### ⚠️ 모드 제한
- **Basic 모드**: 발동 안 함 (성능 최적화)
- **Advanced 모드**: 발동됨

#### 💻 구현 로직
```python
# aggregation/topology.py
def evaluate_layering_chain(address, transactions, spec):
    # 1. 그래프 구축
    graph = build_graph(transactions)
    
    # 2. 같은 토큰 필터링
    same_token_transactions = filter_same_token(transactions)
    
    # 3. 3-hop 이상 체인 탐지
    chains = find_chains(address, graph, min_hops=3)
    
    # 4. 금액 변동 확인 (각 홉 5% 이내)
    for chain in chains:
        if all(is_amount_similar(hop1, hop2, delta_pct=5) 
               for hop1, hop2 in zip(chain[:-1], chain[1:])):
            return True
    
    return False
```

#### 📊 예시
```
경로: A → B → C → D (3-hop)
토큰: USDT (같은 토큰)
금액: 1000 → 990 → 985 USD (5% 이내 변동)
결과: B-201 발동 (25점) ✅ (Advanced 모드)
```

---

### B-202: Cycle (length 2-3, same token)

**이름**: Cycle (length 2-3, same token)  
**축**: B (Behavior)  
**Severity**: HIGH  
**점수**: 30점  
**구현 상태**: ✅ 구현됨 (Advanced 모드 전용)

#### 📝 설명
**사이클(Cycle)** 패턴을 탐지합니다. 자금이 같은 주소들 사이를 순환하는 의심스러운 패턴입니다.

#### 🔍 발동 조건
**Topology 조건** (모두 만족):
- 같은 토큰 사용 (`same_token: true`)
- 사이클 길이 2 또는 3 (`cycle_length_in: [2, 3]`)
- 사이클 총 금액 ≥ 100 USD (`cycle_total_usd_gte: 100`)

#### ⚠️ 모드 제한
- **Basic 모드**: 발동 안 함
- **Advanced 모드**: 발동됨

#### 💻 구현 로직
```python
# aggregation/topology.py
def evaluate_cycle(address, transactions, spec):
    # 1. 그래프 구축
    graph = build_graph(transactions)
    
    # 2. 2-hop 또는 3-hop 사이클 탐지
    cycles = find_cycles(graph, lengths=[2, 3])
    
    # 3. 같은 토큰 & 총 금액 확인
    for cycle in cycles:
        if is_same_token(cycle) and cycle_total_usd(cycle) >= 100:
            return True
    
    return False
```

#### 📊 예시
```
사이클: A → B → A (2-hop)
토큰: USDT (같은 토큰)
총 금액: 500 USD
결과: B-202 발동 (30점) ✅ (Advanced 모드)
```

---

### B-203: Fan-out (10m bucket)

**이름**: Fan-out (10m bucket)  
**축**: B (Behavior)  
**Severity**: MEDIUM  
**점수**: 20점  
**구현 상태**: ✅ 구현됨 (버킷 룰)

#### 📝 설명
10분 버킷 내에 **한 주소에서 여러 주소로 분산**되는 패턴을 탐지합니다. 자금 분산의 전형적 패턴입니다.

#### 🔍 발동 조건
**버킷**: 10분 (600초)  
**그룹화**: 체인 ID, 토큰, `from` 주소별

**집계 조건** (모두 만족):
- 서로 다른 `to` 주소 수 ≥ 5개 (`distinct_gte: to >= 5`)
- 총 금액 ≥ 1,000 USD (`sum_gte: usd_value >= 1000`)
- 각 거래 금액 ≥ 100 USD (`every_gte: usd_value >= 100`)

#### 💻 구현 로직
```python
# aggregation/bucket.py
bucket = BucketEvaluator()
# 10분 버킷으로 그룹화
grouped = bucket.group_by_bucket(
    transactions,
    size_sec=600,
    group_by=["chain_id", "token", "from"]
)

for group in grouped:
    distinct_to = len(set(tx["to"] for tx in group))
    total_usd = sum(tx["usd_value"] for tx in group)
    min_usd = min(tx["usd_value"] for tx in group)
    
    if distinct_to >= 5 and total_usd >= 1000 and min_usd >= 100:
        # 룰 발동
```

#### 📊 예시
```
From: 0xSENDER
10분 내 거래:
- → 0xA (200 USD)
- → 0xB (150 USD)
- → 0xC (180 USD)
- → 0xD (170 USD)
- → 0xE (300 USD)
서로 다른 주소: 5개
총 금액: 1,000 USD
결과: B-203 발동 (20점) ✅
```

---

### B-204: Fan-in (10m bucket)

**이름**: Fan-in (10m bucket)  
**축**: B (Behavior)  
**Severity**: MEDIUM  
**점수**: 20점  
**구현 상태**: ✅ 구현됨 (버킷 룰)

#### 📝 설명
10분 버킷 내에 **여러 주소에서 한 주소로 집중**되는 패턴을 탐지합니다. 자금 집중의 전형적 패턴입니다.

#### 🔍 발동 조건
**버킷**: 10분 (600초)  
**그룹화**: 체인 ID, 토큰, `to` 주소별

**집계 조건** (모두 만족):
- 서로 다른 `from` 주소 수 ≥ 5개 (`distinct_gte: from >= 5`)
- 총 금액 ≥ 1,000 USD
- 각 거래 금액 ≥ 100 USD

#### 📊 예시
```
To: 0xTARGET
10분 내 거래:
- 0x1 → (200 USD)
- 0x2 → (150 USD)
- 0x3 → (180 USD)
- 0x4 → (170 USD)
- 0x5 → (300 USD)
서로 다른 주소: 5개
총 금액: 1,000 USD
결과: B-204 발동 (20점) ✅
```

---

### B-501: High-Value Buckets

**이름**: High-Value Buckets  
**축**: B (Behavior)  
**Severity**: MEDIUM  
**점수**: 동적 점수 (3~30점)  
**구현 상태**: ✅ 구현됨 (동적 점수)

#### 📝 설명
거래 금액에 따라 **동적으로 점수**를 부여합니다. 고액 거래일수록 높은 점수를 받습니다.

#### 🔍 발동 조건
거래 금액 (`usd_value`)에 따라 점수가 결정됩니다:

| 금액 범위 | 점수 |
|----------|------|
| 1,000 ~ 5,000 USD | 3점 |
| 5,000 ~ 10,000 USD | 6점 |
| 10,000 ~ 50,000 USD | 9점 |
| 50,000 ~ 250,000 USD | 14점 |
| 250,000 ~ 1,000,000 USD | 21점 |
| ≥ 1,000,000 USD | 30점 |

#### 💻 구현 로직
```python
# evaluator.py 172-198줄
buckets_spec = rule.get("buckets")
field = buckets_spec.get("field", "usd_value")
ranges = buckets_spec.get("ranges", [])
value = float(tx_data.get(field, 0))

# 범위에 맞는 점수 찾기
dynamic_score = 0
for range_spec in ranges:
    min_val = range_spec.get("min", 0)
    max_val = range_spec.get("max", float('inf'))
    if min_val <= value < max_val:
        dynamic_score = range_spec.get("score", 0)
        break

if dynamic_score > 0:
    # 룰 발동
```

#### 📊 예시
```
거래 금액: 15,000 USD
범위: 10,000 ~ 50,000 USD
결과: B-501 발동 (9점) ✅
```

---

### B-502: Structuring — Rounded Value Repetition (24h outgoing)

**이름**: Structuring — Rounded Value Repetition (24h outgoing)  
**축**: B (Behavior)  
**Severity**: LOW  
**점수**: 10점  
**구현 상태**: ✅ 구현됨 (윈도우 룰)

#### 📝 설명
24시간 내에 **반올림된 금액이 반복**되는 패턴을 탐지합니다. Structuring (금액 분할) 의심 신호입니다.

#### 🔍 발동 조건
**윈도우**: 24시간 (86,400초)  
**그룹화**: 주소별, 방향: outgoing (송금)

**집계 조건**:
1. 거래 중 하나라도 ≥ 10,000,000 USD
2. 반올림된 금액으로 그룹화
3. 각 그룹에서:
   - 거래 횟수 ≥ 5회
   - 총 금액 ≥ 10,000 USD

#### 💻 구현 로직
```python
# 윈도우에서 outgoing 거래만 필터링
outgoing_txs = [tx for tx in transactions if tx["from"] == address]

# 반올림된 금액으로 그룹화
rounded_groups = group_by_rounded_value(outgoing_txs)

for group in rounded_groups:
    if len(group) >= 5 and sum(tx["usd_value"] for tx in group) >= 10000:
        # 룰 발동
```

#### 📊 예시
```
주소: 0xTARGET (송금)
24시간 내 거래:
- 10,000 USD (반올림)
- 10,000 USD (반올림)
- 10,000 USD (반올림)
- 10,000 USD (반올림)
- 10,000 USD (반올림)
반복 횟수: 5회
총 금액: 50,000 USD
결과: B-502 발동 (10점) ✅
```

---

## 미구현 룰

다음 룰들은 YAML에 정의되어 있으나 아직 **구현되지 않았습니다**. 코드에서 `state` 필드가 있으면 건너뛰어집니다 (`evaluator.py` 74-75줄).

### B-401: First 7 Days Burst
- **설명**: 주소 생성 후 7일 내 고액 거래 (10,000 USD 이상, 3회 이상)
- **미구현 이유**: 주소의 생명주기 정보 (`first_seen_ts`, `first7d_usd` 등) 필요

### B-402: Reactivation
- **설명**: 1년 이상 된 주소가 180일 비활성 후 재활성화 (1,000 USD 이상)
- **미구현 이유**: 주소의 생명주기 정보 (`first_seen_ts`, `last_seen_ts` 등) 필요

### B-403A: Lifecycle A — Young but Busy
- **설명**: 생성 30일 이내, 100회 이상 거래, 중앙값 100 USD
- **미구현 이유**: 주소의 생명주기 정보 (`age_days`, `tx_count_30d` 등) 필요

### B-403B: Lifecycle B — Old and Rare High Value
- **설명**: 1년 이상, 총 10회 이하, 총액 50,000 USD 이상
- **미구현 이유**: 주소의 생명주기 정보 (`age_days`, `tx_count_total` 등) 필요

---

## 룰 평가 로직

### 평가 순서

`evaluator.py`의 `evaluate_single_transaction()` 메서드에서 룰 평가 순서:

1. **State 룰 건너뛰기** (B-401, B-402, B-403A, B-403B)
2. **E-103 조건부 체크** (백엔드 데이터 필요)
3. **E-102 PPR 평가** (간접 제재 노출)
4. **B-103 통계 평가** (Prerequisites 체크 포함)
5. **B-201, B-202 Topology 평가** (Advanced 모드에서만)
6. **B-501 동적 점수 평가** (거래 금액 기반)
7. **버킷 룰 평가** (B-203, B-204, B-502)
8. **윈도우 룰 평가** (B-101, B-102, C-004)
9. **단일 트랜잭션 룰 평가** (C-001, C-003, E-101, E-104, E-105 등)

### 룰 평가 플로우

```
트랜잭션 데이터
    ↓
State 룰 체크 → 건너뛰기 (미구현)
    ↓
특수 룰 처리:
  - E-102 (PPR)
  - B-103 (통계)
  - B-201, B-202 (Topology, Advanced만)
  - B-501 (동적 점수)
    ↓
버킷/윈도우 룰 평가
    ↓
단일 트랜잭션 룰 평가
    ↓
예외 사항 체크
    ↓
발동된 룰 목록 반환
```

### 예외 처리

각 룰은 `exceptions` 필드로 예외 사항을 정의할 수 있습니다:

- **CEX_INTERNAL**: 거래소 내부 거래는 대부분의 룰에서 제외
- **MM_BOT**: 마켓 메이커 봇은 행동 패턴 룰에서 제외
- **REWARD_PAYOUT**: 리워드 지급은 믹서 노출 룰에서 제외

---

## 참고 자료

- **룰 정의 파일**: `rules/tracex_rules.yaml`
- **룰 평가기**: `core/rules/evaluator.py`
- **윈도우 평가기**: `core/aggregation/window.py`
- **버킷 평가기**: `core/aggregation/bucket.py`
- **Topology 평가기**: `core/aggregation/topology.py`
- **주소 분석기**: `core/scoring/address_analyzer.py`
- **구현된 룰 목록**: `ACTIVE_RULES.md`

---

## 변경 이력

- **v1.0** (2025-01): 초기 룰북 정의
  - 22개 룰 정의
  - 18개 룰 구현 (Basic 모드)
  - 20개 룰 구현 (Advanced 모드)
  - 4개 룰 미구현 (State 룰)

