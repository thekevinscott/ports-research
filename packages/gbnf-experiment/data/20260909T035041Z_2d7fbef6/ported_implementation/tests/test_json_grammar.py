"""End-to-end tests driving a realistic JSON grammar."""

import pytest

from gbnf import GBNF, InputParseError, RuleType

JSON_GRAMMAR = r"""root   ::= object
value  ::= object | array | string | number | ("true" | "false" | "null") ws

object ::=
  "{" ws (
            string ":" ws value
    ("," ws string ":" ws value)*
  )? "}" ws

array  ::=
  "[" ws (
            value
    ("," ws value)*
  )? "]" ws

string ::=
  "\"" (
    [^"\\] |
    "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
  )* "\"" ws

number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws

ws ::= ([ \t\n] ws)?
"""


def feed(document, chunk_size=None):
    """Feed ``document`` through the grammar, one chunk at a time."""
    state = GBNF(JSON_GRAMMAR)
    if chunk_size is None:
        return state.add(document)
    for i in range(0, len(document), chunk_size):
        state = state.add(document[i : i + chunk_size])
    return state


@pytest.mark.parametrize(
    "document",
    [
        "{}",
        '{"a": 1}',
        '{"a":1,"b":2}',
        '{"a": [1, 2, 3]}',
        '{"a": {"b": {"c": null}}}',
        '{"a": true, "b": false, "c": null}',
        '{"a": -1.5e10}',
        '{"a": "with \\"escapes\\" and \\u00e9"}',
        '{"nested": [{"x": []}, {}]}',
        '{\n  "pretty": [\n    1,\n    2\n  ]\n}',
    ],
)
def test_accepts_valid_json(document):
    feed(document)


@pytest.mark.parametrize("chunk_size", [1, 2, 3, 5])
def test_chunking_does_not_change_the_result(chunk_size):
    document = '{"a": [1, {"b": "c"}], "d": null}'
    assert [r.to_json() for r in feed(document, chunk_size)] == [
        r.to_json() for r in feed(document)
    ]


@pytest.mark.parametrize(
    "document",
    [
        "{,}",
        '{"a" 1}',
        '{"a": 1,,}',
        '{"a": tru3}',
        "{]",
        '{"a": 01}',
    ],
)
def test_rejects_invalid_json(document):
    with pytest.raises(InputParseError):
        feed(document)


@pytest.mark.parametrize(
    "document",
    [
        "{",
        '{"a"',
        '{"a": ',
        '{"a": "unterminated}',
        '{"a": [1,',
        '{"a": tru',
    ],
)
def test_accepts_incomplete_documents_as_prefixes(document):
    # the parser is incremental: an unfinished document is valid, it just cannot end
    state = feed(document)
    assert RuleType.END not in [rule.type for rule in state]


def test_a_complete_document_may_end():
    state = feed('{"a": 1}')
    assert RuleType.END in [rule.type for rule in state]


def test_an_incomplete_document_may_not_end():
    state = feed('{"a":')
    assert RuleType.END not in [rule.type for rule in state]


def test_suggests_a_closing_brace_after_a_value():
    state = feed('{"a": 1')
    suggested = {
        chr(value)
        for rule in state
        if rule.type is RuleType.CHAR
        for value in rule.value
        if isinstance(value, int)
    }
    assert "}" in suggested
    assert "," in suggested


def test_suggests_digits_while_reading_a_number():
    state = feed('{"a": 1')
    ranges = [
        value
        for rule in state
        if rule.type is RuleType.CHAR
        for value in rule.value
        if isinstance(value, list)
    ]
    assert [ord("0"), ord("9")] in ranges
