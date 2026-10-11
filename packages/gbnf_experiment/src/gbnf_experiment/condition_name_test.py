import pytest

from gbnf_experiment.condition_name import condition_name

CONFIG = {
    "source_language": "javascript",
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}


@pytest.fixture
def condition():
    def build(**kwargs) -> str:
        return condition_name(**{**CONFIG, **kwargs})

    return build


def describe_condition_name():
    def it_names_the_source_only_condition(condition):
        assert condition() == "source-javascript_effort-high_model-claude-opus-5"

    def it_names_the_unit_tests_condition(condition):
        assert condition(include_unit_tests=True) == (
            "source-javascript_unit-tests_effort-high_model-claude-opus-5"
        )

    def it_names_the_source_integration_tests_condition(condition):
        assert condition(include_source_integration_tests=True) == (
            "source-javascript_source-integration-tests_effort-high_model-claude-opus-5"
        )

    def it_names_the_target_integration_tests_condition(condition):
        assert condition(include_target_integration_tests=True) == (
            "source-javascript_target-integration-tests_effort-high_model-claude-opus-5"
        )

    def it_names_every_suite_condition(condition):
        assert condition(
            include_unit_tests=True,
            include_source_integration_tests=True,
            include_target_integration_tests=True,
        ) == (
            "source-javascript_unit-tests_source-integration-tests"
            "_target-integration-tests_effort-high_model-claude-opus-5"
        )

    def it_distinguishes_the_source_language(condition):
        assert condition(source_language="python") == (
            "source-python_effort-high_model-claude-opus-5"
        )

    def it_labels_the_effort_arm(condition):
        assert condition(effort="low") == (
            "source-javascript_effort-low_model-claude-opus-5"
        )

    def it_labels_the_model_arm(condition):
        assert condition(model="claude-sonnet-4-5") == (
            "source-javascript_effort-high_model-claude-sonnet-4-5"
        )
