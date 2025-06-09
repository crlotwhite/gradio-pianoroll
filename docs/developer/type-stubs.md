# 타입 스텁 (.pyi) 파일 관리

이 가이드는 gradio-pianoroll 프로젝트의 타입 스텁 파일을 관리하는 방법을 설명합니다.

## 개요

타입 스텁 파일(.pyi)은 Python 코드의 타입 정보를 별도로 제공하여 타입 체커(mypy, PyLance 등)와 IDE에서 더 나은 타입 힌트와 자동완성을 제공합니다.

## 현재 상태

### 자동으로 관리되는 파일들

- `backend/gradio_pianoroll/pianoroll.pyi` - 메인 PianoRoll 컴포넌트
- `backend/gradio_pianoroll/backend_data.pyi` - PianoRollBackendData 클래스
- `backend/gradio_pianoroll/note.pyi` - Note 클래스
- `backend/gradio_pianoroll/audio_utils.pyi` - 오디오 유틸리티 함수들
- `backend/gradio_pianoroll/timing_utils.pyi` - 타이밍 계산 함수들

### 빌드 설정

`pyproject.toml`에서 타입 스텁 파일들이 패키지에 포함되도록 설정되어 있습니다:

```toml
[tool.hatch.build]
artifacts = ["/backend/gradio_pianoroll/templates", "*.pyi"]
```

## 스텁 파일 생성

### 수동 생성

개별 모듈에 대해 mypy의 stubgen을 사용하여 스텁을 생성할 수 있습니다:

```bash
# mypy 설치 (개발 의존성에 포함됨)
pip install -e ".[dev]"

# 특정 모듈의 스텁 생성
python -m mypy.stubgen --module backend.gradio_pianoroll.pianoroll --output .
```

### 자동 생성 (선택사항)

필요한 경우 개별 모듈에 대해 mypy stubgen을 직접 사용할 수 있습니다:

```bash
# 새로운 모듈 추가 시에만 사용
python -m mypy.stubgen --module backend.gradio_pianoroll.new_module --output .
```

## MyPy 설정

프로젝트의 mypy 설정은 `pyproject.toml`에 정의되어 있습니다:

```toml
[tool.mypy]
python_version = "3.10"
strict = true
# ... 기타 설정들

[[tool.mypy.overrides]]
module = "gradio.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "numpy.*"
ignore_missing_imports = true
```

## 타입 체크 실행

모든 백엔드 코드에 대해 타입 체크를 실행하려면:

```bash
python -m mypy backend/gradio_pianoroll/
```

## 주의사항

### 관리 방식

현재 프로젝트는 **수동 관리** 방식을 채택하고 있습니다:

- **장점**: 더 정확하고 완전한 타입 정보 제공
- **관리**: 코드 변경 시 해당 `.pyi` 파일도 함께 업데이트
- **규모**: 5개 모듈로 수동 관리가 충분히 가능

### 버전 관리

`.pyi` 파일은 Git에서 관리되며, 코드 변경 시 함께 커밋해야 합니다.

## 개발 워크플로우

1. **코드 수정**: Python 소스 코드 수정
2. **스텁 업데이트**: 해당하는 `.pyi` 파일 수정
3. **타입 체크**: `mypy`로 타입 오류 확인
4. **테스트**: 기능 테스트 실행
5. **커밋**: 소스 코드와 스텁 파일 함께 커밋

## 자주 발생하는 문제

### Import 오류

스텁 파일에서 import 오류가 발생할 경우:

1. 필요한 타입을 적절히 import했는지 확인
2. `typing` 모듈의 타입들을 사용했는지 확인
3. 상대 임포트 경로가 올바른지 확인

### 타입 불일치

실제 구현과 스텁의 타입이 다른 경우:

1. 스텁 파일의 타입 정의를 구현에 맞게 수정
2. 필요한 경우 `Union`, `Optional` 등을 사용
3. 복잡한 타입은 `TypeVar`나 `Generic`을 활용

## 참고 자료

- [MyPy 공식 문서](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 561 - Distributing and Packaging Type Information](https://peps.python.org/pep-0561/) 