from typing import Iterator, Optional


class SymbolIds:
    def __init__(self) -> None:
        self._map: dict[str, int] = {}
        self._pos: dict[str, int] = {}
        self._reverse_map: dict[int, str] = {}

    def entries(self) -> Iterator[tuple[str, int]]:
        return iter(self._map.items())

    def __iter__(self) -> Iterator[tuple[str, int]]:
        return iter(self._map.items())

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
        value = self._reverse_map.get(key)
        if value is None:
            raise ValueError(f"SymbolIds does not contain value: {key}")
        return value

    def get_pos(self, key: str) -> int:
        value = self._pos.get(key)
        if value is None:
            raise ValueError(f"SymbolIds does not contain key: {key}")
        return value
