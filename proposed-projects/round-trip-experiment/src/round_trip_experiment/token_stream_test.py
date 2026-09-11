from round_trip_experiment.languages import PYTHON, TYPESCRIPT
from round_trip_experiment.token_stream import PLACEHOLDER, token_stream

PYTHON_SOURCE = b'def f(a):\n    # note\n    return a.b + 1.5 + "x"\n'
TYPESCRIPT_SOURCE = b"const s: Foo = { k: a, b }; // note\nlet n = 2 + `t${x}`;\n"


def tokens(spec, suffix, source, abstract_identifiers):
    return token_stream(source, spec.parsers[suffix], spec, abstract_identifiers=abstract_identifiers)


def describe_token_stream():
    def it_yields_every_leaf_token_in_source_order():
        assert tokens(PYTHON, ".py", b"x = 1\n", abstract_identifiers=False) == ["x", "=", "1"]

    def it_replaces_identifiers_with_the_placeholder():
        assert tokens(PYTHON, ".py", PYTHON_SOURCE, abstract_identifiers=True) == [
            "def", PLACEHOLDER, "(", PLACEHOLDER, ")", ":",
            "return", PLACEHOLDER, ".", PLACEHOLDER, "+", "1.5", "+", '"', "x", '"',
        ]

    def it_keeps_identifiers_when_not_abstracting():
        assert tokens(PYTHON, ".py", PYTHON_SOURCE, abstract_identifiers=False) == [
            "def", "f", "(", "a", ")", ":",
            "return", "a", ".", "b", "+", "1.5", "+", '"', "x", '"',
        ]

    def it_drops_comments():
        assert "# note" not in tokens(PYTHON, ".py", PYTHON_SOURCE, abstract_identifiers=False)
        assert "// note" not in tokens(TYPESCRIPT, ".ts", TYPESCRIPT_SOURCE, abstract_identifiers=False)

    def it_abstracts_property_type_and_shorthand_identifiers_in_typescript():
        assert tokens(TYPESCRIPT, ".ts", TYPESCRIPT_SOURCE, abstract_identifiers=True) == [
            "const", PLACEHOLDER, ":", PLACEHOLDER, "=", "{", PLACEHOLDER, ":", PLACEHOLDER, ",", PLACEHOLDER, "}", ";",
            "let", PLACEHOLDER, "=", "2", "+", "`", "t", "${", PLACEHOLDER, "}", "`", ";",
        ]

    def it_keeps_typescript_predefined_types_as_tokens():
        assert tokens(TYPESCRIPT, ".ts", b"let a: string;\n", abstract_identifiers=True) == [
            "let", PLACEHOLDER, ":", "string", ";",
        ]

    def it_parses_tsx_with_the_tsx_grammar():
        assert "<" in tokens(TYPESCRIPT, ".tsx", b"const x = <div />;\n", abstract_identifiers=True)

    def it_returns_nothing_for_an_empty_file():
        assert tokens(PYTHON, ".py", b"", abstract_identifiers=True) == []
