import pytest

from measure_transcript.classify_path import classify_path


def describe_classify_path():
    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("/input/python/gbnf/graph.py", "source"),
            ("/input/python", "source"),
            ("/input/python/gbnf/graph_test.py", "source_tests"),
            ("/input/python/tests/generated/iteration/iteration_test.py", "source_tests"),
            ("/input/python/tests", "source_tests"),
            ("/input/javascript/integration-tests/generated/x.test.ts", "target_tests"),
            ("/input/javascript/src/a.test.ts", "target_tests"),
            ("/input/javascript/package.json", "other"),
            ("/input", "other"),
            ("/target/src/index.ts", "port"),
            ("/target", "port"),
            ("/tmp/x.py", "other"),
            ("/targets/x", "other"),
            (None, "other"),
        ],
    )
    def it_classifies_a_python_source_layout(path, expected):
        assert classify_path(path, "python", {}) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("/input/javascript/src/gbnf.ts", "source"),
            ("/input/javascript/src/gbnf.test.ts", "source_tests"),
            ("/input/javascript/integration-tests/generated/v.test.ts", "source_tests"),
            ("/input/python/tests/generated/v_test.py", "target_tests"),
            ("/input/python/pyproject.toml", "other"),
        ],
    )
    def it_classifies_a_javascript_source_layout(path, expected):
        assert classify_path(path, "javascript", {}) == expected

    def it_classifies_a_copy_by_where_it_came_from():
        copies = {"/target/tests/generated": "/input/javascript/integration-tests/generated"}
        assert classify_path("/target/tests/generated/x.test.ts", "python", copies) == "target_tests"
        assert classify_path("/target/tests/own.test.ts", "python", copies) == "port"
