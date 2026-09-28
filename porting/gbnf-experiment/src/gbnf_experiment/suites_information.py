from pathlib import Path

from porting_harness.prompt import Prompt

SUITES_PATH = Path(__file__).parent / "suites.txt"
SUITE_PATH = Path(__file__).parent / "suite.txt"


def suites_information(*, include_javascript_tests: bool, include_python_tests: bool) -> Prompt:
    """The suites the condition mounted, named one per line, or nothing at all.

    A condition with no suite says nothing about tests rather than saying there
    are none: the agent should not be told about a tier it cannot see.
    """
    suites = [
        Prompt(SUITE_PATH, language=language)
        for language, included in (
            ("javascript", include_javascript_tests),
            ("python", include_python_tests),
        )
        if included
    ]
    if not suites:
        return Prompt("")
    return Prompt(SUITES_PATH, suites="\n".join(str(suite) for suite in suites))
