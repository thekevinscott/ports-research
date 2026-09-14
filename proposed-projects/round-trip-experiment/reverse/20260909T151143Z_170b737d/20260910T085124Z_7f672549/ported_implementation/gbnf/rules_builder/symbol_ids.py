from typing import Dict, ItemsView, Iterator, Tuple


class SymbolIds:
    def __init__(self):
        self.__map__: Dict[str, int] = {}
        self.__pos__: Dict[str, int] = {}
        self.__reverse_map__: Dict[int, str] = {}

    def items(self) -> ItemsView[str, int]:
        return self.__map__.items()

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        return iter(self.__map__.items())

    def __len__(self) -> int:
        return len(self.__map__)

    def __getitem__(self, key: str) -> int:
        return self.__map__[key]

    def set(self, key: str, value: int, pos: int) -> None:
        self.__map__[key] = value
        self.__reverse_map__[value] = key
        self.__pos__[key] = pos

    def __contains__(self, key: str) -> bool:
        return key in self.__map__

    def has(self, key: str) -> bool:
        return key in self.__map__

    def reverse_get(self, key: int) -> str:
        if key not in self.__reverse_map__:
            raise ValueError(f"SymbolIds does not contain value: {key}")
        return self.__reverse_map__[key]

    def get_pos(self, key: str) -> int:
        if key not in self.__pos__:
            raise ValueError(f"SymbolIds does not contain key: {key}")
        return self.__pos__[key]
