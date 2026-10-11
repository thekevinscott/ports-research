from pathlib import Path

from prompt import Prompt

SUITES_PATH = Path(__file__).parent / "prompts" / "suites.txt"
SUITE_PATH = Path(__file__).parent / "prompts" / "suite.txt"
OTHER = {"python": "javascript", "javascript": "python"}
# Where each suite sits in /shared, read from the rules that admit it.
UNIT_TESTS = {
    "python": "python/gbnf/**/*_test.py",
    "javascript": "javascript/src/**/*.test.ts",
}
INTEGRATION_TESTS = {
    "python": "python/tests/generated/",
    "javascript": "javascript/integration-tests/generated/",
}


def suites_information(
    *,
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
) -> Prompt:
    """The suites the condition included, named one per line with where they sit, or nothing.

    A condition with no suite says nothing about tests rather than saying there
    are none: the agent should not be told about a tier it cannot see.
    """
    target_language = OTHER[source_language]
    suites = [
        Prompt(SUITE_PATH, language=language, kind=kind, location=location)
        for included, language, kind, location in (
            (include_unit_tests, source_language, "unit", UNIT_TESTS[source_language]),
            (
                include_source_integration_tests,
                source_language,
                "integration",
                INTEGRATION_TESTS[source_language],
            ),
            (
                include_target_integration_tests,
                target_language,
                "integration",
                INTEGRATION_TESTS[target_language],
            ),
        )
        if included
    ]
    if not suites:
        return Prompt("")
    return Prompt(SUITES_PATH, suites="\n".join(str(suite) for suite in suites))
