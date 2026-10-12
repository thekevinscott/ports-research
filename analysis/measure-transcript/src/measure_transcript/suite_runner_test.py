import pytest

from measure_transcript.suite_runner import suite_runner


def describe_suite_runner():
    @pytest.mark.parametrize(
        ("words", "paths"),
        [
            (["pytest", "-q", "tests"], ["tests"]),
            (["uv", "run", "--offline", "pytest", "-q", "-p", "no:cacheprovider", "tests/generated"], ["tests/generated"]),
            (["python3", "-m", "pytest", "x_test.py"], ["x_test.py"]),
            (["timeout", "600", "pytest", "-q"], []),
            (["vitest", "run", "src/rules-builder"], ["src/rules-builder"]),
            (["vitest", "--config", "./vitest.config.unit.ts", "run"], []),
            (["npx", "vitest", "run"], []),
            (["pnpm", "exec", "vitest", "run", "a.test.ts"], ["a.test.ts"]),
            (["CI=1", "jest", "src"], ["src"]),
            (["npm", "test"], []),
            (["pnpm", "run", "test:unit"], []),
            (["pnpm", "test"], []),
            (["just", "test-unit"], []),
            (["node", "--test", "x.test.mjs"], ["x.test.mjs"]),
        ],
    )
    def it_finds_a_suite_run_and_its_path_arguments(words, paths):
        assert suite_runner(words) == paths

    @pytest.mark.parametrize(
        "words",
        [
            ["which", "pytest"],
            ["pytest", "--version"],
            ["pytest", "--collect-only", "-q"],
            ["vitest", "--version"],
            ["node", "x.js"],
            ["npm", "install"],
            ["cat", "pytest.ini"],
            ["just", "lint"],
            [],
        ],
    )
    def it_returns_none_for_anything_else(words):
        assert suite_runner(words) is None
