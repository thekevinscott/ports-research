import pytest

from measure_transcript.is_test_path import is_test_path


def describe_is_test_path():
    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("/target/src/a.test.ts", True),
            ("/target/src/a.spec.ts", True),
            ("/target/gbnf/graph_test.py", True),
            ("/target/test_graph.py", True),
            ("/target/tests/conftest.py", True),
            ("/target/integration-tests/x.ts", True),
            ("/target/__tests__/a.js", True),
            ("/target/src/a.ts", False),
            ("/target/tests/fixtures/data.json", False),
            ("/target/gbnf/testing.py", False),
        ],
    )
    def it_recognizes_test_files(path, expected):
        assert is_test_path(path) is expected
