"""Both languages reachable by name inside a real sandboxed run.

The image once decided one arm of the experiment before the model saw it: a
javascript arm found `vitest` on PATH and ran the reference's own tests as a live
oracle, while a python arm got `command not found` from `python3`, read that as a
dead end and began *fixing* what it judged to be bugs in the reference. Porting
turned into improving, and the cause was the Dockerfile.

Both halves of a language are covered, because either alone leaves the arms
uneven. The run's only egress is the allowlisted API, so nothing downloads.
"""

import pytest

ARITHMETIC = {
    "node": "node -e 'console.log(6 * 7)'",
    "python": "python -c 'print(6 * 7)'",
    "python3": "python3 -c 'print(6 * 7)'",
}

RUNNERS = {"vitest": "vitest --version", "pytest": "pytest --version"}


@pytest.fixture(scope="module")
def reported(sandbox) -> dict[str, str]:
    return sandbox({**ARITHMETIC, **RUNNERS}).report


def describe_the_sandbox_image():
    def it_runs_both_languages_interpreters_by_name(reported):
        assert {name: reported[name] for name in ARITHMETIC} == dict.fromkeys(ARITHMETIC, "42")

    def it_runs_both_languages_test_runners_by_name(reported):
        assert reported["vitest"].startswith("vitest/2.1.3")
        assert reported["pytest"].startswith("pytest 9.1.1")
