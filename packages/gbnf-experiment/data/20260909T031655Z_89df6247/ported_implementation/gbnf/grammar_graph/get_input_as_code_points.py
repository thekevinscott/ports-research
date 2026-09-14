def get_input_as_code_points(src) -> list[int]:
    if not isinstance(src, str):
        return list(src) if isinstance(src, (list, tuple)) else [src]

    return [ord(char) for char in src]
