"""Port of reference_implementation/src/rules-builder/rules-builder.test.ts.

Not part of the generated suite in /workspace/tests, but it pins the exact
internal rule definitions the parser emits, so it is the sharpest check that the
port matches the reference rather than merely satisfying the public API.
"""

import json
from pathlib import Path

import pytest
from gbnf.rules_builder import RulesBuilder

_CASES = json.loads(
    (Path(__file__).parent / 'fixtures' / 'reference-cases.json').read_text()
)['rules-builder/rules-builder.test.ts']


def as_dict(rule_def):
    # `{ type: ALT }` has no `value` key at all in the reference expectations.
    if rule_def.value is None:
        return {'type': rule_def.type.value}
    return {'type': rule_def.type.value, 'value': rule_def.value}


@pytest.mark.parametrize(
    'grammar, expectation', [case[1:] for case in _CASES], ids=[case[0] for case in _CASES]
)
def test_parses_grammar(grammar, expectation):
    parsed_grammar = RulesBuilder(grammar)
    assert [[as_dict(r) for r in rule] for rule in parsed_grammar.rules] == expectation['rules']
    assert [list(entry) for entry in parsed_grammar.symbol_ids] == [
        list(entry) for entry in expectation['symbolIds']
    ]
