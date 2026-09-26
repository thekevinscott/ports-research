def parse_space(src: str, pos: int, newline_ok: bool) -> int:
    def at(i: int):
        return src[i] if 0 <= i < len(src) else None

    while at(pos) in (" ", "\t", "#") or (
        newline_ok and at(pos) in ("\r", "\n")
    ):
        if at(pos) == "#":
            while at(pos) is not None and at(pos) != "\r" and at(pos) != "\n":
                pos += 1
        else:
            pos += 1
    return pos
