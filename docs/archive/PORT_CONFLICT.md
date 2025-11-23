# 포트 충돌 문제 해결 가이드

## 🚨 문제: Port 5000 is in use

백엔드 서버를 실행할 때 다음과 같은 오류가 발생할 수 있습니다:

```
Port 5000 is in use by another program. Either identify and stop that program, or start the server with a different port.
```

---

## ✅ 해결 방법

### 방법 1: 자동 포트 변경 (권장)

`run_server.py`가 포트 5000이 사용 중이면 자동으로 포트 5001로 변경합니다.

**프론트엔드도 포트 5001로 변경 필요**:
- `frontend/src/services/api.ts`의 `API_BASE_URL`을 `http://localhost:5001`로 변경

### 방법 2: 포트 5000 사용 중인 프로세스 종료

```bash
# 포트 5000 사용 중인 프로세스 확인
lsof -ti:5000

# 프로세스 종료
lsof -ti:5000 | xargs kill -9
```

**주의**: 시스템 프로세스를 종료하면 안 됩니다. 백엔드 서버만 종료하세요.

### 방법 3: AirPlay Receiver 비활성화 (macOS)

macOS에서 AirPlay Receiver가 포트 5000을 사용할 수 있습니다.

1. 시스템 설정 열기
2. 일반 > AirDrop 및 Handoff
3. AirPlay 수신기 끄기

---

## 🔧 포트 변경 방법

### 백엔드 포트 변경

`run_server.py` 파일에서 포트를 직접 변경:

```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 5001로 변경
```

### 프론트엔드 포트 변경

`frontend/src/services/api.ts` 파일에서 포트 변경:

```typescript
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5001";  // 5001로 변경
```

또는 환경 변수 설정:

```bash
# .env 파일 생성
cd frontend
echo "VITE_API_BASE_URL=http://localhost:5001" > .env
```

---

## 📋 권장 포트

- **백엔드**: 5001 (기본값 5000이 사용 중일 때)
- **프론트엔드**: 5173 (Vite 기본값)

---

## 🔍 포트 사용 확인

### 포트 5000 사용 중인 프로세스 확인

```bash
lsof -i :5000
```

### 포트 5001 사용 중인 프로세스 확인

```bash
lsof -i :5001
```

---

## 💡 팁

### 환경 변수 사용

프로젝트 루트에 `.env` 파일을 생성하여 포트를 관리할 수 있습니다:

```bash
# .env 파일
BACKEND_PORT=5001
FRONTEND_PORT=5173
```

---

## 📚 관련 문서

- `SETUP_BACKEND.md`: 백엔드 설정 가이드
- `RUN_DEMO.md`: 프론트엔드 실행 가이드

