class SymbolIds:
    """Bidirectional name <-> id map that also remembers where each name was seen."""

    def __init__(self):
        # we don't need to delete, just preserve relationships
        self._map: dict[str, int] = {}
        self._pos: dict[str, int] = {}
        self._reverse_map: dict[int, str] = {}

    @property
    def size(self) -> int:
        return len(self._map)

    def keys(self):
        return list(self._map.keys())

    def has(self, key: str) -> bool:
        return key in self._map

    def get(self, key: str) -> int:
        if key not in self._map:
            raise Exception(f"SymbolIds does not contain key: {key}")
        return self._map[key]

    def reverse_get(self, key: int) -> str:
        if key not in self._reverse_map:
            raise Exception(f"SymbolIds does not contain value: {key}")
        return self._reverse_map[key]

    def get_pos(self, key: str) -> int:
        if key not in self._pos:
            raise Exception(f"SymbolIds does not contain key: {key}")
        return self._pos[key]

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._pos[key] = pos
        self._reverse_map[value] = key

    def __iter__(self):
        return iter(list(self._map.items()))

    def __len__(self) -> int:
        return len(self._map)
