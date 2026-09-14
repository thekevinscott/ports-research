from pathlib import Path
from unittest.mock import patch

import pytest

from measure_complexity_curve.run_complexity_curve import run_complexity_curve

TARGET = Path("/data/run/ported_implementation")


def call(**overrides):
    return run_complexity_curve(
        **{
            "language": "python",
            "target": TARGET,
            "max_size": 128,
            "steps": 6,
            "nesting_depth": 1,
            "alternation_width": 2,
            "iterations": 10,
            "seed": 0,
            **overrides,
        }
    )


@pytest.fixture
def curve():
    return [
        {"size": 4, "seconds": 0.001},
        {"size": 8, "seconds": 0.002},
        {"size": 16, "seconds": 0.004},
        {"size": 32, "seconds": 0.008},
        {"size": 64, "seconds": 0.016},
        {"size": 128, "seconds": 0.032},
    ]


@pytest.fixture
def measure_python_curve_function(curve):
    with patch("measure_complexity_curve.run_complexity_curve.measure_python_curve", autospec=True) as m:
        m.return_value = curve
        yield m


@pytest.fixture
def measure_typescript_curve_function(curve):
    with patch("measure_complexity_curve.run_complexity_curve.measure_typescript_curve", autospec=True) as m:
        m.return_value = curve
        yield m


def describe_run_complexity_curve():
    def it_measures_python_targets_with_the_python_curve_driver(
        measure_python_curve_function, measure_typescript_curve_function
    ):
        call(language="python")
        measure_python_curve_function.assert_called_once()
        measure_typescript_curve_function.assert_not_called()

    def it_measures_typescript_targets_with_the_typescript_curve_driver(
        measure_python_curve_function, measure_typescript_curve_function
    ):
        call(language="typescript")
        measure_typescript_curve_function.assert_called_once()
        measure_python_curve_function.assert_not_called()

    def it_passes_the_generated_corpus_and_iterations_to_the_driver(measure_python_curve_function):
        call(max_size=128, steps=6, iterations=10)
        kwargs = measure_python_curve_function.call_args.kwargs
        assert kwargs["target"] == TARGET
        assert kwargs["iterations"] == 10
        assert [entry["size"] for entry in kwargs["corpus"]] == [4, 8, 16, 32, 64, 128]

    def it_reports_the_language_and_target(measure_python_curve_function):
        report = call()
        assert report["language"] == "python"
        assert report["target"] == str(TARGET)

    def it_reports_the_raw_curve(measure_python_curve_function, curve):
        report = call()
        assert report["curve"] == curve

    def it_reports_a_log_log_slope_of_one_for_a_linear_curve(measure_python_curve_function):
        report = call()
        assert report["log_log_slope"] == pytest.approx(1.0)

    def it_reports_a_steeper_slope_for_a_quadratic_curve(measure_python_curve_function):
        quadratic = [{"size": size, "seconds": (size / 4) ** 2 * 0.001} for size in (4, 8, 16, 32, 64, 128)]
        measure_python_curve_function.return_value = quadratic
        report = call()
        assert report["log_log_slope"] == pytest.approx(2.0)
