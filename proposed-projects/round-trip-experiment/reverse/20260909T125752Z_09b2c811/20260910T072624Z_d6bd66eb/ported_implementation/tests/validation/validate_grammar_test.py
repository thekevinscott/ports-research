import pytest
from gbnf import GBNF, GrammarParseError


def describe_validate_grammar():
    @pytest.mark.parametrize(
        ("grammar"),
        [
            '''root ::= "foo"''',
            '''root ::= "foo" | "bar"''',
            """root ::= ("foo" | "bar")""",
            """root ::= ("foo" | "bar")?""",
            """root ::= ("foo" | "bar")*""",
            """root ::= ("foo" | "bar")+""",
            """root ::= [a-z]""",
            """root ::= [a-zA-Z]""",
            """root ::= [a-zA-Z0-9]""",
            """root ::= [a-zA-Z0-9]*""",
            """root ::= [a-zA-Z0-9]?""",
            """root ::= [a-z]+""",
            """root ::= [a-zA-Z0-9]+""",
            """root ::= ([a-zA-Z0-9])*""",
            """root ::= ([a-zA-Z0-9])?""",
            """root ::= ([a-zA-Z0-9])+""",
            '''
  root ::= foo
  foo ::= "foo"''',
            """
  root ::= foo
  foo ::= "foo" | "bar" | ([a-z])?
  """,
        ],
    )
    def test_it_parses_a_grammar(grammar):
        GBNF(grammar)

    @pytest.mark.parametrize(
        ("grammar", "error_pos", "error_reason"),
        [
            ("", 0, "No rules were found"),
            ('root = "foo"', 5, "Expecting ::= at 5"),
            (
                """root ::= foo
foo := "foo"
  """,
                17,
                "Expecting ::= at 17",
            ),
            ("root ::= foo", 9, 'Undefined rule identifier "foo"'),
            (
                """root ::= foo
bar ::= "bar"
  """,
                9,
                'Undefined rule identifier "foo"',
            ),
            (
                """root ::= foo
foo ::= baz
bar ::= "bar"
  """,
                21,
                'Undefined rule identifier "baz"',
            ),
            ("root ::= foo ::= bar", 13, "Expecting newline or end at 13"),
            (
                """root ::= ([a-z]
foo ::= "foo"
  """,
                20,
                "Expecting ')' at 20",
            ),
        ],
    )
    def test_it_reports_an_error_for_an_invalid_grammar(
        grammar, error_pos, error_reason
    ):
        expected = GrammarParseError(grammar, error_pos, error_reason)
        with pytest.raises(GrammarParseError) as e:
            graph = GBNF(grammar)
        e = e.value
        assert e == expected
