from pathlib import Path

from .strip_comments import strip_comments


def embedded_text(source: Path, language: str, strip: bool) -> bytes:
    text = source.read_bytes()
    return strip_comments(text, language) if strip else text
