import re
from typing import Optional

WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c: Optional[str]) -> bool:
    if c is None:
        return False
    return WORD_CHAR.search(c) is not None
