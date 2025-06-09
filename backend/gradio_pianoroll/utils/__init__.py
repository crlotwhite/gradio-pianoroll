"""
연구자용 유틸리티 모듈

이 패키지는 연구자들이 피아노롤 컴포넌트를 보다 쉽게 사용할 수 있도록
다양한 헬퍼 함수와 템플릿을 제공합니다.

모든 유틸리티는 선택적으로 import할 수 있으며, 메인 컴포넌트와는
독립적으로 작동합니다.

사용 예시:
    from gradio_pianoroll import PianoRoll
    from gradio_pianoroll.utils import research

    # 연구자용 편의 함수 사용
    data = research.from_notes([(60, 0, 1), (64, 1, 1)])
    piano_roll = PianoRoll(value=data)
"""

# 각 모듈을 lazy import로 제공
__all__ = []


def __getattr__(name: str):
    """Lazy import for utility modules"""
    if name == "research":
        from . import research

        return research
    elif name == "templates":
        from . import templates

        return templates
    elif name == "converters":
        from . import converters

        return converters
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
