from typing import Any, Dict, Iterator


class Pointers:
    def __init__(self, *pointers: Any):
        self._pointers: Dict[str, Any] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: Any) -> None:
        self._pointers[pointer.id] = pointer

    def __iter__(self) -> Iterator[Any]:
        # A copy, so that pointers added while iterating do not disturb the walk.
        return iter(list(self._pointers.values()))

    def __len__(self) -> int:
        return len(self._pointers)

    @property
    def size(self) -> int:
        return len(self._pointers)
