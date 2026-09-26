import pytest

from .rule_ref import RuleRef


def test_initializes_with_a_given_value():
    rule_ref = RuleRef(123)
    assert rule_ref.value == 123


def test_allows_setting_and_getting_nodes():
    mock_nodes = [1]
    rule_ref = RuleRef(123)
    rule_ref.nodes = mock_nodes
    assert rule_ref.nodes == mock_nodes


def test_raises_an_error_if_trying_to_get_nodes_before_setting():
    rule_ref = RuleRef(123)
    with pytest.raises(ValueError, match="Nodes are not set"):
        rule_ref.nodes
