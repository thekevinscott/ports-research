from unittest.mock import patch

import pytest
from hypothesis import strategies as st

from exercise_api.generate_cases import generate_cases


@pytest.fixture
def case_strategy_function():
    with patch("exercise_api.generate_cases.case_strategy", autospec=True) as m:
        m.return_value = st.fixed_dictionaries({"grammar": st.sampled_from(["a", "b", "c", "d", "e", "f"]), "input": st.text(max_size=3)})
        yield m


def describe_generate_cases():
    def it_returns_exactly_count_cases(case_strategy_function):
        assert len(generate_cases(seed=0, count=25)) == 25

    def it_is_deterministic_for_a_seed(case_strategy_function):
        assert generate_cases(seed=3, count=20) == generate_cases(seed=3, count=20)

    def it_varies_with_the_seed(case_strategy_function):
        assert generate_cases(seed=1, count=20) != generate_cases(seed=2, count=20)

    def it_never_repeats_a_case(case_strategy_function):
        cases = generate_cases(seed=0, count=30)
        assert len({(c["grammar"], c["input"]) for c in cases}) == 30
