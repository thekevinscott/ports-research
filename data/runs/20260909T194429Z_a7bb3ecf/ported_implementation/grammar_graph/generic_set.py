from __future__ import annotations

from typing import Callable, Dict, Generic, Iterator, Optional, TypeVar

T = TypeVar('T')
K = TypeVar('K')


class GenericSet(Generic[T, K]):
    """A set of elements deduplicated by a derived key.

    The reference keeps a `Map` of keys plus a `Set` of the elements; the `Set`
    uses reference identity, which is reproduced here by keying on `id()`.
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
            raise Exception('Could not get ref')
        del self._keys[key]
        self._set.pop(id(ref), None)

    def has(self, el: T) -> bool:
        return id(el) in self._set

    def get(self, el: T) -> Optional[T]:
        return self._keys.get(self.get_key(el))

    def __iter__(self) -> Iterator[T]:
        yield from list(self._set.values())

    @property
    def size(self) -> int:
        return len(self._set)

    def __len__(self) -> int:
        return len(self._set)
