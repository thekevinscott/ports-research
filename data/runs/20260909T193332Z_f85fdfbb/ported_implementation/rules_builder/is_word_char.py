from __future__ import annotations

import re

_WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c: str) -> bool:
    return c is not None and bool(_WORD_CHAR.search(c))
