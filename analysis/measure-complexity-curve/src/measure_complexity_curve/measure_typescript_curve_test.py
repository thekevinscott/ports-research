from pathlib import Path
from unittest.mock import patch

import pytest

from measure_complexity_curve.measure_typescript_curve import measure_typescript_curve

TARGET = Path("/data/run/ported_implementation")
CORPUS = [
    {"size": 4, "grammar": 'root ::= "a"\n'},
    {"size": 8, "grammar": 'root ::= "b"\n'},
]


@pytest.fixture
def hyperfine_mean_function():
    with patch("measure_complexity_curve.measure_typescript_curve.hyperfine_mean", autospec=True) as m:
        m.side_effect = [0.05, 0.25, 0.45]  # baseline, then one raw mean per corpus entry
        yield m


def describe_measure_typescript_curve():
    def it_returns_one_point_per_corpus_entry(hyperfine_mean_function):
        curve = measure_typescript_curve(target=TARGET, corpus=CORPUS, iterations=10)
        assert [point["size"] for point in curve] == [4, 8]

    def it_subtracts_the_baseline_before_dividing_by_iterations(hyperfine_mean_function):
        curve = measure_typescript_curve(target=TARGET, corpus=CORPUS, iterations=10)
        assert curve[0]["seconds"] == pytest.approx((0.25 - 0.05) / 10)
        assert curve[1]["seconds"] == pytest.approx((0.45 - 0.05) / 10)

    def it_measures_a_zero_iteration_baseline_first(hyperfine_mean_function):
        measure_typescript_curve(target=TARGET, corpus=CORPUS, iterations=10)
        baseline_command = hyperfine_mean_function.call_args_list[0].kwargs["command"]
        assert "--iterations 0" in baseline_command

    def it_runs_through_pnpm_dlx_not_npx(hyperfine_mean_function):
        measure_typescript_curve(target=TARGET, corpus=CORPUS, iterations=10)
        command = hyperfine_mean_function.call_args_list[1].kwargs["command"]
        assert "pnpm dlx" in command
        assert "npx" not in command

    def it_passes_target_and_iterations_to_the_parse_grammar_script(hyperfine_mean_function):
        measure_typescript_curve(target=TARGET, corpus=CORPUS, iterations=10)
        command = hyperfine_mean_function.call_args_list[1].kwargs["command"]
        assert str(TARGET) in command
        assert "--iterations 10" in command
        assert "parse-grammar.ts" in command

    def it_propagates_a_measurement_failure(hyperfine_mean_function):
        hyperfine_mean_function.side_effect = RuntimeError("hyperfine produced no report")
        with pytest.raises(RuntimeError):
            measure_typescript_curve(target=TARGET, corpus=CORPUS, iterations=10)
