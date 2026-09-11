from typing import Dict, Iterator

from .graph_pointer import GraphPointer


class Pointers:
    def __init__(self, *pointers: GraphPointer) -> None:
        self._pointers: Dict[str, GraphPointer] = {}
        for pointer in pointers:
            self.add(pointer)

    def __repr__(self) -> str:
        return f"<Pointers {', '.join(str(p.node.rule) for p in self)}>"

    def add(self, pointer: GraphPointer) -> None:
        self._pointers[pointer.id] = pointer

    def __iter__(self) -> Iterator[GraphPointer]:
        return iter(list(self._pointers.values()))

    def __len__(self) -> int:
        return len(self._pointers)

    @property
    def size(self) -> int:
        return len(self._pointers)
