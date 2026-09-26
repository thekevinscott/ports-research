from typing import Callable, Dict, Generic, Iterator, Optional, TypeVar

T = TypeVar('T')
K = TypeVar('K')


class GenericSet(Generic[T, K]):
    """An insertion-ordered set keyed by a derived key.

    Adding an element whose key is already present is a no-op, so the first
    element seen for a key is the one the set keeps.
    """

    def __init__(self, get_key: Callable[[T], K]):
        self.get_key = get_key
        self._keys: Dict[K, T] = {}

    def add(self, el: T) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            self._keys[key] = el

    def delete(self, el: T) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            raise Exception('Could not get ref')
        del self._keys[key]

    def has(self, el: T) -> bool:
        key = self.get_key(el)
        return key in self._keys and self._keys[key] is el

    def get(self, el: T) -> Optional[T]:
        return self._keys.get(self.get_key(el))

    def __iter__(self) -> Iterator[T]:
        yield from list(self._keys.values())

    @property
    def size(self) -> int:
        return len(self._keys)
