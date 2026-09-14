import re

from ..utils.errors.grammar_parse_error import GrammarParseError

PARSE_NAME_ERROR = "Failed to find a valid name"


def GET_INVALID_CHAR_ERROR(char: str) -> str:
    return (
        f'Invalid character "{char}" when parsing name, '
        "only lowercase letters and hyphens are allowed."
    )


_WORD_CHAR = re.compile(r"[a-zA-Z]")
_VALID_NAME_CHAR = re.compile(r"[a-zA-Z-]")
_INVALID_NEXT_CHAR = re.compile(r"[_0-9]")


def char_at(src: str, pos: int) -> str:
    """Reading out of bounds yields `undefined` in JS; here, the empty string."""
    if 0 <= pos < len(src):
        return src[pos]
    return ""


def is_word_char(c: str) -> bool:
    return bool(c) and bool(_WORD_CHAR.match(c))


def parse_name(grammar: str, pos: int) -> str:
    name = ""
    while pos < len(grammar) and _VALID_NAME_CHAR.match(grammar[pos]):
        name += grammar[pos]
        pos += 1
    if not name:
        raise GrammarParseError(grammar, pos, PARSE_NAME_ERROR)
    if pos < len(grammar) and _INVALID_NEXT_CHAR.match(grammar[pos]):
        raise GrammarParseError(grammar, pos, GET_INVALID_CHAR_ERROR(grammar[pos]))
    return name


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


def parse_char(src: str, pos: int) -> tuple[int, int]:
    if char_at(src, pos) == "\\":
        escaped = char_at(src, pos + 1)
        if escaped == "x":
            return (int(src[pos + 2 : pos + 4], 16), 4)
        if escaped == "u":
            return (int(src[pos + 2 : pos + 6], 16), 6)
        if escaped == "U":
            return (int(src[pos + 2 : pos + 10], 16), 10)
        if escaped == "t":
            return (ord("\t"), 2)
        if escaped == "r":
            return (ord("\r"), 2)
        if escaped == "n":
            return (ord("\n"), 2)
        if escaped in ('"', "[", "]"):
            return (ord(src[pos + 1]), 2)
        if escaped == "\\":
            return (ord(src[pos + 1]), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return (ord(src[pos]), 1)
