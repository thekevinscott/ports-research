import json
import os
from typing import Any, List

from gbnf import RuleChar, RuleCharExclude, RuleEnd, RuleType

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def load_fixture(name: str) -> List[Any]:
    """Load the `test.for` data tables extracted from the JavaScript suite."""
    with open(os.path.join(FIXTURES, f"{name}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def to_rule(expected: dict):
    """Convert a rule from the JavaScript fixtures into its ported equivalent."""
    type_ = expected["type"]
    if type_ == RuleType.CHAR.value:
        return RuleChar(expected["value"])
    if type_ == RuleType.CHAR_EXCLUDE.value:
        return RuleCharExclude(expected["value"])
    if type_ == RuleType.END.value:
        return RuleEnd()
    raise ValueError(f"Unknown rule type: {type_}")


def to_rules(expected: List[dict]) -> List[Any]:
    return [to_rule(rule) for rule in expected]
