from __future__ import annotations

from typing import Dict, Iterator, List, Tuple

__all__ = ["SymbolIds", "SymbolIdsKeyError"]


class SymbolIdsKeyError(KeyError):
    """Raised for a missing symbol.

    Subclasses `KeyError` so it can be caught as one, but renders its message
    without `KeyError`'s surrounding quotes.
    """

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else ""


class SymbolIds:
    # we don't need to delete, just preserve relationships
    def __init__(self) -> None:
        self._map: Dict[str, int] = {}
        self._pos: Dict[str, int] = {}
        self._reverse_map: Dict[int, str] = {}

    @property
    def size(self) -> int:
        return len(self._map)

    def __len__(self) -> int:
        return len(self._map)

    def keys(self) -> List[str]:
        return list(self._map.keys())

    def has(self, key: str) -> bool:
        return key in self._map

    def __contains__(self, key: object) -> bool:
        return key in self._map

    def get(self, key: str) -> int:
        if key not in self._map:
            raise SymbolIdsKeyError(f"SymbolIds does not contain key: {key}")
        return self._map[key]

    def reverse_get(self, key: int) -> str:
        if key not in self._reverse_map:
            raise SymbolIdsKeyError(f"SymbolIds does not contain value: {key}")
        return self._reverse_map[key]

    def get_pos(self, key: str) -> int:
        if key not in self._pos:
            raise SymbolIdsKeyError(f"SymbolIds does not contain key: {key}")
        return self._pos[key]

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._pos[key] = pos
        self._reverse_map[value] = key

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        yield from self._map.items()

    def __repr__(self) -> str:
        return f"SymbolIds({self._map!r})"

    # camelCase aliases, matching the reference API
    reverseGet = reverse_get
    getPos = get_pos
