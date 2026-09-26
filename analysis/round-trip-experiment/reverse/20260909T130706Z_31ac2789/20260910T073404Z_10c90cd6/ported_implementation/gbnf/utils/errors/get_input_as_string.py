from .errors_types import ValidInput


def get_input_as_string(src: ValidInput) -> str:
    if isinstance(src, str):
        return src
    if isinstance(src, int) and not isinstance(src, bool):
        return chr(src)
    return "".join(chr(code_point) for code_point in src)


getInputAsString = get_input_as_string
