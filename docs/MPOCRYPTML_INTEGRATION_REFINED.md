# MPOCryptoML 통합 전략 (개선안)

## 🔍 중복 문제 분석

### 현재 겹치는 부분

1. **Fan-out/Fan-in 패턴**

   - TRACE-X: B-203 (Fan-out), B-204 (Fan-in) - 버킷 기반, 명확한 임계값
   - MPOCryptoML: Fan-out/Fan-in 패턴 탐지 - 구조적 분석
   - **중복**: 둘 다 같은 패턴을 탐지

2. **제재 주소/믹서 연결성**

   - TRACE-X: C-001 (직접 제재), E-101 (믹서 직접 노출)
   - PPR: 제재 주소/믹서와의 연결성 측정
   - **중복**: 둘 다 제재/믹서 연결을 탐지

3. **간접 연결성**
   - TRACE-X: E-102 (간접 제재 노출, 2홉 이내) - 미구현
   - PPR: 오프체인 연결성 측정
   - **중복 가능성**: 비슷한 목적

---

## 💡 개선된 통합 전략

### 전략: 역할 분담 + 보완적 활용

각 방법의 고유한 역할에 집중하고, 중복을 제거:

```
최종 리스크 스코어 =
    TRACE-X 룰 점수 (기본) +
    MPOCryptoML 보너스/페널티 (미묘한 패턴) +
    PPR 연결성 (E-102 룰 구현)
```

### 1. TRACE-X 룰 (기본 점수, 100%)

**역할**: 규제 기반, 명확한 기준, 해석 가능한 룰

- ✅ C-001: 직접 제재 (명확한 기준)
- ✅ C-003: 고액 거래 (명확한 임계값)
- ✅ C-004: 반복 고액 거래 (윈도우 기반)
- ✅ E-101: 믹서 직접 노출 (명확한 기준)
- ✅ B-203, B-204: Fan-out/Fan-in (버킷 기반, 명확한 임계값)
- ✅ B-101, B-102: Burst 패턴 (명확한 기준)

**특징**:

- 명확한 임계값 (예: 5개 주소, 1,000 USD)
- 해석 가능한 룰
- 규제 준수 중심

### 2. MPOCryptoML 패턴 (보너스/페널티, ±20점)

**역할**: 룰로 잡히지 않는 미묘한 구조적 패턴 탐지

**사용 방법**:

- TRACE-X 룰이 발동하지 않았지만 구조적으로 의심스러운 경우
- 룰 점수에 보너스/페널티로 반영

**예시**:

```python
# B-203 룰이 발동하지 않았지만
# MPOCryptoML에서 강한 Fan-out 패턴 탐지
if not rule_fired("B-203") and mpocryptml.detect_fan_out_pattern(address):
    bonus_score = 10  # 보너스 점수

# Stack 패턴 탐지 (B-201 룰 미구현)
if mpocryptml.detect_stack_pattern(address, min_length=3):
    bonus_score = 15  # 레이어링 의심
```

**적용 패턴**:

- ✅ Stack (B-201 룰 미구현 → 보너스)
- ✅ Bipartite (새로운 패턴 → 보너스)
- ✅ Gather-Scatter (강한 연결성 → 보너스)
- ✅ Random (비정상적 무작위성 → 보너스)

**점수 범위**: -20 ~ +20점 (최종 점수에 추가)

### 3. PPR 연결성 (E-102 룰 구현, 최대 30점)

**역할**: E-102 룰 (간접 제재 노출) 구현

**현재 문제**:

- E-102는 SDN_HOP1, SDN_HOP2 리스트가 필요 (미구현)
- PPR로 이를 대체 가능

**구현 방법**:

```python
# E-102 룰 대신 PPR 연결성 사용
ppr_score = ppr_connector.calculate_connection_risk(
    address, graph, sdn_addresses, mixer_addresses
)

if ppr_score["total_ppr"] >= 0.05:  # 임계값
    # E-102 룰 발동 (30점)
    fired_rules.append({
        "rule_id": "E-102",
        "score": 30,
        "source": "PPR"  # PPR 기반
    })
```

**점수**: E-102 룰 점수 (30점)로 통합

---

## 🛠️ 구체적 구현 방안

### 방안 1: MPOCryptoML을 보조 지표로만 사용 (추천)

```python
class HybridScorer:
    def calculate_final_score(self, address, transactions):
        # 1. TRACE-X 룰 평가 (기본 점수)
        rule_results = self.rule_evaluator.evaluate(...)
        base_score = sum(r["score"] for r in rule_results)

        # 2. MPOCryptoML 패턴 분석 (보너스/페널티)
        pattern_bonus = 0

        # B-201 룰 미구현 → Stack 패턴 보너스
        stack_paths = self.pattern_detector.detect_stack_pattern(address)
        if stack_paths and not any(r["rule_id"] == "B-201" for r in rule_results):
            pattern_bonus += 15  # 레이어링 의심

        # Bipartite 패턴 (새로운 패턴)
        bipartite = self.pattern_detector.detect_bipartite_pattern([address])
        if bipartite["is_bipartite"]:
            pattern_bonus += 10  # 구조적 의심

        # Gather-Scatter 강함 (연결성 높음)
        gs = self.pattern_detector.gather_scatter(address)
        if gs > 10000:  # 임계값
            pattern_bonus += 5

        # 3. PPR 연결성 (E-102 룰 구현)
        ppr_result = self.ppr_connector.calculate_connection_risk(...)
        if ppr_result["total_ppr"] >= 0.05:
            # E-102 룰 발동
            rule_results.append({
                "rule_id": "E-102",
                "score": 30,
                "source": "PPR"
            })
            base_score += 30

        # 4. 최종 점수
        final_score = min(100, base_score + pattern_bonus)

        return {
            "final_score": final_score,
            "base_score": base_score,
            "pattern_bonus": pattern_bonus,
            "fired_rules": rule_results
        }
```

### 방안 2: MPOCryptoML을 룰 점수 조정에만 사용

```python
# 기존 룰 점수 조정
if rule_fired("B-203"):
    base_score = 20

    # MPOCryptoML에서도 강하게 탐지되면 점수 증가
    if mpocryptml.detect_fan_out_pattern(address)["is_detected"]:
        adjusted_score = base_score * 1.5  # 30점
    else:
        adjusted_score = base_score  # 20점
```

---

## 📊 역할 분담 정리

| 구성 요소            | 역할                   | 점수 범위      | 중복 제거             |
| -------------------- | ---------------------- | -------------- | --------------------- |
| **TRACE-X 룰**       | 규제 기반, 명확한 기준 | 0~100점        | 기본 점수             |
| **MPOCryptoML 패턴** | 미묘한 구조적 패턴     | ±20점 보너스   | 룰 미구현/약한 경우만 |
| **PPR 연결성**       | E-102 룰 구현          | 0~30점 (E-102) | E-102 대체            |

### 중복 제거 원칙

1. **Fan-out/Fan-in**: TRACE-X 룰(B-203, B-204) 우선, MPOCryptoML은 보조
2. **제재/믹서 직접 연결**: TRACE-X 룰(C-001, E-101) 우선
3. **간접 연결**: PPR로 E-102 룰 구현 (SDN_HOP 리스트 대체)
4. **새로운 패턴**: MPOCryptoML만 탐지 (Stack, Bipartite 등)

---

## 🎯 최종 통합 공식

```
최종 리스크 스코어 =
    TRACE-X 룰 점수 (기본, 0~100점) +
    MPOCryptoML 보너스 (미묘한 패턴, ±20점) +
    PPR 기반 E-102 룰 (간접 연결, 0~30점)

최종 점수 = min(100, base_score + pattern_bonus)
```

**장점**:

- ✅ 중복 제거
- ✅ 각 방법의 고유 역할 명확
- ✅ 해석 가능성 유지
- ✅ 점진적 개선 가능

---

## 📋 구현 우선순위

### 1단계: PPR로 E-102 룰 구현 (높은 우선순위)

```python
# core/rules/evaluator.py 수정
if rule_id == "E-102":
    # SDN_HOP 리스트 대신 PPR 사용
    ppr_result = self.ppr_connector.calculate_connection_risk(...)
    if ppr_result["total_ppr"] >= 0.05:
        # 룰 발동
        fired_rules.append({...})
```

### 2단계: MPOCryptoML 보너스 시스템 (중간 우선순위)

```python
# core/scoring/address_analyzer.py 수정
pattern_bonus = self._calculate_pattern_bonus(address, transactions)
final_score = min(100, base_score + pattern_bonus)
```

### 3단계: 통합 테스트 (낮은 우선순위)

- 데모 데이터로 검증
- 성능 비교

---

## 💡 결론

**중복을 제거하고 역할을 명확히**:

1. **TRACE-X 룰**: 기본 점수 (규제 기반, 명확한 기준)
2. **MPOCryptoML**: 보너스/페널티 (미묘한 패턴, 룰 미구현 보완)
3. **PPR**: E-102 룰 구현 (간접 연결성 측정)

이렇게 하면 각 방법의 고유한 강점을 살리면서 중복을 최소화할 수 있습니다.
