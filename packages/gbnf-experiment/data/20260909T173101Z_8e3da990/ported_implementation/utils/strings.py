def char_at(src: str, pos: int) -> str:
    """JS-style string indexing: reads outside the string yield ``''``.

    The reference implementation relies on ``src[pos]`` returning ``undefined``
    past the end of the grammar (and on negative indices being out of bounds),
    then compares the result against single characters. An empty string is
    falsy and never equal to a real character, so it stands in for
    ``undefined`` here.
    """
    if 0 <= pos < len(src):
        return src[pos]
    return ''


charAt = char_at
