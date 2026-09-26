from __future__ import annotations

from typing import Callable, Generic, Iterator, TypeVar

from ..utils.errors.gbnf_error import GBNFError

T = TypeVar("T")
K = TypeVar("K")


class GenericSet(Generic[T, K]):
    """A set whose membership is decided by a derived key, preserving insertion order."""

    def __init__(self, get_key: Callable[[T], K]):
        self.get_key = get_key
        self._keys: dict[K, T] = {}
        self._set: dict[int, T] = {}

    def add(self, el: T) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            self._keys[key] = el
            self._set[id(el)] = el

    def delete(self, el: T) -> None:
        key = self.get_key(el)
        ref = self._keys.get(key)
        if ref is None:
            raise GBNFError("Could not get ref")
        del self._keys[key]
        self._set.pop(id(ref), None)

    def has(self, el: T) -> bool:
        return id(el) in self._set

    def get(self, el: T):
        return self._keys.get(self.get_key(el))

    def __iter__(self) -> Iterator[T]:
        yield from list(self._set.values())

    @property
    def size(self) -> int:
        return len(self._set)

    def __len__(self) -> int:
        return len(self._set)
