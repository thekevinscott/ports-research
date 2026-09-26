def char_at(src: str, pos: int) -> str:
    """Read a single character, returning '' when the position is out of bounds.

    Indexing past the end of a string is an error in Python, where the reference
    implementation relies on it yielding `undefined` and failing the comparison it
    is part of.
    """
    if pos < 0 or pos >= len(src):
        return ""
    return src[pos]
