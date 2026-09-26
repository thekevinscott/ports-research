import re

_WORD_CHAR = re.compile(r"[a-zA-Z]")


def is_word_char(c) -> bool:
    # JS coerces a missing character to the string "undefined" before testing it.
    return bool(_WORD_CHAR.search(c if c is not None else "undefined"))
