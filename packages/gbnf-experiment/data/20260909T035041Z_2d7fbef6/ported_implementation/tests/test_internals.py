"""Tests for the graph internals and the JS-compatibility helpers."""

import pytest

from gbnf import GBNF, GrammarParseError
from gbnf.grammar_graph.generic_set import GenericSet
from gbnf.grammar_graph.get_serialized_rule_key import get_serialized_rule_key
from gbnf.grammar_graph.types import RuleChar, RuleCharExclude, RuleEnd
from gbnf.utils import js
from gbnf.utils.is_point_in_range import is_point_in_range


class TestGenericSet:
    def test_deduplicates_by_derived_key(self):
        s = GenericSet(lambda el: el["id"])
        first = {"id": 1}
        s.add(first)
        s.add({"id": 1})
        assert s.size == 1
        assert list(s) == [first]

    def test_preserves_insertion_order(self):
        s = GenericSet(lambda el: el)
        for value in "cab":
            s.add(value)
        assert list(s) == ["c", "a", "b"]

    def test_get_returns_the_first_element_stored_for_a_key(self):
        s = GenericSet(lambda el: el["id"])
        first = {"id": 1}
        s.add(first)
        assert s.get({"id": 1}) is first

    def test_has_checks_identity(self):
        s = GenericSet(lambda el: el["id"])
        first = {"id": 1}
        s.add(first)
        assert s.has(first)
        assert not s.has({"id": 1})

    def test_delete_removes_the_stored_element(self):
        s = GenericSet(lambda el: el["id"])
        s.add({"id": 1})
        s.delete({"id": 1})
        assert s.size == 0

    def test_delete_of_an_absent_key_raises(self):
        s = GenericSet(lambda el: el["id"])
        with pytest.raises(Exception, match="Could not get ref"):
            s.delete({"id": 1})


class TestRuleKeys:
    def test_end_rules_share_a_key(self):
        assert get_serialized_rule_key(RuleEnd()) == get_serialized_rule_key(RuleEnd())

    def test_char_and_excluded_char_have_different_keys(self):
        assert get_serialized_rule_key(RuleChar([97])) != get_serialized_rule_key(
            RuleCharExclude([97])
        )

    def test_ranges_are_serialized(self):
        assert get_serialized_rule_key(RuleChar([[97, 122]])) == "1-[[97,122]]"

    def test_rules_compare_by_value(self):
        assert RuleChar([97]) == RuleChar([97])
        assert RuleChar([97]) != RuleChar([98])
        assert RuleChar([97]) != RuleCharExclude([97])
        assert len({RuleChar([97]), RuleChar([97])}) == 1


class TestGraph:
    def test_identical_rules_share_a_single_instance(self):
        # the graph deduplicates rules so that pointers can be grouped by identity
        graph = GBNF('root ::= "a" | "a"')._graph
        nodes = [node for root in graph.roots.values() for node in root.values()]
        assert nodes[0].rule is nodes[1].rule

    def test_print_renders_every_path(self):
        graph = GBNF('root ::= "ab" | [c-d]')._graph
        assert graph.print() == "\n{0,0,0}[a]-> {0,0,1}[b]-> {0,0,2}end\n{0,1,0}[c,d]-> {0,1,1}end"

    def test_print_renders_references(self):
        graph = GBNF('root ::= foo\nfoo ::= "a"')._graph
        assert graph.print() == "\n{0,0,0}Ref(1)-> {0,0,1}end\n{1,0,0}[a]-> {1,0,1}end"

    def test_print_can_colorize(self):
        graph = GBNF('root ::= "a"')._graph
        assert "\x1b[" in graph.print(colors=True)
        assert "\x1b[" not in graph.print()

    def test_pointers_are_deduplicated_by_path(self):
        # both alternates reach the same node via the same parent chain after "a"
        state = GBNF('root ::= "a" "b" | "a" "b"').add("a")
        assert state.size == 1


class TestUndefinedRuleReporting:
    def test_reports_the_missing_rule_even_behind_a_generated_sub_rule(self):
        # the reference implementation leaves a hole in its rules array here; the port
        # skips holes so the intended error is reported instead of crashing
        grammar = 'root ::= root "a"\nbar ::= [a-]\nfoo ::= "b" [A-Z] missing+'
        with pytest.raises(GrammarParseError, match='Undefined rule identifier "missing"'):
            GBNF(grammar)


class TestJsHelpers:
    def test_char_at_is_forgiving_out_of_range(self):
        assert js.char_at("ab", 0) == "a"
        assert js.char_at("ab", 5) == ""
        assert js.char_at("ab", -1) == ""

    def test_to_code_units_splits_astral_characters(self):
        assert js.to_code_units("a") == [ord("a")]
        assert js.to_code_units("\U0001f600") == [0xD83D, 0xDE00]

    def test_to_utf16_expands_astral_characters(self):
        assert js.to_utf16("ab") == "ab"
        assert len(js.to_utf16("\U0001f600")) == 2

    def test_from_char_code_truncates_to_16_bits(self):
        assert js.from_char_code(0x41) == "A"
        assert js.from_char_code(0x10041) == "A"

    def test_parse_int_reads_the_longest_valid_prefix(self):
        assert js.parse_int("41", 16) == 0x41
        assert js.parse_int("4z", 16) == 4
        assert js.parse_int("zz", 16) != js.parse_int("zz", 16)  # NaN

    def test_join_renders_none_as_an_empty_string(self):
        assert js.join(["a", None, "b"], "\n") == "a\n\nb"


def test_is_point_in_range():
    assert is_point_in_range(5, [1, 10])
    assert is_point_in_range(1, [1, 10])
    assert is_point_in_range(10, [1, 10])
    assert not is_point_in_range(0, [1, 10])
    assert not is_point_in_range(11, [1, 10])
