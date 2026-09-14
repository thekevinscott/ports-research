from typing import Optional


def char_at(src: str, pos: int) -> Optional[str]:
    """Index into `src` the way JavaScript does, yielding `None` when out of bounds."""
    if 0 <= pos < len(src):
        return src[pos]
    return None
