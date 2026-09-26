def validate_non_empty(value: list) -> list:
    if not len(value):
        raise ValueError("Value cannot be empty.")
    return value
