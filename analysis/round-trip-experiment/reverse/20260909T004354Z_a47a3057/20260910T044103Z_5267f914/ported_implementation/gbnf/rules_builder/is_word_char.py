import re

WORD_CHAR_PATTERN = re.compile(r"[a-zA-Z]")


def is_word_char(c: str) -> bool:
    return bool(WORD_CHAR_PATTERN.search(c))
