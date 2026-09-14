import json
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

Colorize = Callable[[Union[str, int], str], str]

# A range is a two element list of code points, [low, high].
Range = List[int]

RuleDict = Dict[str, Any]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]


class PrintOpts:
    def __init__(
        self,
        colorize: Colorize,
        pointers: Optional[Any] = None,
        show_position: bool = False,
    ):
        self.colorize = colorize
        self.pointers = pointers
        self.show_position = show_position


class Rule:
    @property
    def type(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Rule) and type(other) is type(self)

    def __hash__(self) -> int:
        return hash(self.type)

    def to_dict(self) -> RuleDict:
        return {"type": self.type}

    def to_json(self) -> RuleDict:
        return self.to_dict()

    def __repr__(self) -> str:
        return f"{self.type}()"


class RuleWithValue(Rule):
    def __init__(self, value: Any):
        self.value = value

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, RuleWithValue)
            and type(other) is type(self)
            and self.value == other.value
        )

    def __hash__(self) -> int:
        return hash((self.type, json.dumps(self.value)))

    def to_dict(self) -> RuleDict:
        return {**super().to_dict(), "value": self.value}

    def __repr__(self) -> str:
        return f"{self.type}(value={json.dumps(self.value)})"


class RuleWithListOfIntsOrRanges(RuleWithValue):
    def __init__(self, value: Optional[Sequence[Union[int, Range]]] = None):
        # copy the incoming list so that later mutation of the rule's value cannot be
        # observed by the caller.
        super().__init__(list(value) if value is not None else [])


class RuleChar(RuleWithListOfIntsOrRanges):
    @property
    def type(self) -> str:
        return "RuleChar"


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    @property
    def type(self) -> str:
        return "RuleCharExclude"


class RuleEnd(Rule):
    @property
    def type(self) -> str:
        return "RuleEnd"
