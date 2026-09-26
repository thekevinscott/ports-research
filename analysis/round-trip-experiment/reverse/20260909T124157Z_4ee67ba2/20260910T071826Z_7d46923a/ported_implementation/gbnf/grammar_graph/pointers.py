from typing import Dict, Iterator

from .graph_pointer import GraphPointer


class Pointers:
    def __init__(self, *pointers: GraphPointer):
        self.__pointers: Dict[str, GraphPointer] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: GraphPointer) -> None:
        self.__pointers[pointer.id] = pointer

    def __iter__(self) -> Iterator[GraphPointer]:
        return iter(list(self.__pointers.values()))

    def __len__(self) -> int:
        return len(self.__pointers)

    def __str__(self) -> str:
        return f"<Pointers {', '.join(str(p.node.rule) for p in self)}>"

    def __repr__(self) -> str:
        return str(self)
