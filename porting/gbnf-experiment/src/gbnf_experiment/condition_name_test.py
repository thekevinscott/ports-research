import pytest

from gbnf_experiment.condition_name import condition_name

CONFIG = {
    "source_language": "typescript",
    "include_typescript_tests": False,
    "include_python_tests": False,
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
        assert condition() == "source-typescript_effort-high_model-claude-opus-5"

    def it_names_the_typescript_tests_condition(condition):
        assert condition(include_typescript_tests=True) == (
            "source-typescript_typescript-tests_effort-high_model-claude-opus-5"
        )

    def it_names_the_python_tests_condition(condition):
        assert condition(include_python_tests=True) == (
            "source-typescript_python-tests_effort-high_model-claude-opus-5"
        )

    def it_names_the_both_suites_condition(condition):
        assert condition(
            include_typescript_tests=True, include_python_tests=True
        ) == (
            "source-typescript_typescript-tests_python-tests_effort-high"
            "_model-claude-opus-5"
        )

    def it_distinguishes_the_source_language(condition):
        assert condition(source_language="python") == (
            "source-python_effort-high_model-claude-opus-5"
        )

    def it_labels_the_effort_arm(condition):
        assert condition(effort="low") == (
            "source-typescript_effort-low_model-claude-opus-5"
        )

    def it_labels_the_model_arm(condition):
        assert condition(model="claude-sonnet-4-5") == (
            "source-typescript_effort-high_model-claude-sonnet-4-5"
        )
