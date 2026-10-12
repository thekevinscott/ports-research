import pytest

from measure_ast.wasserstein import wasserstein


def describe_wasserstein():
    def it_is_zero_for_identical_samples():
        assert wasserstein([1, 2, 3], [3, 2, 1]) == 0

    def it_is_the_shift_when_every_sample_moves_by_the_same_amount():
        assert wasserstein([1, 2, 3], [2, 3, 4]) == 1

    def it_averages_the_moved_mass_over_equal_sized_samples():
        assert wasserstein([1, 1], [1, 3]) == 1

    def it_compares_samples_of_different_sizes_by_their_distributions():
        assert wasserstein([1], [1, 2]) == 0.5

    def it_is_symmetric():
        assert wasserstein([1, 5, 9], [2, 2]) == wasserstein([2, 2], [1, 5, 9]) == pytest.approx(11 / 3)
