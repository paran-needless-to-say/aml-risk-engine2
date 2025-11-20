# SDN_ENHANCED 3.XML 파일 설명

## 📋 파일 개요

**파일명**: `SDN_ENHANCED 3.XML`  
**크기**: 약 99.44 MB  
**줄 수**: 약 2,538,711줄  
**데이터 기준일**: 2025-11-13  
**출처**: OFAC (Office of Foreign Assets Control) - 미국 재무부 산하 기관

## 🎯 파일 목적

이 파일은 **OFAC SDN (Specially Designated Nationals) 리스트**의 Enhanced XML 버전입니다.

- **SDN 리스트**: 미국 정부가 제재한 개인, 조직, 기업 등의 목록
- **Enhanced XML**: 상세한 정보를 포함한 확장 버전 (이름, 주소, 식별자, 디지털 통화 주소 등)

## 📊 파일 구조

### 1. 루트 요소: `<sanctionsData>`

```xml
<sanctionsData xmlns="...">
  <publicationInfo>...</publicationInfo>
  <referenceValues>...</referenceValues>
  <featureTypes>...</featureTypes>
  <entities>...</entities>
</sanctionsData>
```

### 2. 주요 섹션

#### `<publicationInfo>`
- 데이터 기준일: `2025-11-13T00:00:00-05:00`
- 필터 정보: SDN List 포함

#### `<referenceValues>`
- 참조 값 정의 (국가, 제재 타입, 별칭 타입 등)
- 예: 국가 코드, 제재 정보 타입, 별칭 타입 (A.K.A., F.K.A. 등)

#### `<entities>`
- 제재 대상 엔티티 목록
- **총 18,336개 엔티티** 포함

### 3. 엔티티 구조

각 `<entity>`는 다음 정보를 포함:

```xml
<entity id="...">
  <profile>
    <type>Individual</type> <!-- 또는 Entity, Vessel 등 -->
    <sanctions>
      <listingType>SDN List</listingType>
    </sanctions>
  </profile>
  <names>
    <name>
      <formattedFullName>...</formattedFullName>
    </name>
  </names>
  <addresses>...</addresses>
  <identifiers>
    <identifier>
      <type>DigitalCurrencyAddress</type>
      <value>0x...</value>
    </identifier>
  </identifiers>
</entity>
```

## 🔍 이더리움 주소 포함 현황

### 추출 결과
- **총 이더리움 주소**: 78개
- **저장 위치**: `data/lists/sdn_addresses_from_xml.json`

### 주소 형식
- 이더리움 주소는 `<identifier>` 요소의 `<value>` 태그에 포함됨
- 형식: `0x`로 시작하는 42자리 16진수 문자열
- 예: `0x098b716b8aaf21512996dc57eb0615e2383e2f96`

### 샘플 주소
1. `0x098b716b8aaf21512996dc57eb0615e2383e2f96`
2. `0xa0e1c89ef1a489c9c7de96311ed5ce5d32c20e4b`
3. `0x3cffd56b47b7b41c56258d9c7731abadc360e073`
4. `0x53b6936513e738f44fb50d2b9476730c0ab3bfc1`
5. `0x35fb6f6db4fb05e6a4ce86f2c93691425626d4b1`
... (총 78개)

## 📝 엔티티 타입

주요 엔티티 타입:
- **Individual**: 개인
- **Entity**: 조직/기업
- **Vessel**: 선박
- **Aircraft**: 항공기

## 🎯 활용 방법

### 1. 이더리움 주소 추출
```bash
python scripts/parse_sdn_xml.py "SDN_ENHANCED 3.XML" "data/lists/sdn_addresses_from_xml.json"
```

### 2. SDN 리스트 업데이트
추출된 주소를 `data/lists/sdn_addresses.json`에 통합하여 사용

### 3. 룰 평가에서 활용
- C-001 룰 (Sanction Direct Touch)에서 사용
- `ListLoader.get_sdn_list()`로 로드

## ⚠️ 주의사항

1. **파일 크기**: 약 100MB로 매우 큼
2. **업데이트 주기**: OFAC에서 정기적으로 업데이트됨
3. **법적 효력**: 미국 정부의 공식 제재 리스트
4. **데이터 기준일**: 2025-11-13 (미래 날짜로 보이지만, 실제로는 최신 데이터)

## 🔗 관련 정보

- **OFAC 공식 사이트**: https://ofac.treasury.gov/
- **SDN 리스트**: https://ofac.treasury.gov/specially-designated-nationals-list-sdn-list
- **Enhanced XML 스키마**: https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ENHANCED_XML.xsd

## 💡 다음 단계

1. ✅ 이더리움 주소 추출 완료 (78개)
2. ⏳ `data/lists/sdn_addresses.json`에 통합
3. ⏳ `ListLoader`가 자동으로 로드하도록 확인
4. ⏳ C-001 룰에서 자동으로 사용됨

