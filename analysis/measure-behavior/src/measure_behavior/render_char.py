import random

NAMED = {"\t": "\\t", "\n": "\\n", "\r": "\\r"}
ESCAPED_IN_LITERAL = {'"': '\\"', "\\": "\\\\"}
ESCAPED_IN_CLASS = {"]": "\\]", "[": "\\[", "\\": "\\\\", "^": "\\x5E", "-": "\\x2D"}


def render_char(char: str, rng: random.Random, in_class: bool) -> str:
    forced = NAMED | (ESCAPED_IN_CLASS if in_class else ESCAPED_IN_LITERAL)
    if char in forced:
        return forced[char]
    if rng.random() >= 0.2:
        return char
    point = ord(char)
    if point < 0x100:
        return f"\\x{point:02X}"
    if point < 0x10000:
        return f"\\u{point:04X}"
    return f"\\U{point:08X}"
