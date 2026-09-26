from __future__ import annotations

from typing import Dict, Iterator, ValuesView

from .graph_pointer import GraphPointer


class Pointers:
    def __init__(self, *pointers: GraphPointer) -> None:
        self._pointers: Dict[str, GraphPointer] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: GraphPointer) -> None:
        self._pointers[pointer.id] = pointer

    def values(self) -> ValuesView[GraphPointer]:
        return self._pointers.values()

    def __iter__(self) -> Iterator[GraphPointer]:
        return iter(self._pointers.values())

    def __len__(self) -> int:
        return len(self._pointers)

    @property
    def size(self) -> int:
        return len(self._pointers)

    def __repr__(self) -> str:
        return f"<Pointers {', '.join(str(p.node.rule) for p in self)}>"
