from unittest.mock import patch

import pytest

from .compose import compose


@pytest.fixture
def filters(tmp_path):
    for name in ("a", "b"):
        (tmp_path / "python").mkdir(exist_ok=True)
        (tmp_path / "python" / f"{name}.rules").write_text(f"+ {name}\n")
    with patch("gbnf_experiment.prepare_filesystem.assemble_whitelist.compose.FILTERS", tmp_path):
        yield tmp_path


def describe_compose():
    def it_concatenates_the_named_rule_files_in_order(filters):
        assert compose("python", ["b", "a"]) == "+ b\n+ a\n"

    def it_returns_nothing_for_no_names(filters):
        assert compose("python", []) == ""

    def describe_the_real_rule_files():
        @pytest.mark.parametrize("language", ["python", "javascript"])
        def it_has_source_unit_tests_and_integration_tests(language):
            assert compose(language, ["source", "unit-tests", "integration-tests"])
