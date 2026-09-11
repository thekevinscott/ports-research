from typing import Generator

from .graph_pointer import GraphPointer


class Pointers:
    def __init__(self, *pointers: GraphPointer):
        self.__pointers__ = {}
        for pointer in pointers:
            self.add(pointer)

    def __repr__(self) -> str:
        return f"<Pointers {', '.join(str(p.node.rule) for p in self)}>"

    def add(self, pointer: GraphPointer) -> None:
        self.__pointers__[pointer.id] = pointer

    def __iter__(self) -> Generator[GraphPointer, None, None]:
        yield from list(self.__pointers__.values())

    def __len__(self) -> int:
        return len(self.__pointers__)
