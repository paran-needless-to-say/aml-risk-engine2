# 테스트용 주소 목록

## 🎯 데모 테스트용 추천 주소

### 1. 레거시 데이터에 있는 실제 주소들

다음 주소들은 레거시 데이터에 실제 거래 내역이 있어 분석 결과가 나올 가능성이 높습니다:

#### Fraud 라벨 (label=1)

- `0x0000000035f26e72b70552b92bf7e02f67a90549` - Fraud로 분류된 주소
- `0x00000000000045166c45af0fc6e4cf31d9e14b9a` - Fraud로 분류된 주소 (다만 CSV에는 label=0으로 표시됨)

#### Normal 라벨 (label=0)

- `0x00000000000045166c45af0fc6e4cf31d9e14b9a` - Normal로 분류된 주소

### 2. 잘 알려진 주소들 (테스트용)

#### USDC 컨트랙트

- `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` - USDC 토큰 컨트랙트

#### Uniswap V2 Router

- `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` - Uniswap V2 Router

#### WETH 컨트랙트

- `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` - Wrapped Ether

### 3. 실제 사용 예시

데모에서 테스트할 때:

1. **빠른 테스트**: 레거시 주소 사용

   ```
   0x0000000035f26e72b70552b92bf7e02f67a90549
   ```

2. **실제 컨트랙트 테스트**: USDC 컨트랙트

   ```
   0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
   ```

3. **예시 주소 (데모에 기본 설정)**
   ```
   0x3e66b66fd1d0b02fda6c811da9e0547970db2f21
   ```

## ⚠️ 주의사항

- 현재 데모는 **거래 데이터를 자동으로 수집하지 않습니다**
- 거래 데이터를 입력하지 않으면 기본 점수(0)가 반환됩니다
- 실제 분석 결과를 보려면 거래 데이터를 JSON 형식으로 입력해야 합니다

## 📝 거래 데이터 입력 예시

```json
[
  {
    "tx_hash": "0x7f5d2baaf513404f2a50a66485ee0d6fec36c2198f1feebae5b0482217e7668a",
    "from": "0x3e66b66fd1d0b02fda6c811da9e0547970db2f21",
    "to": "0x3531addf2ce7877d54aa4ba0748ab261c3e5149a",
    "usd_value": 5000,
    "timestamp": 1618297835,
    "is_sanctioned": false,
    "is_mixer": false,
    "is_bridge": false
  }
]
```

## 🔧 향후 개선

- Etherscan API 연동으로 자동 거래 데이터 수집
- 레거시 데이터에서 자동으로 거래 데이터 로드
- 주소 검색 시 자동으로 관련 거래 표시
