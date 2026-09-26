from typing import List


def validate_non_empty(value: List[int]) -> List[int]:
    if len(value) == 0:
        raise Exception("Value cannot be empty.")
    return value
