from typing import Dict, Iterator


class Pointers:
    """An insertion-ordered collection of pointers, keyed by pointer id.

    A pointer's id is the sum of its node's id and its parent's id chain, so two
    pointers sharing an id point at the same node through an identical parent
    chain and are interchangeable when walking the graph.
    """

    def __init__(self, *pointers):
        self._pointers: Dict[str, object] = {}
        for pointer in pointers:
            self.add(pointer)

    def add(self, pointer) -> None:
        self._pointers[pointer.id] = pointer

    def __iter__(self) -> Iterator:
        yield from list(self._pointers.values())

    @property
    def size(self) -> int:
        return len(self._pointers)
