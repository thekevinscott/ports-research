def get_input_as_string(src) -> str:
    """`src` is a string, a code point, or a list of code points."""
    if isinstance(src, str):
        return src
    code_points = src if isinstance(src, (list, tuple)) else [src]
    return "".join(chr(cp) for cp in code_points)
