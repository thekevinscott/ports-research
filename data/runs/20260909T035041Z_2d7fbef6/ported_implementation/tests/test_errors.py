import pytest

from gbnf import GBNF, GrammarParseError, InputParseError
from helpers import END, rules_after


class TestGrammarParseError:
    def test_empty_grammar(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF("")
        assert str(exc.value) == (
            "Failed to parse grammar: No rules were found\n"
            "\n"
            "No input provided"
        )

    def test_whitespace_only_grammar(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF("   ")
        assert str(exc.value) == (
            "Failed to parse grammar: No rules were found\n\n   \n^"
        )

    def test_undefined_rule_identifier(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF("root ::= undefined-rule")
        assert str(exc.value) == (
            'Failed to parse grammar: Undefined rule identifier "undefined-rule"\n'
            "\n"
            "root ::= undefined-rule\n"
            "         ^"
        )

    def test_undefined_rule_identifier_after_other_rules(self):
        # the missing rule is reported even when later rules generate sub-rules
        with pytest.raises(GrammarParseError) as exc:
            GBNF('root ::= "a" missing\nfoo ::= "b"+')
        assert 'Undefined rule identifier "missing"' in str(exc.value)

    def test_missing_definition_operator(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF('root :: "a"')
        assert str(exc.value) == (
            "Failed to parse grammar: Expecting ::= at 5\n\nroot :: \"a\"\n     ^"
        )

    def test_missing_body(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF("root")
        assert str(exc.value) == "Failed to parse grammar: Expecting ::= at 4\n\nroot\n\n^"

    def test_quantifier_without_a_preceding_item(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF("root ::= *")
        assert str(exc.value) == (
            "Failed to parse grammar: Expecting preceding item to */+/? at 9\n"
            "\n"
            "root ::= *\n"
            "         ^"
        )

    def test_unclosed_group(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF('root ::= "a" ("b"')
        assert "Expecting ')' at 17" in str(exc.value)

    def test_invalid_character_in_a_name(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF('root_1 ::= "a"')
        assert str(exc.value) == (
            'Failed to parse grammar: Invalid character "_" when parsing name, '
            "only lowercase letters and hyphens are allowed.\n"
            "\n"
            "root_1 ::= \"a\"\n"
            "    ^"
        )

    def test_unterminated_string(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF('root ::= "unterminated')
        assert "Unexpected end of grammar input, failed to complete parse" in str(exc.value)

    def test_unknown_escape(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF('root ::= "\\q"')
        assert "Unknown escape" in str(exc.value)

    def test_error_carries_the_grammar_and_position(self):
        with pytest.raises(GrammarParseError) as exc:
            GBNF("root ::= *")
        assert exc.value.grammar == "root ::= *"
        assert exc.value.pos == 9
        assert exc.value.reason == "Expecting preceding item to */+/? at 9"

    def test_missing_root_symbol(self):
        with pytest.raises(Exception, match="SymbolIds does not contain key: root"):
            GBNF('foo ::= "a"')

    def test_an_empty_rule_body_is_allowed(self):
        assert rules_after("root ::=") == [END]


class TestInputParseError:
    def test_reports_the_offending_position(self):
        with pytest.raises(InputParseError) as exc:
            GBNF('root ::= "abc"').add("abd")
        assert str(exc.value) == "Failed to parse input string:\n\nabd\n  ^"

    def test_reports_input_past_the_end_of_the_grammar(self):
        with pytest.raises(InputParseError) as exc:
            GBNF('root ::= "abc"').add("abcd")
        assert "Failed to parse input string:" in str(exc.value)

    def test_includes_previously_parsed_input(self):
        state = GBNF('root ::= "abcdef"').add("abc")
        with pytest.raises(InputParseError) as exc:
            state.add("X")
        assert str(exc.value) == "Failed to parse input string:\n\nabcX\n   ^"
        assert exc.value.src == "abcX"

    def test_error_for_most_recent_input_omits_earlier_input(self):
        state = GBNF('root ::= "abcdef"').add("abc")
        with pytest.raises(InputParseError) as exc:
            state.add("X")
        assert exc.value.error_for_most_recent_input == (
            "Failed to parse input string:\n\nX\n^"
        )

    def test_shows_at_most_three_lines_of_context(self):
        with pytest.raises(InputParseError) as exc:
            GBNF("root ::= [a-z\\n]+").add("abc\ndef\nghi!")
        assert str(exc.value) == "Failed to parse input string:\n\ndef\nghi!\n\n ^"
