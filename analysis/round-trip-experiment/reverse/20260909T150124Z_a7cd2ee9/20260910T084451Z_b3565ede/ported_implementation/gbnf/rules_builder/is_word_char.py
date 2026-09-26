def is_word_char(c: str | None) -> bool:
    if not c:
        return False
    return ("a" <= c <= "z") or ("A" <= c <= "Z")
