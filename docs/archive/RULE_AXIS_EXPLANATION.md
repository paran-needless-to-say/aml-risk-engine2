# 룰 축 (Axis) 설명

## 📊 현재 룰 축 구조

### 실제 사용 중인 축

현재 룰북(`tracex_rules.yaml`)에는 **3개의 축**이 실제로 사용되고 있습니다:

1. **C (Compliance)**: 규제 준수 관련 리스크
2. **E (Exposure)**: 위험한 주소/서비스와의 노출
3. **B (Behavior)**: 의심스러운 거래 패턴

### 코드에서 정의된 축 (5개)

코드(`improved_rule_scorer.py`)에서는 **5개의 축**을 지원하도록 설계되어 있습니다:

1. **A (Amount)**: 금액 관련 룰

   - 고액 거래, 이상한 금액 패턴
   - **현재 상태**: 룰북에 없음 (미사용)

2. **B (Behavior)**: 행동 패턴

   - Burst 패턴, Rapid Sequence, 레이어링, 순환 패턴
   - **현재 상태**: ✅ 사용 중 (12개 룰)

3. **C (Compliance)**: 규제 준수

   - 제재 주소 거래, 고위험 국가 VASP, 고액 거래
   - **현재 상태**: ✅ 사용 중 (4개 룰)

4. **D (Temporal)**: 시간 패턴

   - 시간 기반 이상 패턴
   - **현재 상태**: 룰북에 없음 (미사용)

5. **E (Exposure)**: 노출
   - 믹서, 브릿지, 스캠 주소와의 연결
   - **현재 상태**: ✅ 사용 중 (5개 룰)

## 🤔 축 분류 이유

### 원래 설계 의도

TRACE-X 룰북은 **AML 리스크의 다양한 측면**을 다루기 위해 축을 분류했습니다:

1. **Compliance (C)**: 규제 기관 관점

   - OFAC 제재, 고위험 국가
   - 법적/규제적 리스크

2. **Exposure (E)**: 위험 노출 관점

   - 믹서, 브릿지, 스캠과의 연결
   - 직접적인 위험 노출

3. **Behavior (B)**: 거래 패턴 관점
   - 의심스러운 거래 행동
   - 패턴 기반 탐지

### 코드에서 5개 축을 지원하는 이유

코드는 **확장성을 고려**하여 5개 축을 지원하도록 설계되었습니다:

- **A (Amount)**: 금액 관련 룰을 별도로 분류 (향후 추가 가능)
- **D (Temporal)**: 시간 패턴 룰을 별도로 분류 (향후 추가 가능)

하지만 **현재 룰북에는 A, D 축 룰이 없습니다.**

## 📈 축별 가중치

현재 코드에서 설정된 축별 가중치:

```python
AXIS_WEIGHTS = {
    "A": 1.5,  # 금액 관련 (가장 중요) - 하지만 룰 없음
    "B": 1.2,  # 행동 패턴
    "C": 1.3,  # 연결성 (Compliance)
    "D": 1.0,  # 시간 패턴 - 하지만 룰 없음
    "E": 1.4   # 노출
}
```

**문제점**: A, D 축에 룰이 없는데 가중치가 설정되어 있음

## 💡 개선 방안

### 1. 실제 사용 중인 축만 사용

현재 사용 중인 축: **B, C, E**

가중치 재조정:

```python
AXIS_WEIGHTS = {
    "B": 1.2,  # 행동 패턴 (12개 룰)
    "C": 1.3,  # 규제 준수 (4개 룰)
    "E": 1.4   # 노출 (5개 룰)
}
```

### 2. A, D 축 룰 추가

**A (Amount) 축 룰 예시**:

- A-001: 매우 고액 거래 (100,000 USD 이상)
- A-002: 이상한 금액 패턴 (반올림되지 않은 금액)
- A-003: 거래 금액 급증

**D (Temporal) 축 룰 예시**:

- D-001: 비정상적인 시간대 거래
- D-002: 거래 간격 이상 패턴
- D-003: 주말/공휴일 집중 거래

### 3. 축 통합

A, D 축이 필요 없다면:

- A → C에 통합 (금액 관련은 Compliance로)
- D → B에 통합 (시간 패턴은 Behavior로)

## 🎯 룰 최적화 전략

### 1. 룰별 효과 측정

각 룰이 실제로 얼마나 효과적인지 측정:

- 룰 발동 횟수
- 룰 발동 시 Fraud 비율
- 룰 제거 시 성능 변화

### 2. 축별 중요도 측정

각 축이 전체 성능에 얼마나 기여하는지 측정:

- 축별 가중치 최적화
- 축 제거 실험

### 3. 룰 임계값 최적화

각 룰의 임계값(금액, 횟수 등) 최적화:

- 현재: 고정값
- 개선: 데이터 기반 최적값

## 📊 현재 룰 통계

### 축별 룰 개수

- **C (Compliance)**: 4개

  - C-001: Sanction Direct Touch
  - C-002: High-Risk Jurisdiction VASP (미구현)
  - C-003: High-Value Single Transfer
  - C-004: High-Value Repeated Transfer

- **E (Exposure)**: 5개

  - E-101: Mixer Direct Exposure
  - E-102: Bridge Direct Exposure
  - E-103: Scam Direct Exposure
  - E-104: Mixer 1-Hop Exposure
  - E-105: Mixer 2-Hop Exposure

- **B (Behavior)**: 12개
  - B-101: Burst Pattern
  - B-102: Rapid Sequence
  - B-103: Statistical Anomaly
  - B-201: Layering Chain
  - B-202: Circular Pattern
  - B-203: Fan-out Pattern
  - B-204: Fan-in Pattern
  - B-301: Time Clustering
  - B-302: Unusual Timing
  - B-401: Address Reuse
  - B-501: Dynamic Scoring (buckets)
  - B-502: Direction-Specific Pattern

## 🔬 실험 제안

1. **축별 가중치 최적화**

   - B, C, E 축 가중치 그리드 서치
   - A, D 축 제거 또는 1.0으로 설정

2. **룰별 효과 분석**

   - 각 룰 제거 시 성능 변화 측정
   - 효과 없는 룰 제거 또는 수정

3. **임계값 최적화**

   - 금액 임계값 (3000 → 최적값)
   - 횟수 임계값 (2 → 최적값)
   - 시간 윈도우 최적화

4. **새로운 룰 추가**
   - A 축: 금액 관련 룰
   - D 축: 시간 패턴 룰
