import pytest

from two_number_adder import add


def describe_add():
    def it_sums_two_positive_numbers():
        assert add(2, 3) == 5

    def it_sums_a_negative_and_a_positive():
        assert add(-4, 4) == 0

    def it_sums_fractions():
        assert add(0.5, 0.25) == 0.75

    def it_rejects_a_value_that_is_not_a_number():
        with pytest.raises(TypeError):
            add("2", 3)

    def it_rejects_a_value_that_is_not_finite():
        with pytest.raises(TypeError):
            add(float("inf"), 1)
