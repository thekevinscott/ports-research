"""Rule name to rule id bookkeeping."""

from typing import Dict, Iterator, Optional, Tuple


class SymbolIds:
    def __init__(self) -> None:
        self.map: Dict[str, int] = {}
        self.positions: Dict[str, int] = {}
        self.reverse_map: Dict[int, str] = {}

    @property
    def size(self) -> int:
        return len(self.map)

    def __len__(self) -> int:
        return len(self.map)

    def entries(self) -> Iterator[Tuple[str, int]]:
        return iter(self.map.items())

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        return iter(self.map.items())

    def get(self, key: str) -> Optional[int]:
        return self.map.get(key)

    def set(self, key: str, value: int, pos: int) -> None:
        self.map[key] = value
        self.reverse_map[value] = key
        self.positions[key] = pos

    def has(self, key: str) -> bool:
        return key in self.map

    def __contains__(self, key: str) -> bool:
        return key in self.map

    def reverse_get(self, key: int) -> str:
        val = self.reverse_map.get(key)
        if val is None:
            raise ValueError(f"SymbolIds does not contain value: {key}")
        return val

    def get_pos(self, key: str) -> int:
        val = self.positions.get(key)
        if val is None:
            raise ValueError(f"SymbolIds does not contain key: {key}")
        return val
