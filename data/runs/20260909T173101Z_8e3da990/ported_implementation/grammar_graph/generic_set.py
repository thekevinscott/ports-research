from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Generic, TypeVar

T = TypeVar('T')
K = TypeVar('K')


class GenericSet(Generic[T, K]):
    """A set keyed by a derived key, but holding (and comparing) elements by identity.

    The reference implementation pairs a `Map<K, T>` with a `Set<T>`; JS sets
    compare objects by reference, so the membership half is keyed on `id()`
    here rather than on `__hash__`/`__eq__`.
    """

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
            raise RuntimeError('Could not get ref')
        del self._keys[key]
        self._set.pop(id(ref), None)

    def has(self, el: T) -> bool:
        return id(el) in self._set

    def get(self, el: T) -> T | None:
        return self._keys.get(self.get_key(el))

    def __iter__(self) -> Iterator[T]:
        yield from list(self._set.values())

    def __len__(self) -> int:
        return len(self._set)

    @property
    def size(self) -> int:
        return len(self._set)
