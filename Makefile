# Gradio PianoRoll Development Makefile

.PHONY: install dev docs test type-check clean help

# 기본 설치
install:
	pip install -e .

# 개발 환경 설치
dev:
	pip install -e ".[dev]"

# 문서 관련
docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

docs-install:
	pip install -e ".[docs]"

# 타입 관련
type-check:
	python -m mypy backend/gradio_pianoroll/

type-install:
	pip install -e ".[typing]"

# 테스트
test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=backend/gradio_pianoroll --cov-report=html --cov-report=term

test-install:
	pip install -e ".[test]"

test-quick:
	python -m pytest tests/ -v -x --disable-warnings

# 빌드
build:
	python -m build

# 정리
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete

# 도움말
help:
	@echo "Available targets:"
	@echo "  install       - Install package in development mode"
	@echo "  dev           - Install with development dependencies"
	@echo "  docs-serve    - Serve documentation locally"
	@echo "  docs-build    - Build documentation"
	@echo "  docs-install  - Install documentation dependencies"
	@echo "  type-check    - Run type checking with mypy"
	@echo "  type-install  - Install typing dependencies"
	@echo "  test          - Run tests"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  test-install  - Install test dependencies"
	@echo "  test-quick    - Run tests quickly (stop on first failure)"
	@echo "  build         - Build distribution packages"
	@echo "  clean         - Clean build artifacts"
	@echo "  help          - Show this help message" 