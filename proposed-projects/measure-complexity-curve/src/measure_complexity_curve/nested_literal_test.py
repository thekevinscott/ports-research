import random

from measure_complexity_curve.nested_literal import nested_literal


def describe_nested_literal():
    def it_is_a_quoted_terminal_at_depth_zero():
        assert nested_literal(random.Random(0), 0) == '"mynb"'

    def it_wraps_the_terminal_in_one_group_per_level_of_depth():
        token = nested_literal(random.Random(0), 3)
        assert token.count("(") == 3
        assert token.count(")") == 3

    def it_only_uses_lowercase_ascii_letters_in_the_terminal():
        token = nested_literal(random.Random(1), 2)
        letters = token.split('"')[1]
        assert letters.isalpha()
        assert letters.islower()

    def it_is_deterministic_for_a_given_seed():
        assert nested_literal(random.Random(7), 4) == nested_literal(random.Random(7), 4)

    def it_ends_each_group_with_a_repetition_operator():
        token = nested_literal(random.Random(2), 1)
        assert token[-1] in "?*+"
