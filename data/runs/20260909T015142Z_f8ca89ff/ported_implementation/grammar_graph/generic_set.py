from __future__ import annotations

from typing import Callable, Dict, Generic, Iterator, Optional, TypeVar

__all__ = ["GenericSet"]

T = TypeVar("T")
K = TypeVar("K")


class GenericSet(Generic[T, K]):
    """A set that dedupes on a derived key while preserving object identity.

    Mirrors the reference implementation, which pairs a `Map<K, T>` with a
    `Set<T>`; membership on the latter is by reference, which is reproduced here
    with an identity-keyed dict.
    """

    def __init__(self, get_key: Callable[[T], K]):
        self.get_key = get_key
        self._keys: Dict[K, T] = {}
        self._set: Dict[int, T] = {}

    def add(self, el: T) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            self._keys[key] = el
            self._set[id(el)] = el

    def delete(self, el: T) -> None:
        key = self.get_key(el)
        ref = self._keys.get(key)
        if ref is None:
            raise Exception("Could not get ref")
        del self._keys[key]
        self._set.pop(id(ref), None)

    def has(self, el: T) -> bool:
        return id(el) in self._set

    def get(self, el: T) -> Optional[T]:
        return self._keys.get(self.get_key(el))

    def __iter__(self) -> Iterator[T]:
        return iter(list(self._set.values()))

    def __contains__(self, el: object) -> bool:
        return id(el) in self._set

    @property
    def size(self) -> int:
        return len(self._set)

    def __len__(self) -> int:
        return len(self._set)

    def __repr__(self) -> str:
        return f"GenericSet(size={self.size})"
