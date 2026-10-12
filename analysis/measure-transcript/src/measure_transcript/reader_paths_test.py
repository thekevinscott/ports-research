import pytest

from measure_transcript.reader_paths import reader_paths


def describe_reader_paths():
    @pytest.mark.parametrize(
        ("program", "args", "expected"),
        [
            ("cat", ["a", "b"], ["a", "b"]),
            ("head", ["-20", "a"], ["a"]),
            ("tail", ["-80", "a"], ["a"]),
            ("less", ["a"], ["a"]),
            ("grep", ["-rn", "pattern", "a"], ["a"]),
            ("sed", ["-n", "1,5p", "a"], ["a"]),
            ("awk", ["/def/", "a"], ["a"]),
        ],
    )
    def it_returns_the_file_operands_of_a_reading_command(program, args, expected):
        assert reader_paths(program, args) == expected

    @pytest.mark.parametrize(
        ("program", "args", "expected"),
        [
            ("head", ["-n", "5", "a"], ["a"]),
            ("tail", ["-n", "+2", "a"], ["a"]),
            ("grep", ["-A", "3", "-B", "2", "-m", "1", "pattern", "a"], ["a"]),
            ("grep", ["-v", "-e", "x", "-e", "y", "a"], ["a"]),
            ("sed", ["-n", "-e", "1p", "a"], ["a"]),
            ("awk", ["-F", ":", "-v", "n=1", "{print}", "a"], ["a"]),
        ],
    )
    def it_skips_option_values_and_a_script_given_by_option(program, args, expected):
        assert reader_paths(program, args) == expected

    def it_returns_none_for_a_command_that_reads_no_file():
        assert reader_paths("ls", ["a"]) is None
        assert reader_paths("sed", ["-i", "s/a/b/", "a"]) is None
