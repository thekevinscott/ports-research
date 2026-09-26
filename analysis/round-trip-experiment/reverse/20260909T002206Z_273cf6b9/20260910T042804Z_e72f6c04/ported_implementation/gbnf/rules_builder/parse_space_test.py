from .parse_space import parse_space


def test_return_input_string_when_no_whitespace_or_comments():
    input = "abcdefghijk"
    assert input[parse_space(input, 0, True) :] == input


def test_skip_leading_spaces_and_tabs():
    input = "   \t   abcdefghijk"
    assert input[parse_space(input, 0, True) :] == "abcdefghijk"


def test_skip_leading_newline_characters_when_newline_ok_true():
    input = "\n\n\r\n\r\nabcdefghijk"
    assert input[parse_space(input, 0, True) :] == "abcdefghijk"


def test_not_skip_leading_newline_characters_when_newline_ok_false():
    input = "\n\n\r\n\r\nabcdefghijk"
    assert input[parse_space(input, 0, False) :] == "\n\n\r\n\r\nabcdefghijk"


def test_skip_comments_and_leading_spaces():
    input = "  # This is a comment\n\t   abcdefghijk"
    assert input[parse_space(input, 0, True) :] == "abcdefghijk"


def test_skip_comments_and_leading_newline_characters_when_newline_ok_true():
    input = "\n\n # This is a comment\n\r\n\r\nabcdefghijk"
    assert input[parse_space(input, 0, True) :] == "abcdefghijk"


def test_skip_comments_and_leading_newline_characters_when_newline_ok_false():
    input = "\n\n # This is a comment\n\r\n\r\nabcdefghijk"
    assert (
        input[parse_space(input, 0, False) :]
        == "\n\n # This is a comment\n\r\n\r\nabcdefghijk"
    )


def test_return_empty_string_if_input_all_whitespace_and_comments():
    input = "  \t# Comment\n# Another comment\n\n"
    assert input[parse_space(input, 0, True) :] == ""


def test_return_empty_string_for_empty_input_string():
    input = ""
    assert input[parse_space(input, 0, True) :] == ""
