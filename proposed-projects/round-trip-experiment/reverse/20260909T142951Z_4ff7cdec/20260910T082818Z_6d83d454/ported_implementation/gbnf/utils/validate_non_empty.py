from typing import List, TypeVar

T = TypeVar("T")


def validate_non_empty(value: List[T]) -> List[T]:
    if len(value) == 0:
        raise ValueError("Value cannot be empty.")
    return value
