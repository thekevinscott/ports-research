"""Rule types exposed by the grammar graph."""

from typing import Any, Callable, List, Optional, Sequence, Union

# A range is a two element list of code points, [start, end].
Range = List[int]


class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"
    REF = "ref"


class PrintOpts:
    def __init__(
        self,
        colorize: Callable[[Any, str], str],
        pointers: Optional[Any] = None,
        show_position: bool = False,
    ):
        self.colorize = colorize
        self.pointers = pointers
        self.show_position = show_position


class RuleChar:
    def __init__(self, value: Optional[Sequence[Union[int, Range]]] = None):
        self.type = RuleType.CHAR
        self.value = list(value) if value is not None else []

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleChar) and self.value == other.value

    # Rules are used as identity keyed dict keys throughout the graph, so keep
    # the default identity hash even though __eq__ is defined.
    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleChar(value={self.value!r})"


class RuleCharExclude:
    def __init__(self, value: Optional[Sequence[Union[int, Range]]] = None):
        self.type = RuleType.CHAR_EXCLUDE
        self.value = list(value) if value is not None else []

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleCharExclude) and self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleCharExclude(value={self.value!r})"


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleEnd)

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return "RuleEnd()"
