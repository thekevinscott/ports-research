from __future__ import annotations

from ..utils.js_compat import char_at

__all__ = ["parse_space", "parseSpace"]


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


parseSpace = parse_space
