# OFAC SDN 리스트 활용 가이드

AML 리스크 스코어링을 위한 OFAC (Office of Foreign Assets Control) SDN 리스트 활용 방법입니다.

## 📚 OFAC SDN 리스트란?

**SDN (Specially Designated Nationals)** 리스트는 미국 재무부가 운영하는 제재 대상 목록입니다.

### 주요 특징

- **무료 공개**: 누구나 다운로드 가능
- **정기 업데이트**: OFAC에서 정기적으로 업데이트
- **암호화폐 주소 포함**: BTC, ETH, BNB, USDT 등 주소가 직접 포함됨
- **공식 데이터**: 가장 신뢰할 수 있는 제재 리스트

### 포함된 주요 주소

- **Lazarus 해킹 지갑**: 북한 해킹 그룹
- **Tornado Cash Router**: 믹서 서비스
- **Blender.io BTC 믹서**: 러시아 관련 믹서
- **Hydra·Garantex 관련 자금 라우터**: 다크웹 마켓플레이스

## 🔗 공식 자료

### OFAC 공식 웹사이트

- **제재 목록 페이지**: https://www.treasury.gov/resource-center/sanctions/SDN-List/Pages/default.aspx
- **SDN XML 파일**: https://www.treasury.gov/ofac/downloads/sdn.xml

### XML 구조

```xml
<sdnEntry>
    <idList>
        <id>
            <idType>Digital Currency Address</idType>
            <idNumber>0xabc123...</idNumber>
        </id>
    </idList>
</sdnEntry>
```

`<idType>Digital Currency Address</idType>`로 표시된 항목이 암호화폐 주소입니다.

## 🛠️ 사용 방법

### 1. 자동 업데이트 (권장)

```bash
# SDN 리스트 자동 업데이트
python3 scripts/update_sdn_list.py
```

이 스크립트는:

1. OFAC 공식 XML 파일을 다운로드
2. 암호화폐 주소를 추출 (BTC, ETH, BNB, USDT 등)
3. `data/lists/sdn_addresses.json` 파일 업데이트
4. 변경사항 요약 출력

### 2. 수동 업데이트

1. OFAC XML 파일 다운로드: https://www.treasury.gov/ofac/downloads/sdn.xml
2. `scripts/update_sdn_list.py` 스크립트 실행
3. 또는 직접 `data/lists/sdn_addresses.json` 파일 편집

### 3. JSON 파일 구조

```json
{
  "btc": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", ...],
  "eth": ["0xabc123...", ...],
  "bnb": ["bnb1...", ...],
  "other": ["...", ...],
  "all": ["...", ...],
  "metadata": {
    "last_updated": "2025-11-18T00:00:00",
    "source": "https://www.treasury.gov/ofac/downloads/sdn.xml",
    "total_entries": 12345,
    "digital_currency_count": 567,
    "counts": {
      "btc": 100,
      "eth": 200,
      "bnb": 50,
      "other": 217,
      "all": 567
    }
  }
}
```

## 🔍 프로젝트에서의 활용

### C-001 룰: Sanction Direct Touch

SDN 리스트는 **C-001 룰**에서 사용됩니다:

```yaml
- id: "C-001"
  name: "Sanction Direct Touch"
  match:
    any:
      - in_list: { field: "from", list: "SDN_LIST" }
      - in_list: { field: "to", list: "SDN_LIST" }
  score: 30
```

### 코드에서의 사용

```python
from core.data.lists import ListLoader

# SDN 리스트 로드
list_loader = ListLoader()
sdn_list = list_loader.get_sdn_list()

# 주소 확인
if "0xabc123..." in sdn_list:
    print("제재 대상 주소입니다!")
```

### 룰 평가기에서의 활용

`core/rules/evaluator.py`에서 SDN 리스트를 사용하여 룰을 평가합니다:

1. **리스트 직접 확인**: 주소가 SDN 리스트에 있는지 확인
2. **백엔드 플래그 활용**: `is_sanctioned` 플래그도 함께 확인

```python
# 리스트에 직접 있는지 확인
if value in target_list:
    return True

# 백엔드에서 제공하는 플래그 활용
if list_name == "SDN_LIST" and tx_data.get("is_sanctioned", False):
    return True
```

## 📊 업데이트 주기

### 권장 업데이트 주기

- **주 1회**: 정기적으로 업데이트 (예: 매주 월요일)
- **긴급 업데이트**: OFAC에서 새로운 제재 발표 시 즉시 업데이트

### 자동화 (선택사항)

```bash
# crontab 설정 예시 (매주 월요일 오전 9시)
0 9 * * 1 cd /path/to/project && python3 scripts/update_sdn_list.py
```

## ⚠️ 주의사항

### 1. 네트워크 오류

OFAC 서버에 접근할 수 없는 경우:

- 수동으로 XML 파일 다운로드
- 또는 기존 리스트 유지

### 2. XML 파싱 오류

XML 구조가 변경된 경우:

- `scripts/update_sdn_list.py` 스크립트 업데이트 필요
- OFAC 공식 문서 확인

### 3. 주소 형식

다양한 체인의 주소 형식:

- **BTC**: `1...`, `3...`, `bc1...`
- **ETH**: `0x...` (42자)
- **BNB**: `bnb1...`
- **기타**: 다양한 형식 가능

## 🔄 업데이트 확인

업데이트 후 확인:

```bash
# JSON 파일 확인
cat data/lists/sdn_addresses.json | jq '.metadata'

# 주소 수 확인
cat data/lists/sdn_addresses.json | jq '.metadata.counts'
```

## 📝 참고 자료

- **OFAC 공식 웹사이트**: https://www.treasury.gov/resource-center/sanctions/SDN-List/Pages/default.aspx
- **SDN XML 다운로드**: https://www.treasury.gov/ofac/downloads/sdn.xml
- **OFAC FAQ**: https://www.treasury.gov/resource-center/faqs/Sanctions/Pages/faq_general.aspx

## 💡 팁

1. **백엔드와 협업**: 백엔드에서도 `is_sanctioned` 플래그를 제공하면 더 정확한 검사 가능
2. **캐싱**: SDN 리스트는 자주 변경되지 않으므로 캐싱 활용
3. **로깅**: 제재 대상 주소 감지 시 로깅하여 모니터링
