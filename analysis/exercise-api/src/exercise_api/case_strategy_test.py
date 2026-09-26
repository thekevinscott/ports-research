from hypothesis import given, settings

from exercise_api.case_strategy import case_strategy


def describe_case_strategy():
    @settings(max_examples=200)
    @given(case_strategy())
    def it_yields_a_grammar_and_an_input_string(case):
        assert set(case) == {"grammar", "input"}
        assert isinstance(case["grammar"], str)
        assert isinstance(case["input"], str)

    @settings(max_examples=200)
    @given(case_strategy())
    def it_keeps_inputs_short(case):
        assert len(case["input"]) <= 40
