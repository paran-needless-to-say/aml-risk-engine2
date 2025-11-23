# 백엔드 서버 설정 가이드

## 🚨 문제: ModuleNotFoundError

백엔드 서버를 실행할 때 다음과 같은 오류가 발생할 수 있습니다:

```
ModuleNotFoundError: No module named 'flask_cors'
```

이는 Python 의존성이 설치되지 않았기 때문입니다.

---

## ✅ 해결 방법

### 방법 1: 가상환경 사용 (권장)

#### 1. 가상환경 생성

```bash
cd /Users/yelim/Desktop/파란학기/Cryptocurrency-Graphs-of-graphs
python3 -m venv venv
```

#### 2. 가상환경 활성화

```bash
source venv/bin/activate
```

터미널 프롬프트 앞에 `(venv)`가 표시되면 성공입니다.

#### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

#### 4. 백엔드 서버 실행

```bash
python3 api/app.py
```

#### 5. 가상환경 비활성화 (작업 완료 후)

```bash
deactivate
```

---

### 방법 2: --user 플래그 사용 (시스템 패키지 보호 우회)

```bash
cd /Users/yelim/Desktop/파란학기/Cryptocurrency-Graphs-of-graphs
python3 -m pip install --user -r requirements.txt
```

**주의**: 시스템 Python에 패키지를 설치하므로 권장하지 않습니다.

---

### 방법 3: --break-system-packages 플래그 사용 (비권장)

```bash
cd /Users/yelim/Desktop/파란학기/Cryptocurrency-Graphs-of-graphs
python3 -m pip install --break-system-packages -r requirements.txt
```

**주의**: 시스템 Python을 손상시킬 수 있으므로 권장하지 않습니다.

---

## 📋 전체 실행 순서 (가상환경 사용)

### 처음 한 번만 실행

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/yelim/Desktop/파란학기/Cryptocurrency-Graphs-of-graphs

# 2. 가상환경 생성
python3 -m venv venv

# 3. 가상환경 활성화
source venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt
```

### 매번 실행할 때

**방법 1: 실행 스크립트 사용 (권장)**

```bash
# 1. 프로젝트 디렉토리로 이동 (중요!)
cd /Users/yelim/Desktop/파란학기/Cryptocurrency-Graphs-of-graphs

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 백엔드 서버 실행
python3 run_server.py
```

**방법 2: 모듈로 실행**

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/yelim/Desktop/파란학기/Cryptocurrency-Graphs-of-graphs

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 백엔드 서버 실행 (모듈로 실행)
python3 -m api.app
```

**⚠️ 주의**:

- `frontend` 디렉토리가 아닌 `Cryptocurrency-Graphs-of-graphs` 디렉토리에서 실행해야 합니다!
- `python3 api/app.py`로 직접 실행하면 `ModuleNotFoundError`가 발생합니다.

---

## 🔍 설치 확인

의존성이 제대로 설치되었는지 확인:

```bash
source venv/bin/activate
python3 -c "import flask; import flask_cors; import flasgger; print('✅ 모든 패키지 설치 완료')"
```

---

## ⚠️ 문제 해결

### 가상환경이 활성화되지 않는 경우

```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### pip 업그레이드 필요

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📦 설치되는 주요 패키지

- `flask`: 웹 프레임워크
- `flask-cors`: CORS 지원
- `flasgger`: Swagger/OpenAPI 문서 생성
- `pyyaml`: YAML 파싱
- `networkx`: 그래프 분석
- `pandas`: 데이터 처리
- `numpy`: 수치 계산
- `requests`: HTTP 요청

---

## 💡 팁

### 가상환경 자동 활성화 (선택사항)

`.zshrc` 또는 `.bashrc`에 다음을 추가하면 프로젝트 디렉토리로 이동할 때 자동으로 가상환경이 활성화됩니다:

```bash
# .zshrc 또는 .bashrc에 추가
cd() {
  builtin cd "$@"
  if [[ -f venv/bin/activate ]]; then
    source venv/bin/activate
  fi
}
```

---

## 📚 관련 문서

- `RUN_DEMO.md`: 프론트엔드 실행 가이드
- `README.md`: 프로젝트 전체 개요
