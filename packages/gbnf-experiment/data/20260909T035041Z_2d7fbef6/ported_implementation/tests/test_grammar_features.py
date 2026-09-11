import pytest

from gbnf import GBNF, InputParseError
from helpers import END, char, char_exclude, rules, rules_after


class TestLiterals:
    def test_single_character(self):
        assert rules_after('root ::= "a"') == [char(ord("a"))]

    def test_sequence(self):
        assert rules_after('root ::= "ab"', "a") == [char(ord("b"))]

    def test_alternates(self):
        assert rules_after('root ::= "ab" | "cd"') == [char(ord("a")), char(ord("c"))]

    def test_alternates_of_differing_length(self):
        assert rules_after('root ::= "a" | "ab" | "abc"', "a") == [END, char(ord("b"))]


class TestCharacterClasses:
    def test_range(self):
        assert rules_after("root ::= [a-z]") == [char([ord("a"), ord("z")])]

    def test_range_matches_any_member(self):
        for letter in "aqz":
            assert rules_after("root ::= [a-z]", letter) == [END]

    def test_range_rejects_non_members(self):
        with pytest.raises(InputParseError):
            GBNF("root ::= [a-z]").add("A")

    def test_alternates(self):
        assert rules_after("root ::= [abc]") == [char(ord("a"), ord("b"), ord("c"))]

    def test_mixed_ranges_and_alternates(self):
        assert rules_after("root ::= [a-c0-9x]") == [
            char([ord("a"), ord("c")], [ord("0"), ord("9")], ord("x"))
        ]

    def test_negated_range(self):
        assert rules_after("root ::= [^a-z]") == [char_exclude([ord("a"), ord("z")])]

    def test_negated_range_matches_outside_the_range(self):
        assert rules_after("root ::= [^a-z]", "A") == [END]

    def test_negated_range_rejects_members(self):
        with pytest.raises(InputParseError):
            GBNF("root ::= [^a-z]").add("a")

    def test_trailing_hyphen_is_a_literal(self):
        assert rules_after("root ::= [a-]", "-") == [END]

    def test_leading_hyphen_is_a_literal(self):
        assert rules_after("root ::= [-a]", "-") == [END]


class TestQuantifiers:
    def test_optional(self):
        assert rules_after('root ::= "a"?') == [char(ord("a")), END]
        assert rules_after('root ::= "a"?', "a") == [END]

    def test_star_allows_zero(self):
        assert rules_after('root ::= "a"*') == [char(ord("a")), END]

    def test_star_allows_many(self):
        assert rules_after('root ::= "a"*', "aaaa") == [char(ord("a")), END]

    def test_plus_requires_one(self):
        assert rules_after('root ::= "a"+') == [char(ord("a"))]
        assert rules_after('root ::= "a"+', "a") == [char(ord("a")), END]

    def test_plus_rejects_zero(self):
        with pytest.raises(InputParseError):
            GBNF('root ::= "a"+').add("b")

    def test_optional_may_be_skipped(self):
        assert rules_after('root ::= "a" "b"? "c"', "a") == [char(ord("b")), char(ord("c"))]
        assert rules_after('root ::= "a" "b"? "c"', "ac") == [END]
        assert rules_after('root ::= "a" "b"? "c"', "abc") == [END]


class TestGroups:
    def test_group(self):
        assert rules_after('root ::= ("a")', "a") == [END]

    def test_group_with_alternates(self):
        assert rules_after('root ::= ("a" | "b")+', "ab") == [
            char(ord("a")),
            char(ord("b")),
            END,
        ]

    def test_nested_groups(self):
        assert rules_after('root ::= (("a" | "b") "c")+', "ac") == [
            char(ord("a")),
            char(ord("b")),
            END,
        ]

    def test_deeply_nested_groups(self):
        grammar = "root ::= " + "(" * 20 + '"a"' + ")" * 20
        assert rules_after(grammar, "a") == [END]


class TestReferences:
    def test_simple_reference(self):
        assert rules_after('root ::= foo\nfoo ::= "bar"', "b", "a") == [char(ord("r"))]

    def test_multiple_references(self):
        grammar = 'root ::= foo bar\nfoo ::= "a"\nbar ::= "b"'
        assert rules_after(grammar, "a") == [char(ord("b"))]

    def test_hyphenated_rule_names(self):
        assert rules_after('root ::= a-b\na-b ::= "x"', "x") == [END]

    def test_rule_defined_before_use(self):
        assert rules_after('foo ::= "a"\nroot ::= foo', "a") == [END]


class TestEscapes:
    @pytest.mark.parametrize(
        ("escape", "expected"),
        [
            ("\\t", "\t"),
            ("\\n", "\n"),
            ("\\r", "\r"),
            ("\\x41", "A"),
            ("\\u0041", "A"),
            ('\\"', '"'),
            ("\\\\", "\\"),
        ],
    )
    def test_escape_sequences(self, escape, expected):
        assert rules_after(f'root ::= "{escape}"') == [char(ord(expected))]

    def test_bracket_escapes_inside_a_class(self):
        assert rules_after("root ::= [\\[\\]]") == [char(ord("["), ord("]"))]

    def test_unknown_escape_is_rejected(self):
        from gbnf import GrammarParseError

        with pytest.raises(GrammarParseError):
            GBNF('root ::= "\\q"')


class TestUnicode:
    def test_multibyte_literals(self):
        assert rules_after('root ::= "日本語"', "日") == [char(ord("本"))]

    def test_multibyte_ranges(self):
        assert rules_after("root ::= [ぁ-ん]+", "あ") == [
            char([ord("ぁ"), ord("ん")]),
            END,
        ]

    def test_astral_escape_matches_a_surrogate_pair(self):
        # `\U` escapes produce a full code point, while string input is fed in as
        # UTF-16 code units, matching the reference implementation.
        (rule,) = GBNF('root ::= "\\U0001F600"')
        assert rule.value == [0x1F600]


class TestWhitespaceAndComments:
    def test_leading_and_trailing_whitespace(self):
        assert rules_after('   root   ::=   "a"   ') == [char(ord("a"))]

    def test_comments_are_ignored(self):
        assert rules_after('# a comment\nroot ::= "a" # trailing\n') == [char(ord("a"))]

    def test_blank_lines_are_ignored(self):
        assert rules_after('root ::= "a"\n\n\n') == [char(ord("a"))]

    def test_carriage_returns_are_handled(self):
        assert rules_after('root ::= "a"\r\nfoo ::= "b"\r\n') == [char(ord("a"))]


class TestRecursion:
    def test_right_recursive_grammar(self):
        grammar = 'root ::= "a" root | "b"'
        assert rules_after(grammar) == [char(ord("a")), char(ord("b"))]
        assert rules_after(grammar, "aab") == [END]

    def test_repetition_via_a_reference(self):
        grammar = 'root ::= ws "a"\nws ::= [ ]*'
        assert rules(GBNF(grammar, "   a")) == [END]
