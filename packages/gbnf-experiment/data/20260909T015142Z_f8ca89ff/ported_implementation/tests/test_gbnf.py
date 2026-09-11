"""Public API tests. Expected values were verified against the TypeScript reference."""
import pytest

from ported_implementation import (
    GBNF,
    GrammarParseError,
    InputParseError,
    ParseState,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
    is_range,
)

CHAR = RuleType.CHAR.value
CHAR_EXCLUDE = RuleType.CHAR_EXCLUDE.value
END = RuleType.END.value


def rules(state):
    return [rule.to_dict() for rule in state]


def test_readme_alternates():
    state = GBNF('root  ::= "yes" | "no"')
    assert rules(state) == [
        {"type": CHAR, "value": [ord("y")]},
        {"type": CHAR, "value": [ord("n")]},
    ]


def test_readme_incremental_add():
    state = GBNF('root  ::= "I like green eggs and ham"')
    assert rules(state) == [{"type": CHAR, "value": [ord("I")]}]
    state = state.add("I li")
    assert rules(state) == [{"type": CHAR, "value": [ord("k")]}]
    state = state.add("ke gree")
    assert rules(state) == [{"type": CHAR, "value": [ord("n")]}]
    state = state.add("n eggs and ham")
    assert rules(state) == [{"type": END}]


def test_initial_string_argument():
    state = GBNF('root ::= "yes" | "no"', "y")
    assert rules(state) == [{"type": CHAR, "value": [ord("e")]}]


def test_state_is_callable():
    state = GBNF('root ::= "abc"')
    assert rules(state("ab")) == [{"type": CHAR, "value": [ord("c")]}]


def test_states_are_immutable():
    state = GBNF('root ::= "abc"')
    next_state = state.add("a")
    assert state is not next_state
    assert rules(state) == [{"type": CHAR, "value": [ord("a")]}]
    assert rules(next_state) == [{"type": CHAR, "value": [ord("b")]}]


def test_size_and_len():
    state = GBNF('root ::= "a" | "b" | "c"')
    assert state.size == 3
    assert len(state) == 3
    assert len(list(state)) == 3


def test_grammar_property():
    grammar = 'root ::= "a"'
    assert GBNF(grammar).grammar == grammar


def test_iterating_twice_yields_the_same_rules():
    state = GBNF('root ::= "a" | "b"')
    assert rules(state) == rules(state)


@pytest.mark.parametrize(
    "grammar,expected",
    [
        ("root ::= [a-z]", [{"type": CHAR, "value": [[97, 122]]}]),
        (
            "root ::= [a-zA-Z0-9_]",
            [{"type": CHAR, "value": [[97, 122], [65, 90], [48, 57], 95]}],
        ),
        ("root ::= [^a-z]", [{"type": CHAR_EXCLUDE, "value": [[97, 122]]}]),
        ("root ::= [abc]", [{"type": CHAR, "value": [97, 98, 99]}]),
        ("root ::= [a-]", [{"type": CHAR, "value": [97, 45]}]),
    ],
)
def test_character_classes(grammar, expected):
    assert rules(GBNF(grammar)) == expected


@pytest.mark.parametrize(
    "grammar,expected",
    [
        ('root ::= "a"*', [{"type": CHAR, "value": [97]}, {"type": END}]),
        ('root ::= "a"+', [{"type": CHAR, "value": [97]}]),
        ('root ::= "a"?', [{"type": CHAR, "value": [97]}, {"type": END}]),
    ],
)
def test_quantifiers(grammar, expected):
    assert rules(GBNF(grammar)) == expected


def test_optional_is_satisfied_after_one_match():
    assert rules(GBNF('root ::= "a"?', "a")) == [{"type": END}]


def test_star_repeats():
    state = GBNF('root ::= "a"*', "aaaa")
    assert rules(state) == [{"type": CHAR, "value": [97]}, {"type": END}]


def test_groups_and_alternates():
    state = GBNF('root ::= ("a" | "b") "c"')
    assert rules(state) == [
        {"type": CHAR, "value": [97]},
        {"type": CHAR, "value": [98]},
    ]
    assert rules(state.add("b")) == [{"type": CHAR, "value": [99]}]


def test_rule_references():
    state = GBNF('root ::= a b\na ::= "x"\nb ::= "y"')
    assert rules(state) == [{"type": CHAR, "value": [ord("x")]}]
    assert rules(state.add("x")) == [{"type": CHAR, "value": [ord("y")]}]
    assert rules(state.add("xy")) == [{"type": END}]


def test_recursive_grammar():
    grammar = 'root ::= "(" root ")" | "x"'
    assert rules(GBNF(grammar, "((")) == [
        {"type": CHAR, "value": [ord("(")]},
        {"type": CHAR, "value": [ord("x")]},
    ]
    assert rules(GBNF(grammar, "((x))")) == [{"type": END}]


@pytest.mark.parametrize(
    "grammar,expected_code_point",
    [
        (r'root ::= "\n"', 10),
        (r'root ::= "\t"', 9),
        (r'root ::= "\r"', 13),
        (r'root ::= "\\"', 92),
        (r'root ::= "\""', 34),
        (r'root ::= "\x41"', 65),
        (r'root ::= "é"', 0xE9),
        (r'root ::= "\U0001F600"', 0x1F600),
    ],
)
def test_escape_sequences(grammar, expected_code_point):
    assert rules(GBNF(grammar)) == [{"type": CHAR, "value": [expected_code_point]}]


def test_comments_and_whitespace_are_skipped():
    grammar = '# a comment\n\n  root   ::=   "a"   # trailing\n\n'
    assert rules(GBNF(grammar)) == [{"type": CHAR, "value": [97]}]


def test_crlf_line_endings():
    state = GBNF('root ::= "a"\r\nsecond ::= "b"\r\n')
    assert rules(state) == [{"type": CHAR, "value": [97]}]


def test_unicode_literal():
    state = GBNF('root ::= "héllo"')
    assert rules(state) == [{"type": CHAR, "value": [ord("h")]}]
    assert rules(state.add("h")) == [{"type": CHAR, "value": [ord("é")]}]


def test_accepts_code_point_input():
    state = GBNF('root ::= "abc"')
    assert rules(state.add([ord("a"), ord("b")])) == [{"type": CHAR, "value": [ord("c")]}]
    assert rules(state.add(ord("a"))) == [{"type": CHAR, "value": [ord("b")]}]


def test_accepts_non_string_grammar_via_str():
    class Grammar:
        def __str__(self):
            return 'root ::= "a"'

    assert rules(GBNF(Grammar())) == [{"type": CHAR, "value": [97]}]


def test_json_grammar():
    grammar = """
root   ::= object
object ::= "{" ws ( string ":" ws value ("," ws string ":" ws value)* )? "}" ws
value  ::= object | array | string | number | ("true" | "false" | "null") ws
array  ::= "[" ws ( value ("," ws value)* )? "]" ws
string ::= "\\"" ( [^"\\\\] )* "\\"" ws
number ::= "-"? ([0-9] | [1-9] [0-9]*) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws
ws     ::= ([ \\t\\n] ws)?
"""
    state = GBNF(grammar, '{"a": 1}')
    assert {"type": END} in rules(state)
    with pytest.raises(InputParseError):
        GBNF(grammar, '{"a": }')


def test_arithmetic_grammar():
    grammar = """
root ::= expr
expr ::= term (("+" | "-") term)*
term ::= factor (("*" | "/") factor)*
factor ::= [0-9]+ | "(" expr ")"
"""
    assert {"type": END} in rules(GBNF(grammar, "(1+2)*3"))
    with pytest.raises(InputParseError):
        GBNF(grammar, "1++")


def test_rule_objects_and_types():
    state = GBNF('root ::= [a-z] | "b"')
    rule = list(state)[0]
    assert isinstance(rule, RuleChar)
    assert rule.type == RuleType.CHAR
    assert rule.type == "char"
    assert rule["type"] == "char"
    assert rule == {"type": "char", "value": [[97, 122]]}
    assert is_range(rule.value[0])
    assert not is_range(97)

    end = list(GBNF('root ::= "a"', "a"))[0]
    assert isinstance(end, RuleEnd)
    assert end == {"type": "end"}

    excluded = list(GBNF("root ::= [^a-z]"))[0]
    assert isinstance(excluded, RuleCharExclude)
    assert excluded.type == RuleType.CHAR_EXCLUDE


def test_returns_parse_state():
    assert isinstance(GBNF('root ::= "a"'), ParseState)


def test_grammar_parse_error_is_raised_for_invalid_grammar():
    with pytest.raises(GrammarParseError):
        GBNF("root ::= missing")
