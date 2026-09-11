from typing import TypeVar

T = TypeVar("T")


def validate_non_empty(value: list[T]) -> list[T]:
    if not len(value):
        raise ValueError("Value cannot be empty.")
    return value
