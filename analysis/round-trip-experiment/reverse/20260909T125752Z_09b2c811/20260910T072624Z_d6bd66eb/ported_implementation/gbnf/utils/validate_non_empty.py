"""Guard against empty collections."""

from typing import List, TypeVar

T = TypeVar("T")


def validate_non_empty(value: List[T]) -> List[T]:
    if not len(value):
        raise ValueError("Value cannot be empty.")
    return value
