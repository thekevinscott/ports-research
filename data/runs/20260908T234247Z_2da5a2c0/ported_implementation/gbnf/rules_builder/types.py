"""Port of ``src/rules-builder/types.ts``.

The TypeScript original models internal rule definitions as plain object literals
(``{ type, value }``). Those are represented here as small mutable objects that
support attribute access as well as ``dict``-style access, so that they read the
same way as the original code.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional, Union


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"

    def __str__(self) -> str:  # mirrors JS string-enum stringification
        return self.value


class InternalRuleDef:
    """A single internal rule definition: a type plus an optional value.

    ``value`` is a ``list[int]`` for ``CHAR``/``CHAR_NOT``, an ``int`` for
    ``RULE_REF``/``CHAR_ALT``/``CHAR_RNG_UPPER``, and absent for ``ALT``/``END``.
    """

    __slots__ = ("type", "value")

    def __init__(
        self,
        type: InternalRuleType,
        value: Optional[Union[int, List[int]]] = None,
    ) -> None:
        self.type = type
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, InternalRuleDef):
            return NotImplemented
        return self.type == other.type and self.value == other.value

    def __hash__(self) -> int:
        value = tuple(self.value) if isinstance(self.value, list) else self.value
        return hash((self.type, value))

    def __repr__(self) -> str:
        if self.value is None:
            return f"InternalRuleDef({self.type.value})"
        return f"InternalRuleDef({self.type.value}, {self.value!r})"

    def to_dict(self) -> dict:
        if self.value is None:
            return {"type": self.type.value}
        return {"type": self.type.value, "value": self.value}
