"""Port of ``src/rules-builder/parse-char.ts``."""

from __future__ import annotations

from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError


def _at(src: str, pos: int) -> str:
    return src[pos] if 0 <= pos < len(src) else ""


def _parse_hex(src: str, pos: int, start: int, end: int) -> int:
    """JS uses `parseInt(slice, 16)`, which yields NaN for non-hex input.

    A NaN code point can never match anything and would silently poison the
    grammar, so an explicit error is raised here instead.
    """
    raw = src[start:end]
    try:
        return int(raw, 16)
    except ValueError:
        raise GrammarParseError(src, pos, f'Invalid hex escape "{raw}"') from None


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if _at(src, pos) == "\\":
        nxt = _at(src, pos + 1)
        if nxt == "x":
            return (_parse_hex(src, pos, pos + 2, pos + 4), 4)
        if nxt == "u":
            return (_parse_hex(src, pos, pos + 2, pos + 6), 6)
        if nxt == "U":
            return (_parse_hex(src, pos, pos + 2, pos + 10), 10)
        if nxt == "t":
            return (ord("\t"), 2)
        if nxt == "r":
            return (ord("\r"), 2)
        if nxt == "n":
            return (ord("\n"), 2)
        if nxt in ('"', "[", "]"):
            return (ord(src[pos + 1]), 2)
        if nxt == "\\":
            return (ord(src[pos + 1]), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {_at(src, pos)}")

    if not _at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return (ord(src[pos]), 1)
