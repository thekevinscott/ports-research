"""Small helpers that reproduce JavaScript semantics the reference relies on."""


def char_at(src: str, pos: int) -> str:
    """`src[pos]` in JS: out of range yields `undefined`, which is falsy.

    Python raises on out-of-range indexing and wraps negative indices, so this
    returns the empty string (also falsy) for any position outside the string.
    """
    if pos < 0 or pos >= len(src):
        return ''
    return src[pos]


HEX_DIGITS = '0123456789abcdefABCDEF'


def js_parse_int_hex(src: str) -> float:
    """`parseInt(src, 16)`: parse the longest leading hex run, else NaN."""
    src = src.lstrip()
    negative = False
    if src[:1] in ('+', '-'):
        negative = src[0] == '-'
        src = src[1:]
    if src[:2].lower() == '0x':
        src = src[2:]
    idx = 0
    while idx < len(src) and src[idx] in HEX_DIGITS:
        idx += 1
    if idx == 0:
        return float('nan')
    value = int(src[:idx], 16)
    return -value if negative else value
