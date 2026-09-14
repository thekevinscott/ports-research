import re

WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(char: str) -> bool:
    return bool(WORD_CHAR.search(char))
