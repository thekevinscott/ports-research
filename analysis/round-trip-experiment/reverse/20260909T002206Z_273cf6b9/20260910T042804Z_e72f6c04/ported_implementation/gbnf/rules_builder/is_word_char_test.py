from .is_word_char import is_word_char


def test_should_return_true_for_lowercase_letters():
    assert is_word_char("a") is True
    assert is_word_char("z") is True


def test_should_return_true_for_uppercase_letters():
    assert is_word_char("A") is True
    assert is_word_char("Z") is True


def test_should_return_false_for_digits():
    assert is_word_char("0") is False
    assert is_word_char("9") is False


def test_should_return_false_for_non_word_characters():
    assert is_word_char("-") is False
    assert is_word_char("@") is False
    assert is_word_char("_") is False
    assert is_word_char("?") is False
    assert is_word_char(" ") is False
