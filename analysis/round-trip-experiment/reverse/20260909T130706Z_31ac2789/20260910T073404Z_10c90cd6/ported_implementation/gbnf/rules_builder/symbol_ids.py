from typing import Dict, Iterator, Optional, Tuple


class SymbolIds:
    def __init__(self):
        self.__map__: Dict[str, int] = {}
        self.__pos__: Dict[str, int] = {}
        self.__reverse_map__: Dict[int, str] = {}

    def entries(self) -> Iterator[Tuple[str, int]]:
        return iter(list(self.__map__.items()))

    def items(self) -> Iterator[Tuple[str, int]]:
        return self.entries()

    def keys(self) -> Iterator[str]:
        return iter(list(self.__map__.keys()))

    def values(self) -> Iterator[int]:
        return iter(list(self.__map__.values()))

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        return self.entries()

    @property
    def size(self) -> int:
        return len(self.__map__)

    def __len__(self) -> int:
        return self.size

    def get(self, key: str) -> Optional[int]:
        return self.__map__.get(key)

    def set(self, key: str, value: int, pos: int) -> None:
        self.__map__[key] = value
        self.__reverse_map__[value] = key
        self.__pos__[key] = pos

    def has(self, key: str) -> bool:
        return key in self.__map__

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __getitem__(self, key: str) -> int:
        return self.__map__[key]

    def reverse_get(self, key: int) -> str:
        val = self.__reverse_map__.get(key)
        if val is None:
            raise ValueError(f"SymbolIds does not contain value: {key}")
        return val

    def get_pos(self, key: str) -> int:
        val = self.__pos__.get(key)
        if val is None:
            raise ValueError(f"SymbolIds does not contain key: {key}")
        return val

    reverseGet = reverse_get
    getPos = get_pos

    def to_json(self) -> Dict[str, int]:
        return dict(self.__map__)

    toJSON = to_json

    def __repr__(self) -> str:
        return f"SymbolIds({self.__map__!r})"
