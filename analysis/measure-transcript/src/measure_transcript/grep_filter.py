# Characters that make a grep pattern more than a fixed string.
REGEX = set(".[]*^$\\+?{}|()")


def grep_filter(words: list[str]):
    """A `grep [-v] [-e] PATTERN...` stage over lines as a test of one line; None for any other stage."""
    if words[:1] != ["grep"]:
        return None
    invert, patterns, operands, args = False, [], [], iter(words[1:])
    for word in args:
        if word == "-v":
            invert = True
        elif word == "-e":
            patterns.append(next(args, ""))
        elif word.startswith("-"):
            return None
        else:
            operands.append(word)
    # Without -e the one operand is the pattern; any other operand is a file, and grep then reads no lines from the pipe.
    if len(operands) > (0 if patterns else 1):
        return None
    patterns += operands
    if not patterns or any(not p or REGEX & set(p) for p in patterns):
        return None
    return lambda line: invert != any(p in line for p in patterns)
