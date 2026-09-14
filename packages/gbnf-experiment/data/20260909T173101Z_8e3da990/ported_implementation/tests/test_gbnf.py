import pytest

from ported_implementation import GBNF, GrammarParseError, InputParseError, ParseState, RuleType


def rules(state):
    return [rule.to_dict() for rule in state]


def chars(state):
    return [rule.value for rule in state if rule.type == RuleType.CHAR]


def test_returns_a_parse_state():
    assert isinstance(GBNF('root ::= "a"'), ParseState)


def test_yields_the_first_char_of_a_literal():
    assert rules(GBNF('root ::= "yes" | "no"')) == [
        {'type': RuleType.CHAR, 'value': [ord('y')]},
        {'type': RuleType.CHAR, 'value': [ord('n')]},
    ]


def test_walks_a_literal_one_token_at_a_time():
    state = GBNF('root ::= "I like green eggs and ham"')
    assert chars(state) == [[ord('I')]]
    state = state.add('I li')
    assert chars(state) == [[ord('k')]]
    state = state.add('ke gree')
    assert chars(state) == [[ord('n')]]


def test_states_are_immutable():
    state = GBNF('root ::= "abc"')
    advanced = state.add('a')
    assert chars(state) == [[ord('a')]]
    assert chars(advanced) == [[ord('b')]]


def test_a_state_can_be_called_directly():
    state = GBNF('root ::= "abc"')
    assert chars(state('a')) == [[ord('b')]]


def test_reports_the_end_of_a_valid_string():
    state = GBNF('root ::= "ab"').add('ab')
    assert rules(state) == [{'type': RuleType.END}]


def test_accepts_an_initial_string():
    assert chars(GBNF('root ::= "abc"', 'ab')) == [[ord('c')]]


def test_accepts_code_points_as_input():
    assert chars(GBNF('root ::= "abc"').add(ord('a'))) == [[ord('b')]]
    assert chars(GBNF('root ::= "abc"').add([ord('a'), ord('b')])) == [[ord('c')]]


def test_exposes_ranges_for_char_classes():
    assert rules(GBNF('root ::= [a-z0-9]')) == [
        {'type': RuleType.CHAR, 'value': [[ord('a'), ord('z')], [ord('0'), ord('9')]]},
    ]


def test_exposes_excluded_chars():
    assert rules(GBNF('root ::= [^a-z]')) == [
        {'type': RuleType.CHAR_EXCLUDE, 'value': [[ord('a'), ord('z')]]},
    ]
    assert chars(GBNF('root ::= [^a-z] "!"').add('Q')) == [[ord('!')]]
    with pytest.raises(InputParseError):
        GBNF('root ::= [^a-z]').add('q')


def test_repetition_operators():
    assert chars(GBNF('root ::= "a"* "b"').add('aaa')) == [[ord('a')], [ord('b')]]
    assert chars(GBNF('root ::= "a"+ "b"').add('a')) == [[ord('a')], [ord('b')]]
    assert chars(GBNF('root ::= "a"? "b"')) == [[ord('a')], [ord('b')]]


def test_groups_and_alternates():
    assert chars(GBNF('root ::= ("a" | "b") "c"').add('b')) == [[ord('c')]]


def test_rule_references():
    state = GBNF('root ::= prefix suffix\nprefix ::= "a"\nsuffix ::= "b"')
    assert chars(state.add('a')) == [[ord('b')]]


def test_recursive_rules():
    state = GBNF('root ::= a\na ::= "x" a | "y"')
    assert chars(state.add('xxx')) == [[ord('x')], [ord('y')]]
    assert rules(state.add('xxxy')) == [{'type': RuleType.END}]


def test_escapes():
    assert chars(GBNF(r'root ::= "\n\t\x41é"')) == [[ord('\n')]]
    assert chars(GBNF(r'root ::= "\x41" "b"').add('A')) == [[ord('b')]]
    assert chars(GBNF(r'root ::= "é" "b"').add('é')) == [[ord('b')]]


def test_comments_are_ignored():
    grammar = '# leading\nroot ::= "a" # trailing\n'
    assert chars(GBNF(grammar)) == [[ord('a')]]


def test_size_and_grammar_accessors():
    grammar = 'root ::= "a" | "b"'
    state = GBNF(grammar)
    assert state.size == 2
    assert len(state) == 2
    assert state.grammar == grammar


def test_deduplicates_identical_rules():
    assert GBNF('root ::= "a" | "a"').size == 1


def test_rejects_input_that_does_not_match():
    with pytest.raises(InputParseError):
        GBNF('root ::= "yes"').add('n')


def test_rejects_input_past_the_end_of_the_grammar():
    state = GBNF('root ::= "a"').add('a')
    with pytest.raises(InputParseError):
        state.add('a')


def test_rejects_an_empty_grammar():
    with pytest.raises(GrammarParseError) as excinfo:
        GBNF('')
    assert 'No rules were found' in str(excinfo.value)


def test_rejects_a_grammar_without_a_root_rule():
    # matches the reference implementation, which raises out of its symbol table
    with pytest.raises(Exception, match='does not contain key: root'):
        GBNF('a ::= "b"')


def test_rejects_an_undefined_rule_reference():
    with pytest.raises(GrammarParseError, match='Undefined rule identifier "missing"'):
        GBNF('root ::= missing')


def test_rejects_a_missing_definition_operator():
    with pytest.raises(GrammarParseError, match='Expecting ::='):
        GBNF('root := "a"')


def test_rejects_an_unclosed_group():
    with pytest.raises(GrammarParseError, match=r"Expecting '\)'"):
        GBNF('root ::= ("a"')


def test_rejects_a_dangling_repetition_operator():
    with pytest.raises(GrammarParseError, match=r'Expecting preceding item to \*/\+/\?'):
        GBNF('root ::= *')


def test_rejects_an_unknown_escape():
    with pytest.raises(GrammarParseError, match='Unknown escape'):
        GBNF(r'root ::= "\q"')


def test_rejects_an_unterminated_literal():
    with pytest.raises(GrammarParseError, match='Unexpected end of grammar input'):
        GBNF('root ::= "a')


def test_rejects_an_invalid_character_in_a_name():
    with pytest.raises(GrammarParseError, match='Invalid character "_"'):
        GBNF('root_1 ::= "a"')


def test_accepts_a_grammar_like_object():
    class Builder:
        def __str__(self):
            return 'root ::= "a"'

    assert chars(GBNF(Builder())) == [[ord('a')]]


def test_parses_a_json_grammar():
    grammar = '\n'.join([
        'root   ::= object',
        'value  ::= object | array | string | number | ("true" | "false" | "null") ws',
        'object ::= "{" ws ( string ":" ws value ("," ws string ":" ws value)* )? "}" ws',
        'array  ::= "[" ws ( value ("," ws value)* )? "]" ws',
        'string ::= "\\"" ( [^"\\\\] )* "\\"" ws',
        'number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws',
        'ws ::= ([ \\t\\n] ws)?',
    ])
    state = GBNF(grammar)
    for token in ['{', '"a"', ': ', '123', ', ', '"b"', ': ', '[true, null]', '}']:
        state = state.add(token)
    assert any(rule.type == RuleType.END for rule in state)


def test_handles_deeply_nested_input():
    grammar = 'root ::= array\narray ::= "[" (array ("," array)*)? "]"'
    depth = 2000
    state = GBNF(grammar).add('[' * depth + ']' * depth)
    assert rules(state) == [{'type': RuleType.END}]


def test_rejects_a_grammar_that_recurses_without_consuming_input():
    with pytest.raises(RecursionError):
        GBNF('root ::= ("a"*)+')
