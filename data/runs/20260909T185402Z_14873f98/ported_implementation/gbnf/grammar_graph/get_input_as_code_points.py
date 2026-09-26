from .types import ValidInput


def get_input_as_code_points(src: ValidInput) -> list[int]:
    if not isinstance(src, str):
        return list(src) if isinstance(src, list) else [src]

    return [ord(char) for char in src]
