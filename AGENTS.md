# AGENTS.md

이 문서는 AI 에이전트와 개발자가 `gradio_pianoroll` 프로젝트를 이해하고 작업할 수 있도록 안내합니다.

## 프로젝트 개요

`gradio_pianoroll`은 Gradio용 커스텀 피아노롤 컴포넌트입니다. 오디오 분석, F0 추적, 음성 합성 등의 기능을 제공하는 인터랙티브 피아노롤 UI를 구현합니다.

### 기술 스택

- **Backend**: Python 3.10+, Gradio 4.0~6.0
- **Frontend**: Svelte 4, TypeScript
- **패키지 관리**: uv (Python), npm (Node.js)
- **빌드 시스템**: Hatchling

## 프로젝트 구조

```
gradio-pianoroll/
├── backend/
│   └── gradio_pianoroll/     # Python 백엔드 코드
│       ├── __init__.py
│       ├── pianoroll.py      # 메인 컴포넌트
│       ├── data_models.py    # 데이터 모델
│       └── utils/            # 유틸리티 함수
├── frontend/                  # Svelte 프론트엔드
│   ├── Index.svelte          # 메인 컴포넌트
│   ├── components/           # UI 컴포넌트
│   ├── types/                # TypeScript 타입 정의
│   └── utils/                # 유틸리티 및 레이어 시스템
├── demo/                      # 데모 애플리케이션
│   ├── app.py                # 메인 데모 앱
│   └── space.py              # HuggingFace Space용
├── examples/                  # 예제 코드
├── docs/                      # 문서 (MkDocs)
└── pyproject.toml            # 프로젝트 설정
```

---

## 필수 요구사항

- Python 3.10+
- Node.js 20+
- npm 9+
- pip 21.3+ 또는 uv

---

## uv를 사용한 개발 환경 설정

[uv](https://docs.astral.sh/uv/)는 빠른 Python 패키지 관리자입니다. 이 프로젝트에서는 uv 사용을 권장합니다.

### uv 설치

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 가상환경 생성 및 활성화

```bash
# 가상환경 생성
uv venv

# Windows에서 활성화
.venv\Scripts\activate

# macOS/Linux에서 활성화
source .venv/bin/activate
```

### 의존성 설치

```bash
# 프로젝트 의존성 설치 (개발 모드)
uv pip install -e .

# 개발 의존성 설치
uv pip install -e ".[dev]"

# 문서 빌드 의존성 설치
uv sync --group docs
```

### 일반적인 uv 명령어

```bash
# 패키지 설치
uv pip install <package>

# 패키지 제거
uv pip uninstall <package>

# 설치된 패키지 목록
uv pip list

# requirements.txt에서 설치
uv pip install -r requirements.txt

# 캐시 정리
uv cache clean
```

---

## Gradio 커스텀 컴포넌트 개발 워크플로우

Gradio 커스텀 컴포넌트는 4단계 워크플로우를 따릅니다: **create → dev → build → publish**

### 1. 개발 서버 실행 (dev)

개발 중에는 핫 리로딩이 지원되는 개발 서버를 사용합니다:

```bash
# 프로젝트 루트에서 실행
gradio cc dev

# 또는 특정 디렉토리 지정
gradio cc dev ./
```

개발 서버가 시작되면 콘솔에 표시된 URL(기본: http://localhost:7861/)로 접속합니다. 
코드 변경 시 자동으로 리로딩됩니다.

### 2. 프론트엔드 개발

프론트엔드는 Svelte 4와 TypeScript로 작성됩니다:

```bash
# frontend 디렉토리로 이동
cd frontend

# npm 의존성 설치
npm install

# 타입 체크
npx tsc --noEmit
```

### 3. 빌드 (build)

배포를 위한 패키지 빌드:

```bash
# 프로젝트 루트에서 실행
gradio cc build
```

빌드 결과:
- `dist/` 디렉토리에 `.tar.gz`와 `.whl` 파일 생성
- 자동으로 문서 생성 (비활성화: `--no-generate-docs`)

### 4. 배포 (publish)

#### PyPI 배포

```bash
# PyPI에 배포
gradio cc publish
```

배포 시 필요한 정보:
- PyPI 사용자 이름과 비밀번호 (또는 API 토큰)
- HuggingFace Space 배포 옵션 (선택)

#### 수동 배포 (uv/pip 사용)

```bash
# 빌드
uv build
# 또는
python -m build

# twine으로 PyPI 업로드
twine upload dist/*
```

### 5. HuggingFace Space 배포

```bash
# Space 배포 (publish 과정에서 선택 가능)
gradio cc publish

# 또는 직접 Space에 푸시
# space.py 파일이 HuggingFace Space의 진입점입니다
```

---

## 코드 품질 도구

### 린팅 및 포맷팅

```bash
# Ruff 린터 실행
uv run ruff check .

# Ruff 자동 수정
uv run ruff check --fix .

# Black 포맷팅
uv run black .

# isort import 정렬
uv run isort .
```

### 타입 체크

```bash
# mypy 타입 체크
uv run mypy backend/
```

### 테스트

```bash
# pytest 실행
uv run pytest
```

---

## 문서 빌드

MkDocs를 사용하여 문서를 빌드합니다:

```bash
# 문서 의존성 설치
uv sync --group docs

# 로컬 문서 서버 실행
uv run mkdocs serve

# 정적 문서 빌드
uv run mkdocs build
```

---

## 예제 실행

```bash
# 간단한 데모
uv run python examples/simple_demo.py

# 전체 데모 앱
uv run python demo/app.py

# F0 분석 데모 (librosa 필요)
uv run python examples/f0_demo.py
```

---

## 개발 가이드라인

### 커밋 전 체크리스트

1. 린터 통과: `uv run ruff check .`
2. 포맷팅 확인: `uv run black --check .`
3. 타입 체크: `uv run mypy backend/`
4. 테스트 통과: `uv run pytest`

### 버전 관리

버전은 `pyproject.toml`과 `frontend/package.json`에서 관리됩니다:

- `pyproject.toml`: `version = "0.0.9"`
- `package.json`: `"version": "0.4.22"`

### 브랜치 전략

- `main`: 프로덕션 브랜치
- 기능 개발: `feature/<feature-name>`
- 버그 수정: `fix/<bug-description>`

---

## 유용한 링크

- [PyPI 패키지](https://pypi.org/project/gradio_pianoroll/)
- [HuggingFace Space](https://huggingface.co/spaces/crlotwhite/gradio_pianoroll)
- [GitHub 리포지토리](https://github.com/crlotwhite/gradio-pianoroll)
- [Gradio 커스텀 컴포넌트 가이드](https://www.gradio.app/guides/custom-components-in-five-minutes)
- [uv 문서](https://docs.astral.sh/uv/)

---

## 트러블슈팅

### 일반적인 문제

**개발 서버가 시작되지 않는 경우:**
```bash
# Node.js 버전 확인 (20+ 필요)
node --version

# npm 버전 확인 (9+ 필요)
npm --version

# frontend 의존성 재설치
cd frontend && npm install
```

**빌드 실패 시:**
```bash
# 빌드 캐시 정리
rm -rf dist/ build/

# frontend 빌드 캐시 정리
cd frontend && rm -rf node_modules && npm install
```

**타입 에러 발생 시:**
```bash
# TypeScript 버전 확인
cd frontend && npx tsc --version

# 타입 정의 재생성
npx tsc --noEmit
```
