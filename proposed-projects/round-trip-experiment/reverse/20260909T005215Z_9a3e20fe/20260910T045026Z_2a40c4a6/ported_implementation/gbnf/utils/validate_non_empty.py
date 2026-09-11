from typing import TypeVar

T = TypeVar("T")


def validate_non_empty(value: list[T]) -> list[T]:
    if len(value) == 0:
        raise ValueError("Value cannot be empty.")
    return value
