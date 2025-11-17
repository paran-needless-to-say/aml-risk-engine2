# 다음 단계 가이드

## ✅ 현재 완료된 것

1. **주소 기반 분석 API** (`POST /api/analyze/address`)

   - 주소의 거래 히스토리 분석
   - 룰 평가 (단일 + 윈도우 룰)
   - 리스크 스코어 계산

2. **단일 트랜잭션 스코어링 API** (`POST /api/score/transaction`)

   - 백엔드 JSON 구조와 일치 ✓
   - 응답 구조 일치 ✓

3. **집계 로직**
   - 시간 윈도우 처리
   - 집계 연산자 지원 (sum_gte, count_gte, every_gte 등)

## 📋 다음 단계

### 1. 테스트 코드 작성 (우선순위: 높음)

**목적**: 구현이 제대로 동작하는지 확인

**작업**:

- [ ] 단위 테스트 작성 (`api/test_address_analysis.py` - 이미 생성됨)
- [ ] 통합 테스트 작성
- [ ] 엣지 케이스 테스트 (빈 거래, 매우 많은 거래 등)

**실행**:

```bash
python api/test_address_analysis.py
```

### 2. 시연용 데이터 준비 (우선순위: 높음)

**목적**: 실제 거래소 연동 없이 시연 가능하도록

**작업**:

- [ ] 시연용 주소 목록 준비
- [ ] 각 주소의 거래 히스토리 데이터 (JSON)
- [ ] 다양한 리스크 레벨 시나리오
  - High Risk: Mixer + 제재 주소
  - Medium Risk: 고액 거래
  - Low Risk: 정상 거래

**구조**:

```
demo/
├── addresses.json          # 시연용 주소 목록
├── transactions/           # 각 주소의 거래 히스토리
│   ├── 0xhigh_risk_txs.json
│   ├── 0xmedium_risk_txs.json
│   └── 0xlow_risk_txs.json
└── scenarios/              # 시나리오별 데이터
    ├── high_risk.json
    ├── medium_risk.json
    └── low_risk.json
```

### 3. 비동기 큐 구현 (실시간 탐지용) (우선순위: 중간)

**목적**: 실시간 탐지를 위한 비동기 처리

**작업**:

- [ ] 큐 시스템 구현 (Redis 또는 in-memory)
- [ ] 비동기 워커 프로세스
- [ ] 작업 상태 조회 API
- [ ] 결과 콜백 처리

**API**:

```http
POST /api/analyze/address/async
GET /api/analyze/address/async/{job_id}
```

### 4. API 문서 업데이트 (우선순위: 중간)

**작업**:

- [ ] OpenAPI/Swagger 스펙 작성
- [ ] 예시 요청/응답 추가
- [ ] 에러 코드 문서화

### 5. 성능 최적화 (우선순위: 낮음)

**작업**:

- [ ] 많은 거래를 가진 주소 처리 최적화
- [ ] 캐싱 (같은 주소 재분석 시)
- [ ] 병렬 처리

## 🎯 추천 진행 순서

1. **테스트 코드 작성 및 실행** (1일)

   - 기본 동작 확인
   - 버그 수정

2. **시연용 데이터 준비** (2-3일)

   - 실제 데이터 수집 또는 시뮬레이션
   - 다양한 시나리오 준비

3. **비동기 큐 구현** (3-4일)

   - 실시간 탐지 기능 완성

4. **문서화 및 정리** (1일)
   - API 문서 완성
   - README 업데이트

## 💡 시연 시나리오

### 시나리오 1: High Risk 주소

- Mixer에서 유입
- 제재 주소와 거래
- 고액 거래
- 예상 스코어: 70-90

### 시나리오 2: Medium Risk 주소

- 고액 거래 (7,000 USD 이상)
- 반복 거래 패턴
- 예상 스코어: 30-60

### 시나리오 3: Low Risk 주소

- 정상 거래 패턴
- CEX 유입
- 예상 스코어: 0-30
