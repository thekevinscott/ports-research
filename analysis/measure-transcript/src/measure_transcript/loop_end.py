# The characters split_command's lexer returns as separator and redirect tokens.
PUNCTUATION = ";&|()<>\n"


def loop_end(tokens: list[str], i: int) -> tuple[int, int] | None:
    """For a loop header ended by the separator token at `i`, the span of its body between `do` and its own `done`; None without them."""
    def separator(token):
        return bool(token) and set(token) <= set(PUNCTUATION)

    do = i
    while do < len(tokens) and separator(tokens[do]):
        do += 1
    if do == len(tokens) or tokens[do] != "do":
        return None
    depth = 1
    for k in range(do + 1, len(tokens)):
        if separator(tokens[k - 1]) and tokens[k] in ("do", "done"):
            depth += 1 if tokens[k] == "do" else -1
            if not depth:
                return do + 1, k
    return None
