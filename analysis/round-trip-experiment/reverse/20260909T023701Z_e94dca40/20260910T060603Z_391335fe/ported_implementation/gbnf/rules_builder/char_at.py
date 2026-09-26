from __future__ import annotations

# JavaScript returns `undefined` when indexing past the end of a string, and comparisons
# against `undefined` are simply false. An empty string gives us the same behavior for
# every comparison the parser makes.


def char_at(src: str, pos: int) -> str:
    if pos < 0 or pos >= len(src):
        return ""
    return src[pos]
