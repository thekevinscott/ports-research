def char_at(src: str, pos: int) -> str | None:
    """Index into `src` the way JavaScript does, yielding `None` out of bounds."""
    if 0 <= pos < len(src):
        return src[pos]
    return None
