import pytest

from measure_transcript.command_word import command_word


def describe_command_word():
    @pytest.mark.parametrize(
        ("words", "expected"),
        [
            (["pytest"], 0),
            (["FOO=1", "BAR=2", "pytest"], 2),
            (["env", "A=1", "x"], 2),
            (["timeout", "600", "pytest"], 2),
            (["timeout", "-s", "KILL", "60s", "x"], 4),
            (["time", "x"], 1),
            (["uv", "run", "pytest"], 2),
            (["uv", "run", "--offline", "--with", "pytest", "python", "x.py"], 5),
            (["npx", "tsx", "a.ts"], 0),
            ([], 0),
        ],
    )
    def it_skips_environment_and_wrapper_prefixes(words, expected):
        assert command_word(words) == expected
