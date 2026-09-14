from __future__ import annotations

from typing import Callable, Dict, Generic, Iterator, Optional, TypeVar

T = TypeVar('T')
K = TypeVar('K')


class GenericSet(Generic[T, K]):
    """An insertion-ordered set keyed by a derived key rather than by identity."""

    def __init__(self, get_key: Callable[[T], K]):
        self.get_key = get_key
        self._keys: Dict[K, T] = {}
        self._set: Dict[T, None] = {}

    def add(self, el: T) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            self._keys[key] = el
            self._set[el] = None

    def delete(self, el: T) -> None:
        key = self.get_key(el)
        ref = self._keys.get(key)
        if ref is None:
            raise ValueError('Could not get ref')
        del self._keys[key]
        self._set.pop(ref, None)

    def has(self, el: T) -> bool:
        return el in self._set

    def get(self, el: T) -> Optional[T]:
        return self._keys.get(self.get_key(el))

    def __iter__(self) -> Iterator[T]:
        return iter(list(self._set.keys()))

    @property
    def size(self) -> int:
        return len(self._set)

    def __len__(self) -> int:
        return len(self._set)
