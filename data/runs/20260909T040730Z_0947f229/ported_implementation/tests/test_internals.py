"""Ports of the reference implementation's own unit tests for the small helpers.

These live alongside the generated suite in /workspace/tests to cover the
edge-case behaviour (JS truthiness, sparse indexing, escape handling) that the
public-API tests only reach indirectly.
"""

import pytest
from gbnf import GBNF, GrammarParseError, InputParseError, is_range
from gbnf.grammar_graph.generic_set import GenericSet
from gbnf.grammar_graph.get_input_as_code_points import get_input_as_code_points
from gbnf.grammar_graph.get_serialized_rule_key import (
    KEY_TRANSLATION,
    get_serialized_rule_key,
)
from gbnf.grammar_graph.rule_ref import RuleRef
from gbnf.grammar_graph.types import RuleChar, RuleCharExclude, RuleEnd, RuleType
from gbnf.rules_builder.is_word_char import is_word_char
from gbnf.rules_builder.parse_char import parse_char
from gbnf.rules_builder.parse_name import (
    GET_INVALID_CHAR_ERROR,
    PARSE_NAME_ERROR,
    parse_name,
)
from gbnf.rules_builder.parse_space import parse_space
from gbnf.utils.errors.build_error_position import build_error_position
from gbnf.utils.errors.get_input_as_string import get_input_as_string
from gbnf.utils.errors.grammar_parse_error import GRAMMAR_PARSER_ERROR_HEADER_MESSAGE
from gbnf.utils.errors.input_parse_error import INPUT_PARSER_ERROR_HEADER_MESSAGE
from gbnf.utils.is_point_in_range import is_point_in_range


class TestBuildErrorPosition:
    @pytest.mark.parametrize(
        'grammar, pos, expected',
        [
            ('root ::= "foo"', 1, ['root ::= "foo"', ' ^']),
            ('root ::= "foo"', 5, ['root ::= "foo"', '     ^']),
            # multi line grammars with pos on first line
            ('aa\nbb', 1, ['aa', ' ^']),
            # multi line grammars with pos on second line, first character
            ('aa\nbb', 2, ['aa', 'bb', '^']),
            # multi line grammars with pos on second line, second character
            ('aa\nbb', 3, ['aa', 'bb', ' ^']),
            # multi line grammars beyond error with pos on second line
            ('aa\nbb\ncc', 3, ['aa', 'bb', ' ^']),
            # multi line grammars beyond error with pos on third line, first char
            ('aa\nbb\ncc', 4, ['aa', 'bb', 'cc', '^']),
            # multi line grammars beyond error with pos on third line, second char
            ('aa\nbb\ncc', 5, ['aa', 'bb', 'cc', ' ^']),
            # multi line grammars beyond error with pos on fourth line, first char
            ('aa\nbb\ncc\ndd', 6, ['bb', 'cc', 'dd', '^']),
            # multi line grammars beyond error with pos on fifth line, second char
            ('aa\nbb\ncc\ndd\nee', 9, ['cc', 'dd', 'ee', ' ^']),
        ],
    )
    def test_it_correctly_shows_position(self, grammar, pos, expected):
        assert build_error_position(grammar, pos) == expected

    def test_it_renders_a_message_for_empty_input(self):
        assert build_error_position('', 0) == ['No input provided']


class TestErrors:
    def test_grammar_parse_error_renders_a_message(self):
        err = GrammarParseError('aa\nbb\ncc\ndd\nee', 5, 'reason')
        assert err.message == '\n'.join([
            GRAMMAR_PARSER_ERROR_HEADER_MESSAGE('reason'),
            '',
            'aa',
            'bb',
            'cc',
            ' ^',
        ])

    @pytest.mark.parametrize(
        'input, pos, marker',
        [('some input', 1, ' ^'), ('a', 0, '^'), ('abcd', 2, '  ^')],
    )
    def test_input_parse_error_renders_a_message(self, input, pos, marker):
        err = InputParseError(input, pos)
        assert err.message == '\n'.join([
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            '',
            input,
            marker,
        ])

    @pytest.mark.parametrize(
        'input, expected',
        [
            ('hello', 'hello'),
            ([104, 101, 108, 108, 111], 'hello'),
            (104, 'h'),
            (0x1F600, '😀'),
            ([0x1F600, 0x1F601], '😀😁'),
        ],
    )
    def test_get_input_as_string(self, input, expected):
        assert get_input_as_string(input) == expected


class TestParseChar:
    @pytest.mark.parametrize('char, code_point', [('a', ord('a')), ('9', ord('9'))])
    def test_parses_char(self, char, code_point):
        grammar = f'root ::= "{char}" "foo"'
        assert parse_char(grammar, len('root ::= "')) == (code_point, 1)

    @pytest.mark.parametrize(
        'escaped_char, code_point, inc_pos',
        [
            ('\\x2A', 0x2A, 4),
            ('\\u006F', 0x6F, 6),
            ('\\U0001F4A9', 128169, 10),
            ('\\t', ord('\t'), 2),
            ('\\n', ord('\n'), 2),
            ('\\r', ord('\r'), 2),
            ('\\"', ord('"'), 2),
            ('\\[', ord('['), 2),
            ('\\]', ord(']'), 2),
            ('\\\\', ord('\\'), 2),
        ],
    )
    def test_parses_escaped_char(self, escaped_char, code_point, inc_pos):
        grammar = f'root ::= "{escaped_char}" "foo"'
        assert parse_char(grammar, len('root ::= "')) == (code_point, inc_pos)

    def test_it_throws_on_invalid_input(self):
        with pytest.raises(GrammarParseError):
            parse_char('', 0)
        with pytest.raises(GrammarParseError):
            parse_char('a', 1)


class TestParseName:
    @pytest.mark.parametrize(
        'src', ['v', 'valid', 'valid-name', 'valid-name-foo', 'validName', 'validName-foo']
    )
    def test_valid_name(self, src):
        assert parse_name(src, 0) == src

    @pytest.mark.parametrize(
        'src, position, expectation',
        [
            ('123valid', 3, 'valid'),
            ('123valid-name', 3, 'valid-name'),
            ('123valid _Name', 3, 'valid'),
            ('123valid\n_Name', 3, 'valid'),
            ('123valid\t_Name', 3, 'valid'),
            ('123valid\r_Name', 3, 'valid'),
        ],
    )
    def test_valid_name_at_non_zero_position(self, src, position, expectation):
        assert parse_name(src, position) == expectation

    @pytest.mark.parametrize(
        'src, error',
        [
            ('123', GrammarParseError('123', 0, PARSE_NAME_ERROR)),
            ('valid_name', GrammarParseError('valid_name', 5, GET_INVALID_CHAR_ERROR('_'))),
            ('valid123', GrammarParseError('valid123', 5, GET_INVALID_CHAR_ERROR('1'))),
        ],
    )
    def test_invalid_name(self, src, error):
        with pytest.raises(GrammarParseError) as excinfo:
            parse_name(src, 0)
        assert str(excinfo.value) == str(error)


class TestParseSpace:
    @pytest.mark.parametrize(
        'input, newline_ok, expected',
        [
            ('abcdefghijk', True, 'abcdefghijk'),
            ('   \t   abcdefghijk', True, 'abcdefghijk'),
            ('\n\n\r\n\r\nabcdefghijk', True, 'abcdefghijk'),
            ('\n\n\r\n\r\nabcdefghijk', False, '\n\n\r\n\r\nabcdefghijk'),
            ('  # This is a comment\n\t   abcdefghijk', True, 'abcdefghijk'),
            ('\n\n # This is a comment\n\r\n\r\nabcdefghijk', True, 'abcdefghijk'),
            (
                '\n\n # This is a comment\n\r\n\r\nabcdefghijk',
                False,
                '\n\n # This is a comment\n\r\n\r\nabcdefghijk',
            ),
            ('  \t# Comment\n# Another comment\n\n', True, ''),
            ('', True, ''),
        ],
    )
    def test_parse_space(self, input, newline_ok, expected):
        assert input[parse_space(input, 0, newline_ok):] == expected


class TestIsWordChar:
    @pytest.mark.parametrize('char', ['a', 'z', 'A', 'Z'])
    def test_letters(self, char):
        assert is_word_char(char) is True

    @pytest.mark.parametrize('char', ['0', '9', '-', '@', '_', '?', ' '])
    def test_non_letters(self, char):
        assert is_word_char(char) is False


class TestIsPointInRange:
    @pytest.mark.parametrize(
        'point, expectation',
        [(96, False), (97, True), (98, True), (122, True), (123, False)],
    )
    def test_is_point_in_range(self, point, expectation):
        assert is_point_in_range(point, [97, 122]) is expectation


class TestGetInputAsCodePoints:
    def test_string(self):
        assert get_input_as_code_points('abc') == [97, 98, 99]

    def test_number(self):
        assert get_input_as_code_points(99) == [99]

    def test_array_of_numbers(self):
        assert get_input_as_code_points([99, 100, 101]) == [99, 100, 101]


class TestGetSerializedRuleKey:
    def test_end_rules(self):
        assert get_serialized_rule_key(RuleEnd()) == f'{KEY_TRANSLATION[RuleType.END]}'

    def test_char_rules(self):
        assert (
            get_serialized_rule_key(RuleChar([97]))
            == f'{KEY_TRANSLATION[RuleType.CHAR]}-[97]'
        )

    def test_char_exclude_rules(self):
        assert (
            get_serialized_rule_key(RuleCharExclude([97]))
            == f'{KEY_TRANSLATION[RuleType.CHAR_EXCLUDE]}-[97]'
        )

    def test_reference_rules(self):
        assert get_serialized_rule_key(RuleRef(99)) == '3-99'

    def test_unknown_rule_types(self):
        with pytest.raises(ValueError, match='Unknown rule type'):
            get_serialized_rule_key(object())


class TestGenericSet:
    def test_it_iterates(self):
        set_ = GenericSet(lambda el: el)
        for el in (1, 2, 3):
            set_.add(el)
        assert list(set_) == [1, 2, 3]

    def test_it_skips_duplicates(self):
        set_ = GenericSet(lambda el: el)
        for _ in range(3):
            set_.add(1)
        assert list(set_) == [1]

    def test_it_skips_duplicates_based_on_a_given_key(self):
        set_ = GenericSet(lambda el: el['id'])
        set_.add({'id': 1})
        set_.add({'id': 1, 'foo': 'foo'})
        set_.add({'id': 1, 'bar': 'bar'})
        assert list(set_) == [{'id': 1}]

    def test_can_delete(self):
        set_ = GenericSet(lambda el: el['id'])
        set_.add({'id': 1})
        set_.delete({'id': 1})
        set_.add({'id': 2, 'foo': 'foo'})
        set_.add({'id': 2, 'bar': 'bar'})
        assert list(set_) == [{'id': 2, 'foo': 'foo'}]


class TestIsRange:
    @pytest.mark.parametrize(
        'value, expected',
        [([97, 122], True), ([97], False), ([97, 122, 123], False), (97, False)],
    )
    def test_is_range(self, value, expected):
        assert is_range(value) is expected


class TestParseState:
    def test_it_is_callable(self):
        state = GBNF('root ::= "foo"')
        assert [rule.to_dict() for rule in state('f')] == [{'type': 'char', 'value': [111]}]

    def test_size_and_grammar(self):
        grammar = 'root ::= "foo" | "bar"'
        state = GBNF(grammar)
        assert state.size == 2
        assert len(state) == 2
        assert state.grammar == grammar

    def test_states_are_immutable(self):
        state = GBNF('root ::= "I like green eggs and ham"')
        assert [rule.to_dict() for rule in state] == [{'type': 'char', 'value': [73]}]
        next_state = state.add('I li')
        assert [rule.to_dict() for rule in next_state] == [{'type': 'char', 'value': [107]}]
        # the original state is unchanged
        assert [rule.to_dict() for rule in state] == [{'type': 'char', 'value': [73]}]

    def test_code_point_input(self):
        state = GBNF('root ::= "foo"')
        assert [rule.to_dict() for rule in state.add([ord('f')])] == [
            {'type': 'char', 'value': [111]}
        ]
