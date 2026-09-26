from typing import Iterator, Optional


class SymbolIds:
    """An insertion-ordered name -> rule id map that also remembers where in the
    grammar each symbol was declared, plus the reverse id -> name lookup used
    when reporting undefined rule references.
    """

    def __init__(self) -> None:
        self._map: dict[str, int] = {}
        self._pos: dict[str, int] = {}
        self._reverse_map: dict[int, str] = {}

    def entries(self) -> Iterator[tuple[str, int]]:
        return iter(list(self._map.items()))

    def __iter__(self) -> Iterator[tuple[str, int]]:
        return self.entries()

    def __len__(self) -> int:
        return len(self._map)

    def get(self, key: str) -> Optional[int]:
        return self._map.get(key)

    def set(self, key: str, value: int, pos: int) -> None:
        self._map[key] = value
        self._reverse_map[value] = key
        self._pos[key] = pos

    def has(self, key: str) -> bool:
        return key in self._map

    def __contains__(self, key: str) -> bool:
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
