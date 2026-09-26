"""Port of ``src/rules-builder/symbol-ids.ts``."""
from __future__ import annotations

from typing import Iterator, KeysView, Tuple


class SymbolIds:
    # we don't need to delete, just preserve relationships
    def __init__(self) -> None:
        self._map: "dict[str, int]" = {}
        self._pos: "dict[str, int]" = {}
        self._reverse_map: "dict[int, str]" = {}

    @property
    def size(self) -> int:
        return len(self._map)

    def keys(self) -> KeysView[str]:
        return self._map.keys()

    def has(self, key: str) -> bool:
        return key in self._map

    def __contains__(self, key: str) -> bool:
        return key in self._map

    def get(self, key: str) -> int:
        if key not in self._map:
            raise KeyError(f'SymbolIds does not contain key: {key}')
        return self._map[key]

    def reverse_get(self, key: int) -> str:
        if key not in self._reverse_map:
            raise KeyError(f'SymbolIds does not contain value: {key}')
        return self._reverse_map[key]

    def get_pos(self, key: str) -> int:
        if key not in self._pos:
            raise KeyError(f'SymbolIds does not contain key: {key}')
        return self._pos[key]

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._pos[key] = pos
        self._reverse_map[value] = key

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        return iter(list(self._map.items()))

    def __len__(self) -> int:
        return len(self._map)
