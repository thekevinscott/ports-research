import pytest

from measure_complexity_curve.log_log_slope import log_log_slope


def describe_log_log_slope():
    def it_is_one_for_a_linear_relationship():
        slope = log_log_slope(sizes=[1, 10, 100], seconds=[1, 10, 100])
        assert slope == pytest.approx(1.0)

    def it_is_two_for_a_quadratic_relationship():
        slope = log_log_slope(sizes=[1, 10, 100], seconds=[1, 100, 10000])
        assert slope == pytest.approx(2.0)

    def it_is_zero_for_a_constant_relationship():
        slope = log_log_slope(sizes=[1, 10, 100], seconds=[5, 5, 5])
        assert slope == pytest.approx(0.0)

    def it_rejects_fewer_than_two_points():
        with pytest.raises(ValueError):
            log_log_slope(sizes=[10], seconds=[1])

    def it_rejects_mismatched_lengths():
        with pytest.raises(ValueError):
            log_log_slope(sizes=[1, 10], seconds=[1])
