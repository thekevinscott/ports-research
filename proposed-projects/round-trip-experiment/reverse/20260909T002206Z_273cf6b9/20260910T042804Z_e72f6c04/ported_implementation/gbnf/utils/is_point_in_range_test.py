import pytest

from .is_point_in_range import is_point_in_range


@pytest.mark.parametrize(
    ("point", "given_range", "expectation"),
    [
        (96, [97, 122], False),
        (97, [97, 122], True),
        (98, [97, 122], True),
        (122, [97, 122], True),
        (123, [97, 122], False),
    ],
)
def test_it_checks_if_point_is_in_range(point, given_range, expectation):
    assert is_point_in_range(point, given_range) is expectation
