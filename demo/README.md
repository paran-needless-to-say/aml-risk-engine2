# 시연용 데이터

CEX용 리스크 스코어링 시스템 시연을 위한 테스트 데이터입니다.

## 📁 구조

```
demo/
├── addresses.json                    # 시연용 주소 목록
├── transactions/                     # 각 주소의 거래 히스토리
│   ├── 0xhigh_risk_mixer_sanctioned_txs.json
│   ├── 0xhigh_risk_repeated_large_txs.json
│   ├── 0xmedium_risk_high_value_txs.json
│   ├── 0xmedium_risk_burst_txs.json
│   ├── 0xlow_risk_normal_txs.json
│   └── 0xlow_risk_small_amounts_txs.json
├── demo_runner.py                    # 시연 실행 스크립트
└── README.md
```

## 🎯 시나리오

### High Risk 주소

1. **0xhigh_risk_mixer_sanctioned**

   - Mixer에서 유입
   - 제재 주소와 거래
   - 고액 거래 (7,000 USD 이상)
   - 예상 스코어: 70-90
   - 예상 레벨: high

2. **0xhigh_risk_repeated_large**
   - 24시간 내 반복 고액 거래
   - C-004 룰 발동 (sum >= 10,000, count >= 3, every >= 3,000)
   - 예상 스코어: 60-80
   - 예상 레벨: high

### Medium Risk 주소

1. **0xmedium_risk_high_value**

   - 고액 단일 거래 (7,000 USD 이상)
   - C-003 룰 발동
   - 예상 스코어: 20-40
   - 예상 레벨: medium

2. **0xmedium_risk_burst**
   - 10분 내 3회 이상 거래
   - B-101 룰 발동 (Burst)
   - 예상 스코어: 15-35
   - 예상 레벨: medium

### Low Risk 주소

1. **0xlow_risk_normal**

   - 정상 거래 패턴
   - CEX 유입
   - 예상 스코어: 0-20
   - 예상 레벨: low

2. **0xlow_risk_small_amounts**
   - 소액 거래만 존재
   - 룰 발동 없음
   - 예상 스코어: 0
   - 예상 레벨: low

## 🚀 사용 방법

### 시연 실행

```bash
python demo/demo_runner.py
```

### 개별 주소 분석

```python
from core.scoring.address_analyzer import AddressAnalyzer
import json

# 거래 히스토리 로드
with open("demo/transactions/0xhigh_risk_mixer_sanctioned_txs.json", "r") as f:
    transactions = json.load(f)

# 분석 수행
analyzer = AddressAnalyzer()
result = analyzer.analyze_address(
    address="0xhigh_risk_mixer_sanctioned",
    chain="ethereum",
    transactions=transactions
)

print(f"리스크 스코어: {result.risk_score}")
print(f"리스크 레벨: {result.risk_level}")
```

### API 테스트

```bash
# 주소 분석 API 호출
curl -X POST http://localhost:5000/api/analyze/address \
  -H "Content-Type: application/json" \
  -d @demo/api_request_example.json
```

## 📊 예상 결과

| 주소                         | 리스크 스코어 | 리스크 레벨 | 주요 룰             |
| ---------------------------- | ------------- | ----------- | ------------------- |
| 0xhigh_risk_mixer_sanctioned | 70-90         | high        | E-101, C-001, C-003 |
| 0xhigh_risk_repeated_large   | 60-80         | high        | C-004               |
| 0xmedium_risk_high_value     | 20-40         | medium      | C-003               |
| 0xmedium_risk_burst          | 15-35         | medium      | B-101               |
| 0xlow_risk_normal            | 0-20          | low         | 없음 또는 CEX 관련  |
| 0xlow_risk_small_amounts     | 0             | low         | 없음                |

## 💡 시연 팁

1. **High Risk 시연**: Mixer + 제재 주소 조합으로 높은 리스크 점수 보여주기
2. **Medium Risk 시연**: 고액 거래나 패턴 기반 룰 발동 보여주기
3. **Low Risk 시연**: 정상 거래 패턴으로 낮은 리스크 점수 보여주기
