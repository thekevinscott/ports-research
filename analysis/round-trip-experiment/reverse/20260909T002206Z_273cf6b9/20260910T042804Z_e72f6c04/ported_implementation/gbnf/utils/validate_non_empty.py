from typing import List


def validate_non_empty(value: List[int]) -> List[int]:
    if not value:
        raise ValueError("Value cannot be empty.")
    return value
