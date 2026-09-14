from typing import Dict, Iterator, Optional, Tuple


class SymbolIds:
    def __init__(self) -> None:
        self.__map: Dict[str, int] = {}
        self.__pos: Dict[str, int] = {}
        self.__reverse_map: Dict[int, str] = {}

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        yield from self.__map.items()

    def entries(self) -> Iterator[Tuple[str, int]]:
        return iter(self.__map.items())

    def __len__(self) -> int:
        return len(self.__map)

    @property
    def size(self) -> int:
        return len(self.__map)

    def get(self, key: str) -> Optional[int]:
        return self.__map.get(key)

    def set(self, key: str, value: int, pos: int) -> None:
        self.__map[key] = value
        self.__reverse_map[value] = key
        self.__pos[key] = pos

    def has(self, key: str) -> bool:
        return key in self.__map

    def reverse_get(self, key: int) -> str:
        val = self.__reverse_map.get(key)
        if val is None:
            raise Exception(f"SymbolIds does not contain value: {key}")
        return val

    def get_pos(self, key: str) -> int:
        val = self.__pos.get(key)
        if val is None:
            raise Exception(f"SymbolIds does not contain key: {key}")
        return val
