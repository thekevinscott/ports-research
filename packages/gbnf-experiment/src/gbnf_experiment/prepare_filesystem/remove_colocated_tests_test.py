import pytest

from gbnf_experiment.prepare_filesystem.remove_colocated_tests import remove_colocated_tests

TREE = {
    "src/gbnf.ts": "export const parse = () => {};\n",
    "src/gbnf.test.ts": "describe('gbnf', () => {});\n",
    "src/utils/errors/input-parse-error.test.ts": "describe('errors', () => {});\n",
    "gbnf/parse.py": "def parse(): ...\n",
    "gbnf/parse_test.py": "def test_parse(): ...\n",
    "gbnf/utils/is_point_in_range_test.py": "def test_range(): ...\n",
    "package.json": '{"name": "gbnf"}\n',
    "pyproject.toml": "[project]\n",
    "tsconfig.test.json": "{}\n",
    "vitest.config.unit.ts": "export default {};\n",
}

COLOCATED_TESTS = [name for name in TREE if name.endswith((".test.ts", "_test.py"))]
SURVIVORS = [name for name in TREE if name not in COLOCATED_TESTS]
LANGUAGES = ("typescript", "python")


@pytest.fixture
def tree(tmp_path):
    for name, text in TREE.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return tmp_path


def relative_files(directory):
    return sorted(
        str(path.relative_to(directory)) for path in directory.rglob("*") if path.is_file()
    )


def describe_remove_colocated_tests():
    def it_removes_a_typescript_colocated_test(tree):
        remove_colocated_tests(directory=tree, languages=LANGUAGES)
        assert not (tree / "src" / "gbnf.test.ts").exists()

    def it_removes_a_python_colocated_test(tree):
        remove_colocated_tests(directory=tree, languages=LANGUAGES)
        assert not (tree / "gbnf" / "parse_test.py").exists()

    def it_reaches_colocated_tests_nested_any_depth(tree):
        remove_colocated_tests(directory=tree, languages=LANGUAGES)
        assert not (tree / "src" / "utils" / "errors" / "input-parse-error.test.ts").exists()
        assert not (tree / "gbnf" / "utils" / "is_point_in_range_test.py").exists()

    def it_removes_both_languages_from_one_tree(tree):
        remove_colocated_tests(directory=tree, languages=LANGUAGES)
        assert [name for name in relative_files(tree) if name in COLOCATED_TESTS] == []

    def it_removes_only_the_languages_it_was_given(tree):
        remove_colocated_tests(directory=tree, languages=["typescript"])
        assert not (tree / "src" / "gbnf.test.ts").exists()
        assert (tree / "gbnf" / "parse_test.py").is_file()

    def it_removes_nothing_when_no_language_is_named(tree):
        remove_colocated_tests(directory=tree, languages=[])
        assert relative_files(tree) == sorted(TREE)

    def it_leaves_every_other_file_in_place(tree):
        remove_colocated_tests(directory=tree, languages=LANGUAGES)
        assert relative_files(tree) == sorted(SURVIVORS)

    def it_leaves_the_surviving_bytes_untouched(tree):
        remove_colocated_tests(directory=tree, languages=LANGUAGES)
        assert {name: (tree / name).read_text() for name in SURVIVORS} == {
            name: TREE[name] for name in SURVIVORS
        }

    def it_is_a_no_op_on_an_already_stripped_tree(tree):
        remove_colocated_tests(directory=tree, languages=LANGUAGES)
        before = relative_files(tree)
        remove_colocated_tests(directory=tree, languages=LANGUAGES)
        assert relative_files(tree) == before
