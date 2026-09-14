import re

WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c: str) -> bool:
    return bool(c) and WORD_CHAR.search(c) is not None
