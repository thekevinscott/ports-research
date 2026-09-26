from typing import Iterator

from .graph_pointer import GraphPointer


class Pointers:
    def __init__(self, *pointers: GraphPointer):
        self._pointers: dict[str, GraphPointer] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: GraphPointer) -> None:
        self._pointers[pointer.id] = pointer

    def __iter__(self) -> Iterator[GraphPointer]:
        yield from list(self._pointers.values())

    @property
    def size(self) -> int:
        return len(self._pointers)

    def __len__(self) -> int:
        return len(self._pointers)
