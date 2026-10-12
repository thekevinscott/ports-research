import pytest

from measure_transcript.segment_runtime import segment_runtime


def describe_segment_runtime():
    @pytest.mark.parametrize(
        ("words", "expected"),
        [
            (["python3", "x.py"], "python"),
            (["/usr/bin/python3.14", "-"], "python"),
            (["uv", "run", "python", "x.py"], "python"),
            (["node", "run.mjs"], "node"),
            (["npx", "tsx", "a.ts"], "node"),
            (["tsx", "a.ts"], "node"),
            (["python3", "--version"], None),
            (["node", "-v"], None),
            (["pytest"], None),
            (["cat", "x.py"], None),
            ([], None),
        ],
    )
    def it_names_the_runtime_a_segment_invokes(words, expected):
        assert segment_runtime(words) == expected
