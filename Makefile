.PHONY: dev build publish

all: dev

dev:
	uv run gradio cc dev

build:
	uv run gradio cc build

publish:
	uv run gradio cc publish