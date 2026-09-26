"""Port of ``src/grammar-graph/generic-set.ts``.

The original pairs a ``Map`` keyed by a derived key with a ``Set`` keyed by
object identity. Rules and pointers define value equality (and are therefore
unhashable), so identity here is tracked with ``id()``; the dict holds a strong
reference to every member, which keeps those ids stable.
"""

from __future__ import annotations

from typing import Callable, Dict, Generic, Iterator, Optional, TypeVar

T = TypeVar('T')
K = TypeVar('K')


class GenericSet(Generic[T, K]):
    def __init__(self, get_key: Callable[[T], K]) -> None:
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
            raise ValueError('Could not get ref')
        del self._keys[key]
        self._set.pop(id(ref), None)

    def has(self, el: T) -> bool:
        return id(el) in self._set

    def get(self, el: T) -> Optional[T]:
        return self._keys.get(self.get_key(el))

    def __iter__(self) -> Iterator[T]:
        return iter(list(self._set.values()))

    def __len__(self) -> int:
        return len(self._set)

    @property
    def size(self) -> int:
        return len(self._set)
