import re


def locate_name_offset(text: str, lineno: int, name: str) -> int:
    """The character offset of the first whole-word match of `name` on line `lineno` (1-indexed).

    rope's `Rename` refactoring is offset-driven rather than name-driven, so this is
    the bridge between an `ast`-discovered definition site and a rope rename call.
    """
    lines = text.splitlines(keepends=True)
    line = lines[lineno - 1]
    match = re.search(rf"\b{re.escape(name)}\b", line)
    if match is None:
        raise ValueError(f"{name!r} not found on line {lineno}")
    return sum(len(prior) for prior in lines[: lineno - 1]) + match.start()
