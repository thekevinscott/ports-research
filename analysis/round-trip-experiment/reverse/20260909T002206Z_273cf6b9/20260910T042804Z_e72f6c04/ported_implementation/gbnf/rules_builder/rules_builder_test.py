"""Cases for the rules builder.

The table is ~1400 lines of `InternalRuleDef*` literals, so it lives beside this file as
`rules_builder_cases.json` and is rebuilt into rule defs here.
"""

import json
from pathlib import Path

import pytest

from .rules_builder import RulesBuilder
from .rules_builder_types import (
    InternalRuleDefAlt,
    InternalRuleDefChar,
    InternalRuleDefCharAlt,
    InternalRuleDefCharNot,
    InternalRuleDefCharRngUpper,
    InternalRuleDefEnd,
    InternalRuleDefReference,
)

CASES = json.loads((Path(__file__).parent / "rules_builder_cases.json").read_text())

BUILDERS = {
    "char": InternalRuleDefChar,
    "char_alt": InternalRuleDefCharAlt,
    "char_not": InternalRuleDefCharNot,
    "char_rng_upper": InternalRuleDefCharRngUpper,
    "ref": InternalRuleDefReference,
    "alt": InternalRuleDefAlt,
    "end": InternalRuleDefEnd,
}


def build_rule_def(fixture):
    kind = fixture["kind"]
    if kind not in BUILDERS:
        raise Exception(f"Unknown rule def kind: {kind}")
    if "value" in fixture:
        return BUILDERS[kind](fixture["value"])
    return BUILDERS[kind]()


@pytest.mark.parametrize(
    ("key", "grammar", "expected"),
    [(key, grammar, expected) for key, grammar, expected in CASES],
)
def test_it_parses_a_grammar(key, grammar, expected):
    symbol_ids_expected, rules_expected = expected
    parsed_grammar = RulesBuilder(grammar.replace("\\n", "\n"))
    assert parsed_grammar.rules == [
        [build_rule_def(rule_def) for rule_def in rule] for rule in rules_expected
    ]
    assert list(parsed_grammar.symbol_ids.entries()) == [
        (name, id) for name, id in symbol_ids_expected
    ]
