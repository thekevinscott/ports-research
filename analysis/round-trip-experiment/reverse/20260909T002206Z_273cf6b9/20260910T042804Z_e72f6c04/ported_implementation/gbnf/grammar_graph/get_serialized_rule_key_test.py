import pytest

from . import get_serialized_rule_key as module
from .get_serialized_rule_key import KEY_TRANSLATION, get_serialized_rule_key
from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .rule_ref import RuleRef

GUARDS = ["is_rule_end", "is_rule_char", "is_rule_char_exclude", "is_rule_ref"]


@pytest.fixture(autouse=True)
def stub_guards(monkeypatch):
    """Every guard reports False unless a test opts one back in."""
    for guard in GUARDS:
        monkeypatch.setattr(module, guard, lambda rule: False)
    yield monkeypatch


def enable(monkeypatch, guard):
    monkeypatch.setattr(module, guard, lambda rule: True)


def test_returns_type_for_end_rules(stub_guards):
    enable(stub_guards, "is_rule_end")
    assert get_serialized_rule_key(RuleEnd()) == f"{KEY_TRANSLATION.RuleEnd}"


def test_returns_type_and_value_for_character_rules(stub_guards):
    enable(stub_guards, "is_rule_char")
    assert (
        get_serialized_rule_key(RuleChar([97])) == f"{KEY_TRANSLATION.RuleChar}-[97]"
    )


def test_returns_type_and_value_for_character_exclude_rules(stub_guards):
    enable(stub_guards, "is_rule_char_exclude")
    assert (
        get_serialized_rule_key(RuleCharExclude([97]))
        == f"{KEY_TRANSLATION.RuleCharExclude}-[97]"
    )


def test_returns_ref_type_with_value_for_reference_rules(stub_guards):
    enable(stub_guards, "is_rule_ref")
    assert get_serialized_rule_key(RuleRef(99)) == "3-99"


def test_raises_for_unknown_rule_types():
    with pytest.raises(ValueError, match="Unknown rule type"):
        get_serialized_rule_key({"type": "UNKNOWN", "value": "something"})
