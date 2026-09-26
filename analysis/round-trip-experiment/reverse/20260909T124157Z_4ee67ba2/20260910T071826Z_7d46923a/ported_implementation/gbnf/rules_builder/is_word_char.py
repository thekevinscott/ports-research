from typing import Optional


def is_word_char(c: Optional[str]) -> bool:
    return bool(c) and ("a" <= c <= "z" or "A" <= c <= "Z")
