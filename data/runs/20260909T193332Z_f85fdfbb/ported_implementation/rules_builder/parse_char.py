from __future__ import annotations

import re

from ..utils.errors.grammar_parse_error import GrammarParseError

_HEX_PREFIX = re.compile(r"^[ \t\n\r\f\v]*([+-]?)((?:0[xX])?[0-9a-fA-F]*)")


def _parse_int_16(src: str) -> float:
    """``parseInt(src, 16)`` semantics: parse the leading hex digits, NaN if none."""
    match = _HEX_PREFIX.match(src)
    if match is None:  # pragma: no cover - the pattern always matches
        return float("nan")
    sign, digits = match.group(1), match.group(2)
    if digits[:2] in ("0x", "0X"):
        digits = digits[2:]
    if not digits:
        return float("nan")
    value = int(digits, 16)
    return -value if sign == "-" else value


def parse_char(src: str, pos: int) -> tuple[int, int]:
    """Parse one (possibly escaped) character, returning its code and its width."""

    def at(i: int) -> str:
        return src[i] if 0 <= i < len(src) else ""

    if at(pos) == "\\":
        escape = at(pos + 1)
        if escape == "x":
            return (_parse_int_16(src[pos + 2:pos + 4]), 4)
        if escape == "u":
            return (_parse_int_16(src[pos + 2:pos + 6]), 6)
        if escape == "U":
            return (_parse_int_16(src[pos + 2:pos + 10]), 10)
        if escape == "t":
            return (ord("\t"), 2)
        if escape == "r":
            return (ord("\r"), 2)
        if escape == "n":
            return (ord("\n"), 2)
        if escape in ('"', "[", "]"):
            return (ord(src[pos + 1]), 2)
        if escape == "\\":
            code_point = at(pos + 1)
            if not code_point:
                raise GrammarParseError(
                    src, pos, "Could not get code point for character"
                )
            return (ord(code_point), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {at(pos)}")

    if not at(pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return (ord(src[pos]), 1)
