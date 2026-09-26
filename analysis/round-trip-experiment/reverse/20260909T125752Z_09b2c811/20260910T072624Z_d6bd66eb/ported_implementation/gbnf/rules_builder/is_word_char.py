"""Characters that may appear in a rule name."""

import re

WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c: str) -> bool:
    return bool(c) and bool(WORD_CHAR.search(c))
