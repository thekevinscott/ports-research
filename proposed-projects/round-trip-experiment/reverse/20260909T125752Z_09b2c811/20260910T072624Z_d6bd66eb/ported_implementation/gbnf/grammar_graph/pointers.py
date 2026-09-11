"""An id keyed collection of graph pointers."""

from typing import Generator

from .graph_pointer import GraphPointer


class Pointers:
    def __init__(self, *pointers: GraphPointer):
        self.pointers = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: GraphPointer) -> None:
        self.pointers[pointer.id] = pointer

    def __iter__(self) -> Generator[GraphPointer, None, None]:
        yield from list(self.pointers.values())

    @property
    def size(self) -> int:
        return len(self.pointers)

    def __len__(self) -> int:
        return len(self.pointers)
