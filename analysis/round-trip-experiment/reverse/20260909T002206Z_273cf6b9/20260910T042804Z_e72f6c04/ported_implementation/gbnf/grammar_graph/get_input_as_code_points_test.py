from .get_input_as_code_points import get_input_as_code_points


def test_it_returns_code_points_for_a_string():
    assert get_input_as_code_points("abc") == [97, 98, 99]


def test_it_returns_code_points_for_a_number():
    assert get_input_as_code_points(99) == [99]


def test_it_returns_code_points_for_a_list_of_numbers():
    assert get_input_as_code_points([99, 100, 101]) == [99, 100, 101]
