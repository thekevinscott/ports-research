from __future__ import annotations

from typing import Iterator


class SymbolIds:
    def __init__(self) -> None:
        self._map: dict[str, int] = {}
        self._positions: dict[str, int] = {}
        self._reverse_map: dict[int, str] = {}

    def __iter__(self) -> Iterator[tuple[str, int]]:
        yield from self._map.items()

    def entries(self) -> Iterator[tuple[str, int]]:
        return iter(self._map.items())

    @property
    def size(self) -> int:
        return len(self._map)

    def get(self, key: str) -> int | None:
        return self._map.get(key)

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._reverse_map[value] = key
        self._positions[key] = pos

    def has(self, key: str) -> bool:
        return key in self._map

    def reverse_get(self, key: int) -> str:
        val = self._reverse_map.get(key)
        if val is None:
            raise ValueError(f"SymbolIds does not contain value: {key}")
        return val

    def get_pos(self, key: str) -> int:
        val = self._positions.get(key)
        if val is None:
            raise ValueError(f"SymbolIds does not contain key: {key}")
        return val
