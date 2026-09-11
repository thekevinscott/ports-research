def char_at(src: str, pos: int) -> str:
    """Indexing a JS string out of bounds yields undefined; here it yields ''."""
    if 0 <= pos < len(src):
        return src[pos]
    return ""
