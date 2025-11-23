# 배포 가이드

백엔드 팀을 위한 API 배포 및 사용 가이드입니다.

## 배포 준비 완료 체크리스트

- [x] API 엔드포인트 구현 완료
- [x] Swagger 문서 자동 생성
- [x] CORS 설정 완료
- [x] Health check 엔드포인트
- [x] 의존성 파일 (requirements.txt)
- [x] 서버 실행 스크립트 (run_server.py)
- [x] 기본 문서 (README.md, API_DOCUMENTATION.md)

---

## 빠른 시작

### 1. 저장소 클론

```bash
git clone <repository-url>
cd Cryptocurrency-Graphs-of-graphs
```

### 2. 의존성 설치

```bash
# Python 3.10+ 필요
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python3 run_server.py
```

서버가 `http://localhost:5001` (또는 5002)에서 실행됩니다.

### 4. API 문서 확인

브라우저에서 `http://localhost:5001/api-docs` 접속

---

## 주요 API 엔드포인트

### 1. 단일 트랜잭션 스코어링

```
POST /api/score/transaction
```

**요청 예시:**

```json
{
  "tx_hash": "0x123...",
  "chain": "ethereum",
  "timestamp": "2025-11-19T10:00:00Z",
  "block_height": 21039493,
  "target_address": "0xabc123...",
  "counterparty_address": "0xdef456...",
  "label": "mixer",
  "is_sanctioned": true,
  "is_known_scam": false,
  "is_mixer": true,
  "is_bridge": false,
  "amount_usd": 500000.0,
  "asset_contract": "0xETH"
}
```

**응답 예시:**

```json
{
  "target_address": "0xabc123...",
  "risk_score": 95,
  "risk_level": "critical",
  "risk_tags": ["mixer_inflow", "sanction_exposure"],
  "fired_rules": [
    { "rule_id": "E-101", "score": 25 },
    { "rule_id": "C-001", "score": 30 }
  ],
  "explanation": "...",
  "completed_at": "2025-11-19T10:00:01Z",
  "timestamp": "2025-11-19T10:00:00Z",
  "chain_id": 1,
  "value": 500000.0
}
```

### 2. 주소 분석 (다중 트랜잭션)

```
POST /api/analyze/address
```

**요청 예시:**

```json
{
  "address": "0xabc123...",
  "chain_id": 1,
  "transactions": [
    {
      "tx_hash": "0x123...",
      "chain_id": 1,
      "timestamp": "2025-11-19T10:00:00Z",
      "block_height": 21039493,
      "target_address": "0xabc123...",
      "counterparty_address": "0xdef456...",
      "label": "mixer",
      "is_sanctioned": true,
      "is_known_scam": false,
      "is_mixer": true,
      "is_bridge": false,
      "amount_usd": 500000.0,
      "asset_contract": "0xETH"
    }
  ],
  "analysis_type": "basic"
}
```

**응답 형식:** 단일 트랜잭션 스코어링과 동일

### 3. Health Check

```
GET /health
```

**응답:**

```json
{
  "status": "ok",
  "service": "aml-risk-engine"
}
```

---

## 🔧 환경 설정

### 포트 설정

기본 포트는 **5001**입니다. 포트를 변경하려면:

1. `run_server.py` 파일에서 `port` 변수 수정
2. 또는 환경 변수 사용 (향후 지원 예정)

### Etherscan API 키 (선택사항)

Etherscan API를 사용하는 경우:

```bash
export ETHERSCAN_API_KEY="your_api_key_here"
```

기본값이 설정되어 있어 필수는 아닙니다.

---

## 📋 필수 데이터 파일

다음 파일들이 `data/lists/` 디렉토리에 있어야 합니다:

- `sdn_addresses.json` - OFAC SDN 리스트 (제재 대상 주소)
- `cex_addresses.json` - CEX 주소 리스트
- `bridge_contracts.json` - Bridge 컨트랙트 주소
- `scam_addresses.json` - 사기 주소 리스트 (선택사항)

이 파일들은 저장소에 포함되어 있습니다.

---

## 🐳 Docker 배포 (선택사항)

Docker를 사용하는 경우:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001
CMD ["python3", "run_server.py"]
```

```bash
docker build -t aml-risk-engine .
docker run -p 5001:5001 aml-risk-engine
```

---

## 🔍 문제 해결

### 포트 충돌

포트가 사용 중인 경우 `run_server.py`가 자동으로 다른 포트(5002)로 변경합니다.

### 모듈을 찾을 수 없음

```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

### CORS 오류

CORS는 이미 설정되어 있습니다. 프론트엔드에서 호출 시 문제가 있으면 `api/app.py`의 CORS 설정을 확인하세요.

---

## 추가 문서

- **API 상세 명세**: `docs/API_DOCUMENTATION.md`
- **입출력 명세**: `docs/RISK_SCORING_IO.md`
- **프로젝트 개요**: `README.md`
- **시스템 개요**: `docs/SYSTEM_OVERVIEW.md`

---

## 백엔드 연동 팁

1. **요청 형식**: 모든 필드는 필수입니다. `label`은 `entity_type`으로도 받을 수 있습니다 (하위 호환성).

2. **응답 형식**:

   - `risk_score`: 0~100 정수
   - `risk_level`: "low" | "medium" | "high" | "critical"
   - `chain_id`: 숫자 (예: 1=Ethereum, 42161=Arbitrum, 43114=Avalanche)
   - `value`: `amount_usd`와 동일한 값 (USD)

3. **성능**:

   - `analysis_type: "basic"`: 1-2초 (기본값, 권장)
   - `analysis_type: "advanced"`: 5-30초 (심층 분석)

4. **에러 처리**: 모든 에러는 JSON 형식으로 반환됩니다:
   ```json
   {
     "error": "Missing required field: tx_hash"
   }
   ```

---

## 배포 완료 확인

서버 실행 후 다음을 확인하세요:

1. Health check: `curl http://localhost:5001/health`
2. Swagger 문서: 브라우저에서 `http://localhost:5001/api-docs` 접속
3. API 테스트: Swagger UI에서 "Try it out" 버튼으로 테스트

---

**문의사항이 있으면 이슈를 등록하거나 팀에 문의하세요!**
