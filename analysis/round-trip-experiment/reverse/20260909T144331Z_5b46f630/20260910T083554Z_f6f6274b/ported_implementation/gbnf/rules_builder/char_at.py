from typing import Optional


def char_at(src: str, pos: int) -> Optional[str]:
    """Index a string the way JavaScript does: out of range yields nothing rather than
    raising."""
    if 0 <= pos < len(src):
        return src[pos]
    return None
