import re
from typing import Optional

WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c: Optional[str]) -> bool:
    return c is not None and WORD_CHAR.search(c) is not None
