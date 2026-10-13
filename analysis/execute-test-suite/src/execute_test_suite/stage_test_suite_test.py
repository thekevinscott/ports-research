import pytest

from execute_test_suite.stage_test_suite import stage_test_suite

REFERENCE_FILES = {
    "python": {
        "gbnf/parse_test.py": "# reference unit",
        "gbnf/rules/rule_test.py": "# reference unit",
        "gbnf/parse.py": "# reference source",
        "tests/generated/iteration/iteration_test.py": "# reference integration",
    },
    "javascript": {
        "src/parse.test.ts": "// reference unit",
        "src/parse.ts": "// reference source",
        "integration-tests/generated/iteration/iteration.test.ts": "// reference integration",
        "integration-tests/generated/validation/validate.test.ts": "// reference integration",
    },
}


@pytest.fixture
def test_suite_directory(tmp_path):
    def build(tree):
        directory = tmp_path / "prepared" / tree
        for relative, text in REFERENCE_FILES[tree].items():
            (directory / relative).parent.mkdir(parents=True, exist_ok=True)
            (directory / relative).write_text(text)
        return directory

    return build


@pytest.fixture
def target(tmp_path):
    directory = tmp_path / "port"
    (directory / "gbnf").mkdir(parents=True)
    (directory / "gbnf" / "parse.py").write_text("# port source")
    (directory / "gbnf" / "parse_test.py").write_text("# port's own copy")
    return directory


def stage(language, suite, test_suite_directory, target, tmp_path):
    return stage_test_suite(
        language=language,
        suite=suite,
        test_suite_directory=test_suite_directory,
        target=target,
        destination=tmp_path / "staged",
    )


def describe_stage_test_suite():
    def it_overlays_the_reference_unit_tests_onto_a_copy_of_the_target(
        test_suite_directory, target, tmp_path
    ):
        staged = stage("python", "unit", test_suite_directory("python"), target, tmp_path)
        destination = tmp_path / "staged"
        assert staged == [destination / "gbnf/parse_test.py", destination / "gbnf/rules/rule_test.py"]
        assert (destination / "gbnf/parse.py").read_text() == "# port source"
        assert (destination / "gbnf/parse_test.py").read_text() == "# reference unit"

    def it_overlays_only_the_generated_integration_tests_for_integration(
        test_suite_directory, target, tmp_path
    ):
        staged = stage("python", "integration", test_suite_directory("python"), target, tmp_path)
        destination = tmp_path / "staged"
        assert staged == [destination / "tests/generated/iteration/iteration_test.py"]
        assert (destination / "gbnf/parse_test.py").read_text() == "# port's own copy"

    def it_never_writes_into_the_target(test_suite_directory, target, tmp_path):
        before = {p: p.read_bytes() for p in target.rglob("*") if p.is_file()}
        stage("python", "unit", test_suite_directory("python"), target, tmp_path)
        assert {p: p.read_bytes() for p in target.rglob("*") if p.is_file()} == before

    def it_overlays_the_javascript_unit_tests_for_typescript(
        test_suite_directory, target, tmp_path
    ):
        staged = stage("typescript", "unit", test_suite_directory("javascript"), target, tmp_path)
        assert staged == [tmp_path / "staged" / "src/parse.test.ts"]

    def it_overlays_every_javascript_integration_test(test_suite_directory, target, tmp_path):
        staged = stage(
            "javascript", "integration", test_suite_directory("javascript"), target, tmp_path
        )
        destination = tmp_path / "staged" / "integration-tests/generated"
        assert staged == [
            destination / "iteration/iteration.test.ts",
            destination / "validation/validate.test.ts",
        ]
