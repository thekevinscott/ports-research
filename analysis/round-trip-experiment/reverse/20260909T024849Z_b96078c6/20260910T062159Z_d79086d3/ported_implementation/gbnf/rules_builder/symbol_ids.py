"""A mapping of rule name -> rule id.

It additionally remembers the position in the grammar each symbol was declared at, and
supports looking a name up by its id.
"""

from __future__ import annotations

from typing import Dict, Iterator, ItemsView, KeysView, Optional, Tuple, ValuesView


class SymbolIds:
    def __init__(self) -> None:
        self._mapping: Dict[str, int] = {}
        self.positions: Dict[str, int] = {}
        self.reverse_mapping: Dict[int, str] = {}

    def set(self, key: str, value: int, pos: int = 0) -> "SymbolIds":
        self._mapping[key] = value
        self.reverse_mapping[value] = key
        self.positions[key] = pos
        return self

    def get(self, key: str, default: Optional[int] = None) -> Optional[int]:
        return self._mapping.get(key, default)

    def has(self, key: str) -> bool:
        return key in self._mapping

    def reverse_get(self, key: int) -> str:
        if key not in self.reverse_mapping:
            raise ValueError(f"SymbolIds does not contain value: {key}")
        return self.reverse_mapping[key]

    def get_pos(self, key: str) -> int:
        if key not in self.positions:
            raise ValueError(f"SymbolIds does not contain key: {key}")
        return self.positions[key]

    def items(self) -> ItemsView[str, int]:
        return self._mapping.items()

    def keys(self) -> KeysView[str]:
        return self._mapping.keys()

    def values(self) -> ValuesView[int]:
        return self._mapping.values()

    def __getitem__(self, key: str) -> int:
        return self._mapping[key]

    def __setitem__(self, key: str, value: int) -> None:
        self.set(key, value)

    def __contains__(self, key: object) -> bool:
        return key in self._mapping

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SymbolIds):
            return self._mapping == other._mapping
        if isinstance(other, dict):
            return self._mapping == other
        return NotImplemented

    def __hash__(self) -> int:
        return id(self)

    def to_dict(self) -> Dict[str, int]:
        return dict(self._mapping)

    def __repr__(self) -> str:
        entries: Tuple[str, ...] = tuple(
            f"{key}={value}" for key, value in self._mapping.items()
        )
        return f"SymbolIds({', '.join(entries)})"
