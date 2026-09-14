"""Port of ``src/rules-builder/types.ts``."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


@dataclass
class InternalRuleDef:
    """A single element of a linear rule definition.

    The reference implementation models these as a union of object literals;
    since they all share the ``{ type, value? }`` shape a single dataclass keeps
    the port straightforward. ``value`` is a list of code points for ``CHAR`` and
    ``CHAR_NOT``, a single number for ``RULE_REF``/``CHAR_ALT``/
    ``CHAR_RNG_UPPER``, and absent for ``ALT``/``END``.
    """

    type: InternalRuleType
    value: Optional[Union[int, List[int]]] = None

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        if self.value is None:
            return f"InternalRuleDef({self.type.value})"
        return f"InternalRuleDef({self.type.value}, {self.value!r})"


InternalRuleDefChar = InternalRuleDef
InternalRuleDefCharNot = InternalRuleDef
InternalRuleDefCharAlt = InternalRuleDef
InternalRuleDefReference = InternalRuleDef
InternalRuleDefEnd = InternalRuleDef
