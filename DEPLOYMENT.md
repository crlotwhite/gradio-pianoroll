# MkDocs 자동 배포 설정 가이드

이 문서는 GitHub Actions를 통해 MkDocs 문서를 자동으로 빌드하고 GitHub Pages에 배포하는 방법을 설명합니다.

## 설정 완료 사항

✅ **GitHub Actions 워크플로우** (`.github/workflows/docs.yml`)
✅ **MkDocs 의존성 파일** (`docs/requirements.txt`)
✅ **MkDocs 설정 파일** (`mkdocs.yml`)

## GitHub Pages 활성화 방법

1. **GitHub 리포지토리 설정**으로 이동
   - 리포지토리 → Settings → Pages

2. **Source 설정**
   - "Deploy from a branch" 대신 **"GitHub Actions"** 선택

3. **Branch 보호 규칙** (선택사항)
   - Settings → Branches에서 main/master 브랜치 보호 설정

## 자동 배포 트리거

다음과 같은 경우에 문서가 자동으로 빌드되고 배포됩니다:

- `docs/` 디렉토리의 파일 변경
- `mkdocs.yml` 파일 수정
- `.github/workflows/docs.yml` 워크플로우 파일 수정
- main/master 브랜치에 push할 때

## 문서 사이트 URL

배포 완료 후 다음 URL에서 문서를 확인할 수 있습니다:
```
https://crlotwhite.github.io/gradio-pianoroll/
```

## 수동 배포

필요시 GitHub Actions 탭에서 "Deploy MkDocs Documentation" 워크플로우를 수동으로 실행할 수 있습니다.

## 로컬 개발

로컬에서 문서를 미리 확인하려면:

```bash
# 의존성 설치
pip install -r docs/requirements.txt

# 로컬 개발 서버 실행
mkdocs serve

# 빌드 테스트
mkdocs build --clean --strict
```

## 문제 해결

### 빌드 실패 시
1. Actions 탭에서 실패한 워크플로우 로그 확인
2. 로컬에서 `mkdocs build --strict` 실행하여 오류 확인
3. 문서 내 링크나 마크다운 문법 오류 수정

### 배포 권한 오류 시
1. Repository Settings → Actions → General
2. "Workflow permissions"에서 "Read and write permissions" 선택
3. "Allow GitHub Actions to create and approve pull requests" 체크

## 추가 기능

### 브랜치별 미리보기
PR 생성 시 문서 빌드 테스트가 자동으로 실행되어 오류를 사전에 발견할 수 있습니다.

### 캐시 활용
Python 의존성이 캐시되어 빌드 시간이 단축됩니다.

### 빌드 최적화
경고는 로그로 출력되지만 빌드를 중단하지 않아 안정적인 배포가 가능합니다.