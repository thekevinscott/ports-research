from .input_parse_error import INPUT_PARSER_ERROR_HEADER_MESSAGE, InputParseError


def test_it_renders_a_message():
    input = "some input"
    pos = 1
    err = InputParseError(input, pos)
    assert err.args[0] == "\n".join(
        [
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            "",
            input,
            " ^",
        ]
    )


def test_it_renders_a_message_for_a_code_point():
    err = InputParseError("a", 0)
    assert err.args[0] == "\n".join(
        [
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            "",
            "a",
            "^",
        ]
    )


def test_it_renders_a_message_for_code_points():
    err = InputParseError("abcd", 2)
    assert err.args[0] == "\n".join(
        [
            INPUT_PARSER_ERROR_HEADER_MESSAGE,
            "",
            "abcd",
            "  ^",
        ]
    )
