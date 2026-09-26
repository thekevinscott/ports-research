def char_at(src: str, pos: int) -> str:
    """Index a string the way JavaScript does.

    Out of range indices (including negative ones) return the empty string rather
    than raising, mirroring `undefined` in the reference implementation. The empty
    string is falsy in Python, so `if char_at(src, pos):` reads the same as
    `if (src[pos])`.
    """
    if 0 <= pos < len(src):
        return src[pos]
    return ""
