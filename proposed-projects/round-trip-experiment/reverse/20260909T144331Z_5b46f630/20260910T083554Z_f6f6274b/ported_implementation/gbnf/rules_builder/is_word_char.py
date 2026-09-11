from typing import Optional


def is_word_char(c: Optional[str]) -> bool:
    return isinstance(c, str) and len(c) == 1 and ("a" <= c <= "z" or "A" <= c <= "Z")
