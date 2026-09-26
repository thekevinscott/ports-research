from __future__ import annotations

from typing import Iterator


class Pointers:
    def __init__(self, *pointers) -> None:
        self._pointers: dict[str, object] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer) -> None:
        self._pointers[pointer.id] = pointer

    def __iter__(self) -> Iterator:
        return iter(list(self._pointers.values()))

    @property
    def size(self) -> int:
        return len(self._pointers)

    def __len__(self) -> int:
        return len(self._pointers)
