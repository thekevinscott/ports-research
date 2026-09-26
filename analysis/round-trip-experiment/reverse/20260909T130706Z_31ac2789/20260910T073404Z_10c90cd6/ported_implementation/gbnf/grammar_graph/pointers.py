from typing import Dict, Generator

from .graph_pointer import GraphPointer


class Pointers:
    def __init__(self, *pointers: GraphPointer):
        self.__pointers__: Dict[str, GraphPointer] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: GraphPointer) -> None:
        self.__pointers__[pointer.id] = pointer

    def __iter__(self) -> Generator[GraphPointer, None, None]:
        yield from list(self.__pointers__.values())

    @property
    def size(self) -> int:
        return len(self.__pointers__)

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"Pointers({list(self.__pointers__.values())!r})"
