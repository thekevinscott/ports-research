from typing import Dict, Generator, ItemsView, Optional, Tuple


class SymbolIds:
    def __init__(self) -> None:
        self._map: Dict[str, int] = {}
        self._pos: Dict[str, int] = {}
        self._reverse_map: Dict[int, str] = {}

    def entries(self) -> ItemsView[str, int]:
        return self._map.items()

    def __iter__(self) -> Generator[Tuple[str, int], None, None]:
        yield from list(self._map.items())

    @property
    def size(self) -> int:
        return len(self._map)

    def get(self, key: str) -> Optional[int]:
        return self._map.get(key)

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._reverse_map[value] = key
        self._pos[key] = pos

    def has(self, key: str) -> bool:
        return key in self._map

    def reverse_get(self, key: int) -> str:
        val = self._reverse_map.get(key)
        if val is None:
            raise ValueError(f"SymbolIds does not contain value: {key}")
        return val

    def get_pos(self, key: str) -> int:
        val = self._pos.get(key)
        if val is None:
            raise ValueError(f"SymbolIds does not contain key: {key}")
        return val
