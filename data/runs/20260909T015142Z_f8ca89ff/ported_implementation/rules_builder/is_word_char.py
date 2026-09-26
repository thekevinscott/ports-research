from __future__ import annotations

import re

__all__ = ["is_word_char", "isWordChar"]

_WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c: str) -> bool:
    return bool(c) and _WORD_CHAR.search(c) is not None


isWordChar = is_word_char
