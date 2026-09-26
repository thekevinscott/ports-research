from typing import List, Union

ValidInput = Union[str, int, List[int]]


def get_input_as_string(src: ValidInput) -> str:
    if isinstance(src, str):
        return src
    code_points = src if isinstance(src, list) else [src]
    return ''.join(chr(cp) for cp in code_points)
