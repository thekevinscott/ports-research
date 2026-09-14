"""Small helpers that emulate the JavaScript semantics the port relies on.

The reference implementation indexes strings freely, relying on JS returning
``undefined`` for out-of-range indices (which is falsy, and compares unequal to
every character). ``char_at`` gives us the same behaviour with the empty string.
"""


def char_at(src: str, pos: int) -> str:
    """``src[pos]`` in JS: the empty string stands in for ``undefined``."""
    if pos < 0 or pos >= len(src):
        return ''
    return src[pos]


def slice_(src: str, start: int, end: int) -> str:
    """``src.slice(start, end)``: out-of-range indices are clamped, not errors."""
    return src[max(start, 0):max(end, 0)]
