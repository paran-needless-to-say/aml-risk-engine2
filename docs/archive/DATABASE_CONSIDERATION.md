# 데이터베이스 구축 고려사항

## 📊 현재 상황 분석

### 현재 데이터 저장 방식

- **JSON 파일 기반**: `data/dataset/*.json`
- **데이터 규모**: 약 127KB (소규모)
- **데이터 수집**: Etherscan API → JSON 파일 저장
- **모델 학습**: JSON 파일 전체 로드 후 학습

---

## 🤔 데이터베이스 도입 필요성 평가

### ✅ 데이터베이스가 **필요한** 경우

#### 1. **대규모 데이터 수집** (수만~수십만 건 이상)

- **현재**: 수백~수천 건
- **필요 시점**: 데이터가 수만 건 이상으로 증가할 때
- **이유**:
  - JSON 파일 전체 로드 시 메모리 부담
  - 파일 크기가 수백 MB 이상일 때

#### 2. **실시간 데이터 업데이트**

- **현재**: 배치 수집 후 JSON 저장
- **필요 시점**: 실시간으로 새로운 거래 데이터를 지속적으로 추가할 때
- **이유**:
  - JSON 파일은 전체 덮어쓰기 방식 (비효율)
  - 증분 업데이트가 어려움

#### 3. **복잡한 쿼리 및 분석**

- **현재**: 전체 데이터 로드 후 Python에서 필터링
- **필요 시점**:
  - 특정 기간, 주소, 체인별 조회
  - 집계 및 통계 분석
  - 그래프 쿼리 (주소 간 관계)
- **이유**: SQL 쿼리로 효율적인 필터링 가능

#### 4. **멀티 사용자/프로세스 환경**

- **현재**: 단일 프로세스에서 JSON 파일 읽기/쓰기
- **필요 시점**:
  - 여러 프로세스가 동시에 데이터 접근
  - API 서버와 학습 프로세스가 동시 실행
- **이유**: 동시성 제어 및 락 관리 필요

#### 5. **데이터 버전 관리 및 히스토리**

- **현재**: 단일 JSON 파일 (버전 관리 없음)
- **필요 시점**:
  - 데이터셋 버전 관리
  - 학습 이력 추적
  - 롤백 필요
- **이유**: DB는 타임스탬프 및 버전 관리 용이

---

## ❌ 데이터베이스가 **불필요한** 경우 (현재 단계)

### 현재 프로젝트 특성

1. **소규모 데이터셋** (수백~수천 건)

   - JSON 파일로 충분히 관리 가능
   - 전체 로드해도 메모리 부담 적음

2. **배치 처리 방식**

   - 주기적으로 데이터 수집 후 학습
   - 실시간 업데이트 불필요

3. **단순한 데이터 구조**

   - 거래별 규칙 결과 + 라벨
   - 복잡한 관계나 중첩 구조 없음

4. **개발/연구 단계**
   - 프로덕션 환경 아님
   - 빠른 프로토타이핑 우선

---

## 💡 단계별 권장사항

### 🟢 **현재 단계 (소규모 데이터)**: JSON 파일 유지

**장점**:

- ✅ 구현 간단, 추가 의존성 없음
- ✅ 버전 관리 용이 (Git)
- ✅ 이식성 좋음 (어디서든 사용 가능)
- ✅ 디버깅 쉬움 (직접 확인 가능)
- ✅ 빠른 프로토타이핑

**개선 방안**:

```python
# 데이터셋을 여러 파일로 분할 (크기 관리)
data/dataset/
  ├── train_0.json  # 1000건씩 분할
  ├── train_1.json
  ├── val.json
  └── test.json

# 압축 저장 (공간 절약)
import gzip
import json

with gzip.open('data/dataset/train.json.gz', 'wt') as f:
    json.dump(dataset, f)
```

---

### 🟡 **중규모 데이터 (수만 건)**: SQLite 도입 고려

**전환 시점**:

- 데이터가 10,000건 이상
- JSON 파일 크기가 50MB 이상
- 학습 시 메모리 부담 발생

**SQLite 장점**:

- ✅ 파일 기반 (설치 불필요)
- ✅ SQL 쿼리 지원
- ✅ 인덱싱으로 빠른 조회
- ✅ Python 표준 라이브러리 지원

**구현 예시**:

```python
import sqlite3
import json

# 데이터베이스 생성
conn = sqlite3.connect('data/dataset/training_data.db')
cursor = conn.cursor()

# 테이블 생성
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tx_hash TEXT UNIQUE,
        chain TEXT,
        ground_truth_label TEXT,
        actual_risk_score REAL,
        rule_results TEXT,  -- JSON 문자열
        tx_context TEXT,    -- JSON 문자열
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 인덱스 생성
cursor.execute('CREATE INDEX idx_label ON transactions(ground_truth_label)')
cursor.execute('CREATE INDEX idx_chain ON transactions(chain)')
cursor.execute('CREATE INDEX idx_score ON transactions(actual_risk_score)')

conn.commit()
```

---

### 🔴 **대규모 데이터 (수십만 건 이상)**: PostgreSQL/MongoDB

**전환 시점**:

- 데이터가 100,000건 이상
- 실시간 업데이트 필요
- 복잡한 쿼리 및 분석 필요

**PostgreSQL 장점**:

- ✅ JSONB 타입 지원 (JSON 데이터 효율적 저장)
- ✅ 복잡한 쿼리 및 집계
- ✅ 트랜잭션 및 동시성 제어
- ✅ 확장성 좋음

**MongoDB 장점**:

- ✅ 유연한 스키마 (JSON 구조 그대로 저장)
- ✅ 수평 확장 용이
- ✅ 그래프 데이터에 적합

---

## 🎯 하이브리드 접근법 (권장)

### 현재 + 미래를 고려한 설계

```python
# 1. 소규모 데이터: JSON 파일 (현재)
# 2. 메타데이터/캐시: Redis (주소별 상태)
# 3. 대규모 데이터: PostgreSQL (필요 시)

class DatasetStorage:
    """하이브리드 데이터 저장소"""

    def __init__(self):
        self.json_storage = JSONStorage()  # 현재 방식
        self.redis_cache = RedisCache()    # 주소 메타데이터
        self.db_storage = None              # 필요 시 활성화

    def save(self, data):
        """데이터 크기에 따라 자동 선택"""
        if len(data) < 10000:
            return self.json_storage.save(data)
        else:
            if not self.db_storage:
                self.db_storage = PostgreSQLStorage()
            return self.db_storage.save(data)
```

---

## 📋 구체적 권장사항

### ✅ **지금 당장 할 것**

1. **JSON 파일 구조 개선**

   - 데이터셋 분할 (train/val/test)
   - 압축 저장 고려
   - 메타데이터 파일 추가 (통계 정보)

2. **데이터 수집 로직 개선**

   - 증분 수집 지원 (중복 제거)
   - 진행 상황 추적 (로그/프로그레스 파일)

3. **데이터 검증 추가**
   - 스키마 검증
   - 데이터 품질 체크

### 🔄 **향후 고려사항**

1. **데이터가 10,000건 이상일 때**

   - SQLite 도입 검토
   - JSON → SQLite 마이그레이션 스크립트 준비

2. **실시간 업데이트 필요 시**

   - PostgreSQL 도입
   - 스트리밍 데이터 처리 파이프라인 구축

3. **복잡한 분석 필요 시**
   - 그래프 데이터베이스 (Neo4j) 고려
   - 주소 간 관계 분석 강화

---

## 💻 구현 우선순위

### Phase 1: 현재 (JSON 파일 개선)

- [ ] 데이터셋 분할 자동화
- [ ] 압축 저장 옵션
- [ ] 데이터 검증 로직

### Phase 2: 중규모 (SQLite 도입)

- [ ] SQLite 스키마 설계
- [ ] JSON → SQLite 마이그레이션
- [ ] 쿼리 인터페이스 구현

### Phase 3: 대규모 (PostgreSQL)

- [ ] PostgreSQL 스키마 설계
- [ ] 데이터 파이프라인 구축
- [ ] 실시간 업데이트 지원

---

## 🎓 결론

### 현재 단계에서는 **데이터베이스 도입이 불필요**합니다.

**이유**:

1. 데이터 규모가 작음 (수백~수천 건)
2. 배치 처리 방식으로 충분
3. JSON 파일이 더 간단하고 유연함
4. 개발 속도가 더 중요

**하지만**:

- 데이터가 10,000건 이상으로 증가하면 SQLite 고려
- 실시간 업데이트 필요 시 PostgreSQL 도입
- 복잡한 쿼리 필요 시 DB 전환 검토

**권장 접근**:

- 현재는 JSON 파일 유지
- 데이터베이스 인터페이스를 추상화하여 나중에 쉽게 전환 가능하도록 설계
- 데이터가 커지면 점진적으로 전환

---

## 📚 참고 자료

- [SQLite vs JSON for Small Datasets](https://www.sqlite.org/whentouse.html)
- [PostgreSQL JSONB Performance](https://www.postgresql.org/docs/current/datatype-json.html)
- [When to Use a Database vs File Storage](https://stackoverflow.com/questions/1108/how-does-database-acid-and-caps-theorem-fit-together)
