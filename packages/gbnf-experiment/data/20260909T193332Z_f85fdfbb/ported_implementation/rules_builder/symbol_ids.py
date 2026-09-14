from __future__ import annotations

from typing import Iterator


class SymbolIdsError(KeyError):
    """Raised when a name or id is missing from a :class:`SymbolIds`."""

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else ""


class SymbolIds:
    """A bidirectional name <-> id map that also remembers where each name was seen."""

    # we don't need to delete, just preserve relationships
    def __init__(self) -> None:
        self._map: dict[str, int] = {}
        self._pos: dict[str, int] = {}
        self._reverse_map: dict[int, str] = {}

    @property
    def size(self) -> int:
        return len(self._map)

    def keys(self) -> list[str]:
        return list(self._map.keys())

    def has(self, key: str) -> bool:
        return key in self._map

    def get(self, key: str) -> int:
        if key not in self._map:
            raise SymbolIdsError(f"SymbolIds does not contain key: {key}")
        return self._map[key]

    def reverse_get(self, key: int) -> str:
        if key not in self._reverse_map:
            raise SymbolIdsError(f"SymbolIds does not contain value: {key}")
        return self._reverse_map[key]

    def get_pos(self, key: str) -> int:
        if key not in self._pos:
            raise SymbolIdsError(f"SymbolIds does not contain key: {key}")
        return self._pos[key]

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._pos[key] = pos
        self._reverse_map[value] = key

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[tuple[str, int]]:
        yield from self._map.items()

    # camelCase aliases, mirroring the reference API.
    reverseGet = reverse_get
    getPos = get_pos
