from typing import TYPE_CHECKING, Dict, Iterator

if TYPE_CHECKING:
    from .graph_pointer import GraphPointer

GraphPointerKey = str


class Pointers:
    def __init__(self, *pointers: "GraphPointer"):
        self.__pointers: Dict[GraphPointerKey, "GraphPointer"] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: "GraphPointer") -> None:
        self.__pointers[pointer.id] = pointer

    def __iter__(self) -> Iterator["GraphPointer"]:
        yield from list(self.__pointers.values())

    def __len__(self) -> int:
        return len(self.__pointers)

    @property
    def size(self) -> int:
        return len(self.__pointers)
