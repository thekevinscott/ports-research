import pytest

from gbnf_experiment.condition_name import condition_name

CONFIG = {
    "source_language": "typescript",
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}


def describe_condition_name():
    @pytest.mark.parametrize(
        ("unit", "source_integration", "target_integration", "suites"),
        [
            (False, False, False, ""),
            (True, False, False, "unit-tests_"),
            (False, True, False, "source-integration-tests_"),
            (False, False, True, "target-integration-tests_"),
            (True, True, False, "unit-tests_source-integration-tests_"),
            (True, False, True, "unit-tests_target-integration-tests_"),
            (False, True, True, "source-integration-tests_target-integration-tests_"),
            (
                True,
                True,
                True,
                "unit-tests_source-integration-tests_target-integration-tests_",
            ),
        ],
        ids=[
            "none",
            "unit",
            "source-integration",
            "target-integration",
            "unit-and-source-integration",
            "unit-and-target-integration",
            "both-integration",
            "all",
        ],
    )
    def it_names_every_suite_that_is_on_in_declaration_order(
        unit, source_integration, target_integration, suites
    ):
        assert condition_name(
            **{
                **CONFIG,
                "include_unit_tests": unit,
                "include_source_integration_tests": source_integration,
                "include_target_integration_tests": target_integration,
            }
        ) == f"source-typescript_{suites}effort-high_model-claude-opus-5"

    def it_distinguishes_the_source_language():
        assert condition_name(**{**CONFIG, "source_language": "python"}) == (
            "source-python_effort-high_model-claude-opus-5"
        )

    def it_labels_the_effort_arm():
        assert condition_name(**{**CONFIG, "effort": "low"}) == (
            "source-typescript_effort-low_model-claude-opus-5"
        )

    def it_labels_the_model_arm():
        assert condition_name(**{**CONFIG, "model": "claude-sonnet-4-5"}) == (
            "source-typescript_effort-high_model-claude-sonnet-4-5"
        )
