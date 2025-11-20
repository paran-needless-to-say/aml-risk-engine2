# Etherscan 태그 활용 가이드

## 📊 Etherscan 태그 정보

Etherscan은 주소에 대해 다양한 태그 정보를 제공합니다:

- **Exchange**: CEX 주소 (Binance, Coinbase 등)
- **Token**: ERC-20/ERC-721 토큰 컨트랙트
- **Contract**: 스마트 컨트랙트
- **Mixer**: 믹서 서비스 (일부)
- **Bridge**: 브릿지 컨트랙트

## 🔧 구현 방법

### 1. 컨트랙트 정보 조회

```python
from core.data.etherscan_client import EtherscanClient

client = EtherscanClient(api_key="TZ66JXC2M8WST154TM3111MBRRX7X7UAF9")

# 컨트랙트 정보 확인
contract_info = client.get_contract_info("0x...")
print(contract_info)
# {
#   "is_contract": True,
#   "contract_name": "TokenContract",
#   "is_token": True
# }
```

### 2. 주소 태그 정보 추출

```python
# 주소 태그 정보
tags = client.get_address_tags("0x...")
print(tags)
# {
#   "label": "token",
#   "entity_type": "token",
#   "is_contract": True,
#   "is_token": True,
#   "is_exchange": False,
#   "is_mixer": False,
#   "is_bridge": False
# }
```

## 🎯 라벨링 개선

### Before (기본 라벨링)

```python
# OFAC/믹서 리스트만 확인
is_sanctioned = address in sdn_list
is_mixer = address in mixer_list
label = "mixer" if is_mixer else ("sanctioned" if is_sanctioned else "unknown")
```

### After (태그 정보 활용)

```python
# Etherscan 태그 정보 활용
tags = client.get_address_tags(address)

if tags["is_mixer"]:
    label = "mixer"
elif tags["is_exchange"]:
    label = "cex"
elif tags["is_token"]:
    label = "token"
elif tags["is_contract"]:
    label = "contract"
else:
    label = "unknown"
```

## 📋 알려진 주소 리스트 확장

Etherscan 태그를 활용하여 알려진 주소 리스트를 확장할 수 있습니다:

### CEX 주소

- Binance: `0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE`
- Coinbase: `0x71660c4005BA85c37ccec55d0C4493E66Fe775d3`
- 등등...

### DEX 주소

- Uniswap V2: `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D`
- Uniswap V3: `0xE592427A0AEce92De3Edee1F18E0157C05861564`
- 등등...

## 💡 활용 예시

### 실제 데이터 수집 시 태그 활용

```python
from core.scoring.real_dataset_builder import RealDatasetBuilder

builder = RealDatasetBuilder(api_key="TZ66JXC2M8WST154TM3111MBRRX7X7UAF9")

# 고위험 주소 수집 (태그 정보 자동 포함)
dataset = builder.build_from_high_risk_addresses(
    addresses=high_risk_addresses,
    max_transactions_per_address=50
)

# 각 거래에 태그 정보 포함됨
for item in dataset:
    tx = item["tx_context"]
    print(f"From: {tx.get('from_tags', {})}")
    print(f"To: {tx.get('to_tags', {})}")
```

## 🔍 태그 정보 확인 방법

### Etherscan 웹사이트

1. 주소 검색: https://etherscan.io/address/0x...
2. "Tags" 섹션 확인
3. Exchange, Token, Contract 등 태그 확인

### API 활용

```python
# 컨트랙트 소스 코드 확인
contract_info = client.get_contract_info(address)

# 컨트랙트 이름에서 태그 추론
if "exchange" in contract_info["contract_name"].lower():
    tags["is_exchange"] = True
if "token" in contract_info["contract_name"].lower():
    tags["is_token"] = True
```

## ⚠️ 주의사항

1. **Rate Limit**: Etherscan API는 5 calls/sec 제한

   - 태그 조회 시 rate limit 고려 필요
   - 대량 수집 시 시간이 오래 걸릴 수 있음

2. **태그 정보 부족**:

   - 모든 주소에 태그가 있는 것은 아님
   - 알려진 주소 리스트와 병행 사용 권장

3. **정확도**:
   - 컨트랙트 이름 기반 추론은 100% 정확하지 않을 수 있음
   - 실제 태그 정보와 비교 검증 필요

## 🚀 개선 방안

### 1. 알려진 주소 데이터베이스 구축

```python
KNOWN_ADDRESSES = {
    "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE": {
        "label": "cex",
        "name": "Binance",
        "entity_type": "cex"
    },
    # ...
}
```

### 2. 태그 정보 캐싱

```python
# 한 번 조회한 태그 정보는 캐시
tag_cache = {}

def get_cached_tags(address):
    if address not in tag_cache:
        tag_cache[address] = client.get_address_tags(address)
    return tag_cache[address]
```

### 3. 배치 처리

```python
# 여러 주소를 한 번에 처리
addresses = ["0x...", "0x...", ...]
tags_batch = [client.get_address_tags(addr) for addr in addresses]
```
