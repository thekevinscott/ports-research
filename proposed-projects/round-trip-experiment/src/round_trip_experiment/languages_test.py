from round_trip_experiment.languages import LANGUAGES, PYTHON, TYPESCRIPT


def describe_languages():
    def it_maps_both_language_names():
        assert LANGUAGES == {"python": PYTHON, "typescript": TYPESCRIPT}

    def it_parses_python_from_py_files():
        assert set(PYTHON.parsers) == {".py"}

    def it_parses_typescript_from_ts_and_tsx_files():
        assert set(TYPESCRIPT.parsers) == {".ts", ".tsx"}

    def it_treats_the_python_identifier_node_as_an_identifier():
        assert PYTHON.identifiers == frozenset({"identifier"})

    def it_treats_every_typescript_identifier_flavour_as_an_identifier():
        assert TYPESCRIPT.identifiers >= {
            "identifier",
            "property_identifier",
            "type_identifier",
            "shorthand_property_identifier",
            "shorthand_property_identifier_pattern",
            "private_property_identifier",
        }

    def it_does_not_treat_typescript_keywords_or_literals_as_identifiers():
        assert not TYPESCRIPT.identifiers & {"string", "number", "this", "true", "false"}
