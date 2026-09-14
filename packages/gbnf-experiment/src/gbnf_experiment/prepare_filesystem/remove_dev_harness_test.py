import pytest

from gbnf_experiment.prepare_filesystem.remove_dev_harness import remove_dev_harness

TREE = {
    "dev/browser/debug/index.html": "<html></html>\n",
    "dev/browser/debug/package.json": '{"name": "debug"}\n',
    "dev/browser/collect-test-cases/vite.config.ts": "export default {};\n",
    "dev/browser/collect-test-cases/grammars/arithmetic.gbnf": "root ::= 'x'\n",
    "dev/node/src/commands/parse.ts": "export const parse = () => {};\n",
    "src/gbnf.ts": "export const parse = () => {};\n",
    "src/utils/is-point-in-range.ts": "export const inRange = () => {};\n",
    "package.json": '{"name": "gbnf"}\n',
    "vite.config.ts": "export default {};\n",
    "dev-deps/requirements.txt": "pytest\n",
    "gbnf/parse.py": "def parse(): ...\n",
}

HARNESS = [name for name in TREE if name.startswith("dev/")]
SURVIVORS = [name for name in TREE if name not in HARNESS]


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


def describe_remove_dev_harness():
    def it_removes_the_typescript_dev_directory(tree):
        remove_dev_harness(directory=tree, language="typescript")
        assert not (tree / "dev").exists()

    def it_removes_the_harness_nested_any_depth(tree):
        remove_dev_harness(directory=tree, language="typescript")
        assert relative_files(tree) == sorted(SURVIVORS)

    def it_leaves_the_library_in_place(tree):
        remove_dev_harness(directory=tree, language="typescript")
        assert (tree / "src" / "gbnf.ts").is_file()
        assert (tree / "package.json").is_file()

    def it_leaves_the_surviving_bytes_untouched(tree):
        remove_dev_harness(directory=tree, language="typescript")
        assert {name: (tree / name).read_text() for name in SURVIVORS} == {
            name: TREE[name] for name in SURVIVORS
        }

    def it_leaves_a_python_reference_alone(tree):
        """Python has no dev harness, and dev-deps/ is not one."""
        remove_dev_harness(directory=tree, language="python")
        assert relative_files(tree) == sorted(TREE)

    def it_spares_the_python_dependency_pinning(tree):
        """dev-deps/ shares a prefix with dev/ and must survive either way."""
        remove_dev_harness(directory=tree, language="typescript")
        assert (tree / "dev-deps" / "requirements.txt").is_file()

    def it_ignores_a_language_it_has_no_harness_for(tree):
        remove_dev_harness(directory=tree, language="rust")
        assert relative_files(tree) == sorted(TREE)

    def it_is_a_no_op_on_an_already_stripped_tree(tree):
        remove_dev_harness(directory=tree, language="typescript")
        before = relative_files(tree)
        remove_dev_harness(directory=tree, language="typescript")
        assert relative_files(tree) == before
