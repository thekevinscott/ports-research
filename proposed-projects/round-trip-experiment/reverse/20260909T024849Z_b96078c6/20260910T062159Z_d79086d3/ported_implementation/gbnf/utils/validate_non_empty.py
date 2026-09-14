from __future__ import annotations

from typing import List, TypeVar

T = TypeVar("T")


def validate_non_empty(value: List[T]) -> List[T]:
    if not value:
        raise ValueError("Value cannot be empty.")
    return value
