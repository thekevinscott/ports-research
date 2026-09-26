from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")


class GenericSet(Generic[T, K]):
    """A set of elements deduplicated by a derived key, preserving insertion order."""

    def __init__(self, get_key: Callable[[T], K]):
        self.get_key = get_key
        self._keys: dict[K, T] = {}

    def add(self, el: T) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            self._keys[key] = el

    def delete(self, el: T) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            raise ValueError("Could not get ref")
        del self._keys[key]

    def has(self, el: T) -> bool:
        return any(existing is el for existing in self._keys.values())

    def get(self, el: T) -> T | None:
        return self._keys.get(self.get_key(el))

    def __iter__(self) -> Iterator[T]:
        return iter(list(self._keys.values()))

    @property
    def size(self) -> int:
        return len(self._keys)

    def __len__(self) -> int:
        return len(self._keys)
