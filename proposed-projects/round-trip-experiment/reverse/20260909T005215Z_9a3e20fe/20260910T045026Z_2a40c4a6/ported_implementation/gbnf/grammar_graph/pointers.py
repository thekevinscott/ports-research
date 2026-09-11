from typing import Iterator

from .graph_pointer import GraphPointer


class Pointers:
    """An insertion-ordered, id-deduplicated collection of pointers.

    Two pointers that share an id address the same node through the same parent
    chain, so only one of them needs to be walked.
    """

    def __init__(self, *pointers: GraphPointer):
        self._pointers: dict[str, GraphPointer] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer: GraphPointer) -> None:
        self._pointers[pointer.id] = pointer

    def __iter__(self) -> Iterator[GraphPointer]:
        return iter(list(self._pointers.values()))

    def __len__(self) -> int:
        return len(self._pointers)
