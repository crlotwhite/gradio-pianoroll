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
uv run gradio cc dev

# 또는 특정 디렉토리 지정
uv run gradio cc dev ./
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
uv run gradio cc build
```

빌드 결과:
- `dist/` 디렉토리에 `.tar.gz`와 `.whl` 파일 생성
- 자동으로 문서 생성 (비활성화: `--no-generate-docs`)

### 4. 배포 (publish)

#### PyPI 배포

```bash
# PyPI에 배포
uv run gradio cc publish
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
uv run gradio cc publish

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

---

## Playwright E2E 테스트

Playwright를 사용하여 Gradio 앱의 End-to-End 테스트를 수행할 수 있습니다.

### Playwright 설치

```bash
# Playwright 설치
uv pip install playwright pytest-playwright

# 브라우저 바이너리 설치
playwright install

# 특정 브라우저만 설치
playwright install chromium

# Linux에서 OS 의존성 포함 설치
playwright install --with-deps
```

### 테스트 구조

테스트 파일은 `tests/e2e/` 디렉토리에 위치합니다:

```
tests/
├── e2e/
│   ├── conftest.py          # Pytest fixtures (Gradio 앱 서버 설정)
│   ├── test_pianoroll.py    # 피아노롤 컴포넌트 테스트
│   └── test_demo_app.py     # 데모 앱 통합 테스트
```

### conftest.py 설정

Gradio 앱을 테스트하기 위한 기본 fixture 설정:

```python
import pytest
from playwright.sync_api import Page, expect
import subprocess
import time
import socket

def find_free_port():
    """사용 가능한 포트 찾기"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

@pytest.fixture(scope="session")
def gradio_server():
    """Gradio 데모 서버 시작"""
    port = find_free_port()
    process = subprocess.Popen(
        ["python", "demo/app.py"],
        env={**os.environ, "GRADIO_SERVER_PORT": str(port)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 서버 시작 대기
    time.sleep(5)
    
    yield f"http://localhost:{port}"
    
    # 테스트 후 서버 종료
    process.terminate()
    process.wait()

@pytest.fixture
def page_with_app(page: Page, gradio_server: str):
    """Gradio 앱이 로드된 페이지 제공"""
    page.goto(gradio_server)
    page.wait_for_load_state("networkidle")
    return page
```

### 기본 테스트 작성

```python
from playwright.sync_api import Page, expect
import pytest

def test_pianoroll_loads(page_with_app: Page):
    """피아노롤 컴포넌트가 로드되는지 확인"""
    # 피아노롤 캔버스 확인
    pianoroll = page_with_app.locator(".pianoroll-container")
    expect(pianoroll).to_be_visible()

def test_keyboard_visible(page_with_app: Page):
    """키보드 컴포넌트가 표시되는지 확인"""
    keyboard = page_with_app.locator(".keyboard")
    expect(keyboard).to_be_visible()

def test_note_creation(page_with_app: Page):
    """노트 생성 테스트"""
    canvas = page_with_app.locator("canvas.grid-canvas")
    
    # 캔버스 클릭으로 노트 생성
    canvas.click(position={"x": 100, "y": 200})
    
    # 노트가 생성되었는지 확인
    page_with_app.wait_for_timeout(500)
    # 노트 관련 상태 확인 로직 추가

def test_toolbar_buttons(page_with_app: Page):
    """툴바 버튼 테스트"""
    # 각 툴바 버튼 확인
    play_button = page_with_app.get_by_role("button", name="Play")
    expect(play_button).to_be_visible()
    expect(play_button).to_be_enabled()
```

### 마우스/터치 인터랙션 테스트

```python
def test_drag_note(page_with_app: Page):
    """노트 드래그 테스트"""
    canvas = page_with_app.locator("canvas.grid-canvas")
    
    # 드래그 앤 드롭
    page_with_app.mouse.move(100, 200)
    page_with_app.mouse.down()
    page_with_app.mouse.move(200, 200, steps=10)
    page_with_app.mouse.up()

def test_zoom_with_scroll(page_with_app: Page):
    """스크롤을 통한 줌 테스트"""
    canvas = page_with_app.locator("canvas.grid-canvas")
    
    # Ctrl + 스크롤로 줌
    canvas.hover()
    page_with_app.keyboard.down("Control")
    page_with_app.mouse.wheel(0, -100)  # 줌 인
    page_with_app.keyboard.up("Control")
```

### 스크린샷 및 비디오 녹화

```python
def test_with_screenshot(page_with_app: Page):
    """스크린샷 캡처 테스트"""
    # 전체 페이지 스크린샷
    page_with_app.screenshot(path="screenshots/full-page.png", full_page=True)
    
    # 특정 요소 스크린샷
    pianoroll = page_with_app.locator(".pianoroll-container")
    pianoroll.screenshot(path="screenshots/pianoroll.png")

# pytest.ini 또는 conftest.py에서 비디오 녹화 설정
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "record_video_dir": "videos/",
        "record_video_size": {"width": 1280, "height": 720}
    }
```

### 테스트 실행

```bash
# 모든 E2E 테스트 실행
uv run pytest tests/e2e/ --browser chromium

# 특정 브라우저로 테스트
uv run pytest tests/e2e/ --browser firefox
uv run pytest tests/e2e/ --browser webkit

# 모든 브라우저에서 테스트
uv run pytest tests/e2e/ --browser chromium --browser firefox --browser webkit

# 헤드리스 모드 비활성화 (디버깅용)
uv run pytest tests/e2e/ --browser chromium --headed

# 슬로우 모션으로 실행 (디버깅용)
uv run pytest tests/e2e/ --browser chromium --headed --slowmo 500

# 특정 테스트만 실행
uv run pytest tests/e2e/test_pianoroll.py::test_note_creation --browser chromium

# 병렬 실행
uv run pytest tests/e2e/ --browser chromium -n auto
```

### 트레이싱 및 디버깅

```bash
# 트레이스 파일 생성
uv run pytest tests/e2e/ --browser chromium --tracing on

# 트레이스 뷰어로 분석
playwright show-trace trace.zip
```

```python
# 테스트 코드에서 트레이싱 활성화
def test_with_tracing(page_with_app: Page, context):
    """트레이싱이 포함된 테스트"""
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    
    # 테스트 수행
    page_with_app.click("button#play")
    
    context.tracing.stop(path="trace.zip")
```

### CI/CD 통합 (GitHub Actions)

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Install dependencies
        run: |
          uv pip install -e ".[dev]"
          uv pip install playwright pytest-playwright
          playwright install --with-deps chromium
      
      - name: Run E2E tests
        run: uv run pytest tests/e2e/ --browser chromium
      
      - name: Upload artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-results
          path: |
            screenshots/
            videos/
            trace.zip
```

### 모바일 뷰포트 테스트

```python
@pytest.fixture
def mobile_page(browser):
    """모바일 뷰포트 설정"""
    context = browser.new_context(
        viewport={"width": 375, "height": 667},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True
    )
    page = context.new_page()
    yield page
    context.close()

def test_mobile_responsive(mobile_page: Page, gradio_server: str):
    """모바일 반응형 테스트"""
    mobile_page.goto(gradio_server)
    mobile_page.wait_for_load_state("networkidle")
    
    # 모바일에서 피아노롤이 적절히 표시되는지 확인
    pianoroll = mobile_page.locator(".pianoroll-container")
    expect(pianoroll).to_be_visible()
```

### 네트워크 요청 모킹

```python
def test_with_mocked_api(page_with_app: Page):
    """API 응답 모킹 테스트"""
    # API 응답 모킹
    page_with_app.route("**/api/analyze", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"notes": [], "tempo": 120}'
    ))
    
    # 분석 버튼 클릭
    page_with_app.click("button#analyze")
    
    # 결과 확인
    expect(page_with_app.locator(".analysis-result")).to_be_visible()
```

### 유용한 팁

1. **선택자 우선순위**: `get_by_role()` > `get_by_test_id()` > CSS 선택자
2. **명시적 대기**: `wait_for_selector()`, `wait_for_load_state()` 활용
3. **테스트 격리**: 각 테스트는 독립적으로 실행되어야 함
4. **재시도 로직**: flaky 테스트 방지를 위해 `expect()` 사용 (자동 재시도)
5. **디버깅**: `page.pause()` 사용하여 브라우저 일시 정지

```python
def test_debug_example(page_with_app: Page):
    """디버깅 예제"""
    # 여기서 브라우저가 일시 정지됨
    page_with_app.pause()
    
    # Inspector에서 상호작용 후 계속 진행
    page_with_app.click("button#submit")
```
