import shutil
from pathlib import Path

import pytest

from round_trip_experiment.check_staged_derivation import check_staged_derivation

CONDITION = {
    "source_language": "typescript",
    "include_typescript_tests": True,
    "include_python_tests": True,
    "effort": "high",
    "model": "claude-opus-5",
}


@pytest.fixture
def staged(tmp_path: Path) -> Path:
    directory = tmp_path / "staging" / "20260909T001426Z_1c28aa33" / "390bf534c55d496b"
    source = directory / "source" / "typescript"
    source.mkdir(parents=True)
    (source / "index.ts").write_text("export const f = () => 1;\n")
    for language in ("python", "typescript"):
        suite = directory / "tests" / language
        suite.mkdir(parents=True)
        (suite / "keep.txt").write_text("suite\n")
    return directory


def describe_check_staged_derivation():
    def it_accepts_a_complete_staged_derivation(staged):
        assert check_staged_derivation(staged, condition=CONDITION) is None

    def it_refuses_a_source_tree_for_another_language(staged):
        with pytest.raises(ValueError, match="source/python"):
            check_staged_derivation(staged, condition={**CONDITION, "source_language": "python"})

    def it_refuses_an_empty_source_tree(staged):
        (staged / "source" / "typescript" / "index.ts").unlink()
        with pytest.raises(ValueError, match="source/typescript"):
            check_staged_derivation(staged, condition=CONDITION)

    def it_refuses_a_missing_test_suite(staged):
        shutil.rmtree(staged / "tests" / "python")
        with pytest.raises(ValueError, match="tests/python"):
            check_staged_derivation(staged, condition=CONDITION)

    def it_refuses_a_dangling_test_suite_link(tmp_path, staged):
        shutil.rmtree(staged / "tests")
        (staged / "tests").symlink_to(tmp_path / "nowhere" / "tests")
        with pytest.raises(ValueError, match="tests/python"):
            check_staged_derivation(staged, condition=CONDITION)

    def it_refuses_a_staged_derivation_that_was_never_written(tmp_path):
        with pytest.raises(ValueError):
            check_staged_derivation(tmp_path / "nowhere", condition=CONDITION)

    def it_requires_only_the_suites_the_condition_turns_on(staged):
        shutil.rmtree(staged / "tests" / "python")
        assert check_staged_derivation(staged, condition={**CONDITION, "include_python_tests": False}) is None
