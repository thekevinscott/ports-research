from .grammar_graph_types import ValidInput


def get_code_point(char: str) -> int:
    if not char:
        raise ValueError(f"Could not get code point for character: {char}")
    return ord(char[0])


def get_input_as_code_points(src: ValidInput) -> list[int]:
    if isinstance(src, bool):
        raise TypeError(f"Invalid input type: {type(src)}")

    if isinstance(src, int):
        return [src]

    if isinstance(src, list):
        for c in src:
            if not isinstance(c, int) or isinstance(c, bool):
                raise TypeError(
                    f"code_point must be an integer for {c} if src is a list"
                )
        return src

    if isinstance(src, str):
        return [get_code_point(char) for char in src]

    raise TypeError(f"Invalid input type: {type(src)}")
