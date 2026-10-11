import pytest

from gbnf_experiment.suites_information import suites_information

NONE = {
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
}
ALL = {name: True for name in NONE}


def rendered(source_language="python", **flags) -> str:
    return str(suites_information(source_language=source_language, **{**NONE, **flags}))


def describe_suites_information():
    def describe_when_no_suite_was_included():
        @pytest.mark.parametrize("source_language", ["python", "javascript"])
        def it_says_nothing_at_all(source_language):
            assert rendered(source_language) == ""

    def describe_the_unit_tests():
        def it_places_python_s_beside_the_modules_they_test():
            assert "- python unit tests: python/gbnf/**/*_test.py" in rendered(
                "python", include_unit_tests=True
            )

        def it_places_javascript_s_beside_the_modules_they_test():
            assert "- javascript unit tests: javascript/src/**/*.test.ts" in rendered(
                "javascript", include_unit_tests=True
            )

    def describe_the_source_integration_tests():
        def it_places_python_s_where_its_generator_writes_them():
            assert "- python integration tests: python/tests/generated/" in rendered(
                "python", include_source_integration_tests=True
            )

        def it_places_javascript_s_where_its_generator_writes_them():
            assert (
                "- javascript integration tests: javascript/integration-tests/generated/"
                in rendered("javascript", include_source_integration_tests=True)
            )

    def describe_the_target_integration_tests():
        def it_names_the_other_language_s_suite():
            assert (
                "- javascript integration tests: javascript/integration-tests/generated/"
                in rendered("python", include_target_integration_tests=True)
            )

        def it_names_nothing_of_the_source_language():
            assert "python" not in rendered("python", include_target_integration_tests=True)

    def describe_when_every_suite_was_included():
        def it_gives_them_a_line_each_source_first():
            assert rendered("python", **ALL).endswith(
                "- python unit tests: python/gbnf/**/*_test.py\n"
                "- python integration tests: python/tests/generated/\n"
                "- javascript integration tests: javascript/integration-tests/generated/\n"
            )

    def describe_the_text_it_renders():
        def it_leaves_no_placeholder_behind():
            assert "{" not in rendered(**ALL)

        def it_says_nothing_about_iterating_to_green():
            assert "green" not in rendered(**ALL)
            assert "iterate" not in rendered(**ALL)
