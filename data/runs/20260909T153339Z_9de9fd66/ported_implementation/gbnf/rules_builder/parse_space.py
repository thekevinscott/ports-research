def _at(src: str, pos: int) -> str:
    """Read a character, mirroring JS's out-of-bounds `undefined` as an empty string."""
    return src[pos] if 0 <= pos < len(src) else ""


def parse_space(src: str, pos: int, newline_ok: bool) -> int:
    while _at(src, pos) in (" ", "\t", "#") or (
        newline_ok and _at(src, pos) in ("\r", "\n")
    ):
        if _at(src, pos) == "#":
            while _at(src, pos) and _at(src, pos) not in ("\r", "\n"):
                pos += 1
        else:
            pos += 1
    return pos
