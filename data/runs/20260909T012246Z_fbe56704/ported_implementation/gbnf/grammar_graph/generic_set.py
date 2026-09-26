from typing import Callable, Dict, Generic, Iterator, TypeVar

T = TypeVar("T")
K = TypeVar("K")


class GenericSet(Generic[T, K]):
    """A set whose membership is determined by a key derived from each element."""

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
            raise ValueError("Could not get ref")
        del self._keys[key]

    def has(self, el: T) -> bool:
        return self.get_key(el) in self._keys

    def get(self, el: T) -> T:
        return self._keys.get(self.get_key(el))

    def __contains__(self, el: T) -> bool:
        return self.has(el)

    def __iter__(self) -> Iterator[T]:
        return iter(list(self._keys.values()))

    def __len__(self) -> int:
        return len(self._keys)

    @property
    def size(self) -> int:
        return len(self._keys)
