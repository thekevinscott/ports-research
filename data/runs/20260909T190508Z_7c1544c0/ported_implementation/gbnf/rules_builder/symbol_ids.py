from typing import Dict, Iterator, KeysView, Tuple


class SymbolIds:
    """An insertion-ordered, bidirectional name <-> id map.

    We never need to delete, just to preserve relationships.
    """

    def __init__(self) -> None:
        self._map: Dict[str, int] = {}
        self._pos: Dict[str, int] = {}
        self._reverse_map: Dict[int, str] = {}

    @property
    def size(self) -> int:
        return len(self._map)

    def keys(self) -> KeysView[str]:
        return self._map.keys()

    def has(self, key: str) -> bool:
        return key in self._map

    def get(self, key: str) -> int:
        if key not in self._map:
            raise Exception(f'SymbolIds does not contain key: {key}')
        return self._map[key]

    def reverse_get(self, key: int) -> str:
        if key not in self._reverse_map:
            raise Exception(f'SymbolIds does not contain value: {key}')
        return self._reverse_map[key]

    def get_pos(self, key: str) -> int:
        if key not in self._pos:
            raise Exception(f'SymbolIds does not contain key: {key}')
        return self._pos[key]

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._pos[key] = pos
        self._reverse_map[value] = key

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        yield from self._map.items()
