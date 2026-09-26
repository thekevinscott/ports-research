"""Port of ``src/rules-builder/symbol-ids.ts``."""

from __future__ import annotations

from typing import Dict, Iterator, Tuple


class SymbolIds:
    # we don't need to delete, just preserve relationships
    def __init__(self) -> None:
        self._map: Dict[str, int] = {}
        self._pos: Dict[str, int] = {}
        self._reverse_map: Dict[int, str] = {}

    @property
    def size(self) -> int:
        return len(self._map)

    def keys(self) -> Iterator[str]:
        return iter(list(self._map.keys()))

    def has(self, key: str) -> bool:
        return key in self._map

    def get(self, key: str) -> int:
        val = self._map.get(key)
        if val is None:
            raise KeyError(f'SymbolIds does not contain key: {key}')
        return val

    def reverse_get(self, key: int) -> str:
        val = self._reverse_map.get(key)
        if val is None:
            raise KeyError(f'SymbolIds does not contain value: {key}')
        return val

    def get_pos(self, key: str) -> int:
        pos = self._pos.get(key)
        if pos is None:
            raise KeyError(f'SymbolIds does not contain key: {key}')
        return pos

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._pos[key] = pos
        self._reverse_map[value] = key

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        return iter(list(self._map.items()))

    def __len__(self) -> int:
        return len(self._map)
