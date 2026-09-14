from typing import Dict, Generator

from .graph_pointer import GraphPointer

GraphPointerKey = str


class Pointers:
    def __init__(self, *pointers: GraphPointer):
        self._pointers: Dict[GraphPointerKey, GraphPointer] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: GraphPointer) -> None:
        self._pointers[pointer.id] = pointer

    def __iter__(self) -> Generator[GraphPointer, None, None]:
        yield from list(self._pointers.values())

    @property
    def size(self) -> int:
        return len(self._pointers)

    def __len__(self) -> int:
        return len(self._pointers)

    def __repr__(self) -> str:
        return f"<Pointers {', '.join(str(p.node.rule) for p in self)}>"
