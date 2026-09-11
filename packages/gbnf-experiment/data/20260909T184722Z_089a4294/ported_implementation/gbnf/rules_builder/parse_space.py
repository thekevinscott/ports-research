from __future__ import annotations


def char_at(src: str, pos: int) -> str:
    """Mirrors JavaScript's out-of-bounds string indexing, which yields a falsy value."""
    return src[pos] if 0 <= pos < len(src) else ""


def parse_space(src: str, pos: int, newline_ok: bool) -> int:
    while char_at(src, pos) in (" ", "\t", "#") or (
        newline_ok and char_at(src, pos) in ("\r", "\n")
    ):
        if char_at(src, pos) == "#":
            while char_at(src, pos) and char_at(src, pos) not in ("\r", "\n"):
                pos += 1
        else:
            pos += 1
    return pos
