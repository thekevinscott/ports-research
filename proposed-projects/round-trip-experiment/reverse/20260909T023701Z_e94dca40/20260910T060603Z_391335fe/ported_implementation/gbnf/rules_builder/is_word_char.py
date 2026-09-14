from __future__ import annotations

import re

WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c: str) -> bool:
    return bool(WORD_CHAR.search(c))
