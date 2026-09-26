from __future__ import annotations

import re

WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c: object) -> bool:
    return isinstance(c, str) and WORD_CHAR.search(c) is not None
