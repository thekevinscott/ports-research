def is_word_char(c: str) -> bool:
    return len(c) > 0 and ("a" <= c <= "z" or "A" <= c <= "Z")
