from .errors_types import ValidInput


def get_input_as_string(src: ValidInput) -> str:
    if isinstance(src, str):
        return src
    if isinstance(src, int):
        return chr(src)
    return "".join(chr(code_point) for code_point in src)


# Lengths and positions are counted in code points, matching how the parser
# walks its input.
def get_length_in_code_points(src: str) -> int:
    return len(src)
