# 타입 체크 및 Stub 파일 관리

이 가이드에서는 Gradio PianoRoll 프로젝트의 타입 체크 시스템과 stub 파일 관리에 대해 설명합니다.

## 🔍 현재 타입 시스템 상황

### 타입 힌트 현황
모든 Python 파일들이 이미 완전한 타입 힌트를 포함하고 있습니다:

- ✅ `pianoroll.py`: 완전한 타입 힌트 포함
- ✅ `timing_utils.py`: 완전한 타입 힌트 포함
- ✅ `data_models.py`: TypedDict 정의들 포함
- ✅ `utils/research.py`: 연구자용 함수들 타입 힌트 포함
- ✅ `utils/templates.py`: 템플릿 생성 함수들 타입 힌트 포함

### Stub 파일 (.pyi) 필요성 분석

**현재 상황:**
- 기존 `pianoroll.pyi`는 58KB로 실제 구현보다 더 큼
- 중복 정보가 많아 유지보수 부담
- 실제 구현 파일들에 이미 완전한 타입 힌트 존재

**결론:** 현재 상황에서는 stub 파일이 불필요합니다.

## 🛠️ 개발 도구 사용법

### 기본 개발 의존성 설치

```bash
# 개발 도구들 설치
pip install -e ".[dev]"

# 또는 타입 체크만 필요한 경우
pip install -e ".[quality]"
```

### 통합 개발 도구 스크립트

`scripts/dev_tools.py`를 사용하여 다양한 개발 작업을 수행할 수 있습니다:

```bash
# 기본 타입 체크 및 import 정렬 검사
python scripts/dev_tools.py

# 타입 체크만 실행
python scripts/dev_tools.py --check

# 코드 포맷팅 및 import 정렬 자동 수정
python scripts/dev_tools.py --fix

# 모든 검사 실행 (테스트 포함)
python scripts/dev_tools.py --all

# 테스트만 실행
python scripts/dev_tools.py --test
```

### 개별 도구 사용법

#### 1. MyPy 타입 체크
```bash
# 백엔드 전체 타입 체크
mypy backend/

# 특정 파일만 체크
mypy backend/gradio_pianoroll/pianoroll.py
```

#### 2. Black 코드 포맷팅
```bash
# 백엔드 코드 포맷팅
black backend/

# 포맷팅 미리보기 (실제 변경 없음)
black --diff backend/
```

#### 3. isort Import 정렬
```bash
# import 정렬
isort backend/

# 정렬 필요 여부만 확인
isort --check-only --diff backend/
```

## 📝 Stub 파일 관리 (선택사항)

### 불필요한 Stub 파일 정리

현재 존재하는 불필요한 stub 파일들을 정리하려면:

```bash
python scripts/cleanup_stubs.py
```

이 스크립트는:
1. 해당하는 `.py` 파일에 타입 힌트가 있는지 확인
2. 타입 힌트가 충분하면 `.pyi` 파일 삭제
3. 삭제된 파일들을 리포트

### 새로운 Stub 파일 자동 생성 (필요시)

외부 라이브러리 배포용으로 stub 파일이 필요한 경우:

```bash
python scripts/generate_stubs.py
```

이 스크립트는:
1. mypy의 `stubgen` 도구 사용
2. 올바른 형식의 stub 파일 생성
3. `stubs/` 디렉토리에 출력

### 통합 관리

```bash
# 기존 stub 정리 후 새로 생성
python scripts/dev_tools.py --clean-stubs --gen-stubs
```

## ⚙️ 설정 파일

### pyproject.toml 설정

프로젝트의 모든 도구 설정은 `pyproject.toml`에 중앙화되어 있습니다:

```toml
[tool.mypy]
python_version = "3.10"
strict = true
# ... 기타 엄격한 타입 체크 설정

[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 88
```

### IDE 설정 권장사항

#### VS Code
`.vscode/settings.json`:
```json
{
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"]
}
```

#### PyCharm
1. Settings → Tools → External Tools에서 mypy, black, isort 설정
2. Code Style → Python에서 Black 호환 설정 활성화

## 🚀 CI/CD 통합

### GitHub Actions 예시

```yaml
name: Type Check and Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Run type check and quality tools
      run: |
        python scripts/dev_tools.py --all
```

## 📊 타입 체크 레벨

### 엄격한 타입 체크 (gradio_pianoroll 패키지)
- `disallow_untyped_defs = true`
- `disallow_incomplete_defs = true`
- `strict = true`

### 느슨한 타입 체크 (외부 라이브러리)
- `ignore_missing_imports = true`
- Gradio, NumPy, librosa 등

## 💡 베스트 프랙티스

1. **타입 힌트 우선**: 새 코드 작성 시 항상 타입 힌트 포함
2. **정기적 검사**: 커밋 전 `python scripts/dev_tools.py` 실행
3. **Stub 파일 최소화**: 실제 구현에 타입 힌트가 있으면 stub 불필요
4. **점진적 개선**: 기존 코드의 타입 힌트를 점진적으로 개선

## 🔧 문제 해결

### 일반적인 mypy 오류

#### "Module has no attribute"
```python
# 잘못된 방법
import gradio_pianoroll
pianoroll = gradio_pianoroll.PianoRoll()  # mypy 오류

# 올바른 방법
from gradio_pianoroll import PianoRoll
pianoroll = PianoRoll()
```

#### "Incompatible return value type"
```python
# 명시적 타입 어노테이션 추가
def create_data() -> Dict[str, Any]:
    return {"notes": [], "tempo": 120}
```

### Stub 관련 문제

#### "Conflicting .pyi file"
1. 해당 `.pyi` 파일 삭제 또는
2. `cleanup_stubs.py` 스크립트 실행

#### "Type stub not found"
외부 라이브러리용 stub이 필요한 경우:
```bash
pip install types-requests  # 예시
```

## 📚 추가 자료

- [MyPy 공식 문서](https://mypy.readthedocs.io/)
- [Black 공식 문서](https://black.readthedocs.io/)
- [Python 타입 힌트 가이드](https://docs.python.org/3/library/typing.html)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

## 🔧 자동 Stubgen 실행 방법들

### 방법 1: Hatch Scripts (추천)

`pyproject.toml`에 이미 설정된 Hatch scripts를 사용할 수 있습니다:

```bash
# Hatch 설치 (아직 설치하지 않았다면)
pip install hatch

# Stub 파일 자동 생성
hatch run generate-stubs

# Stub 파일 정리
hatch run clean-stubs

# 정리 후 다시 생성
hatch run build-stubs

# 개발 환경 전체 설정 (품질 검사 + 테스트 + stub 생성)
hatch run dev-setup

# 릴리즈 준비 (모든 검사 + stub 생성)
hatch run prepare-release
```

### 방법 2: 직접 명령어

가장 간단한 방법으로 직접 실행:

```bash
# Stub 파일 생성
python -c "import sys; sys.argv=['stubgen', 'backend/gradio_pianoroll', '-o', 'backend/', '--include-private']; import mypy.stubgen; mypy.stubgen.main()"

# 또는 더 간단하게 (mypy가 PATH에 있다면)
stubgen backend/gradio_pianoroll -o backend/ --include-private
```

### 방법 3: Make 파일

`Makefile`을 만들어서 사용:

```makefile
.PHONY: stubs clean-stubs type-check

stubs:
	@echo "🔧 Generating stub files..."
	@python -c "import shutil; shutil.rmtree('stubs', ignore_errors=True)"
	@python -c "import sys; sys.argv=['stubgen', 'backend/gradio_pianoroll', '-o', 'stubs', '--include-private']; import mypy.stubgen; mypy.stubgen.main()"
	@echo "✅ Stub files generated in stubs/ directory"

clean-stubs:
	@echo "🗑️ Cleaning stub files..."
	@python -c "import shutil; shutil.rmtree('stubs', ignore_errors=True)"
	@echo "✅ Stub files cleaned"

type-check:
	@echo "🔍 Type checking..."
	@mypy backend/

quality: type-check
	@black backend/
	@isort backend/
	@echo "✅ Code quality checks completed"

dev-setup: quality stubs
	@echo "🚀 Development setup completed"
```

사용법:
```bash
make stubs        # Stub 생성
make clean-stubs  # Stub 정리
make dev-setup    # 전체 개발 환경 설정
```

### 방법 4: Pre-commit Hook

Git 커밋 전에 자동으로 실행되도록 설정:

```yaml
# .pre-commit-config.yaml (이미 생성됨)
repos:
  - repo: local
    hooks:
      - id: stubgen
        name: Generate type stubs
        entry: python -c "import sys; sys.argv=['stubgen', 'backend/gradio_pianoroll', '-o', 'stubs', '--include-private']; import mypy.stubgen; mypy.stubgen.main()"
        language: system
        files: ^backend/gradio_pianoroll/.*\.py$
        pass_filenames: false
        verbose: true
```

설치 및 사용:
```bash
pip install pre-commit
pre-commit install
git commit -m "Update code"  # 자동으로 stubgen 실행
```

### 방법 5: NPM Scripts (Node.js가 있다면)

`package.json` 생성:

```json
{
  "name": "gradio-pianoroll-dev",
  "scripts": {
    "stubs": "python -c \"import sys; sys.argv=['stubgen', 'backend/gradio_pianoroll', '-o', 'stubs', '--include-private']; import mypy.stubgen; mypy.stubgen.main()\"",
    "clean-stubs": "python -c \"import shutil; shutil.rmtree('stubs', ignore_errors=True)\"",
    "type-check": "mypy backend/",
    "format": "black backend/ && isort backend/",
    "dev-setup": "npm run format && npm run type-check && npm run stubs"
  }
}
```

사용법:
```bash
npm run stubs      # Stub 생성
npm run dev-setup  # 전체 개발 환경 설정
```

## 🎯 권장사항

현재 프로젝트 상황에 맞는 **추천 방법**:

1. **일반 개발**: `hatch run generate-stubs` (Hatch scripts 사용)
2. **CI/CD**: 직접 명령어 사용 (환경 의존성 최소화)
3. **팀 개발**: Pre-commit hook (일관성 보장)
4. **간단한 사용**: `make stubs` (Make 파일)

### 현재 설정된 Hatch Commands

```bash
# 개발 도구들
hatch run type-check     # 타입 체크
hatch run format         # 코드 포맷팅
hatch run sort-imports   # Import 정렬
hatch run lint           # 린팅

# Stub 관련
hatch run generate-stubs # Stub 생성
hatch run clean-stubs    # Stub 정리
hatch run build-stubs    # 정리 후 생성

# 통합 명령어들
hatch run quality        # 모든 품질 검사
hatch run dev-setup      # 개발 환경 설정
hatch run prepare-release # 릴리즈 준비
```

모든 설정이 `pyproject.toml`에 포함되어 있어서, 별도 설정 파일 없이 바로 사용할 수 있습니다! 🎉