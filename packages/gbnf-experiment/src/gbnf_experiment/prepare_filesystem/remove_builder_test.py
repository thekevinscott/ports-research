import pytest

from gbnf_experiment.prepare_filesystem.remove_builder import remove_builder

INDEX_TS = (
    "export { GBNF as default, } from './gbnf.js';\n"
    "export {\n"
    "  isRange,\n"
    "} from './grammar-graph/type-guards.js';\n"
    "export { ParseState, } from './grammar-graph/parse-state.js';\n"
    "\n"
    "export * from \"./builder/index.js\";\n"
    "\n"
    "export {\n"
    "  type ToStringArgs,\n"
    "} from './builder/types.js';\n"
)

TREE = {
    "src/builder/index.ts": "export * from './grammar-builder.js';\n",
    "src/builder/build-grammar.ts": "export const buildGrammar = () => {};\n",
    "src/builder/grammar-builder.ts": "export class GrammarBuilder {}\n",
    "src/index.ts": INDEX_TS,
    "src/gbnf.ts": "export const parse = () => {};\n",
    "src/utils/is-point-in-range.ts": "export const inRange = () => {};\n",
    "package.json": '{"name": "gbnf"}\n',
    "gbnf/parse.py": "def parse(): ...\n",
    "gbnf/rules_builder/symbol_ids.py": "class SymbolIds: ...\n",
}

BUILDER_FILES = [name for name in TREE if name.startswith("src/builder/")]
SURVIVORS = [name for name in TREE if name not in BUILDER_FILES and name != "src/index.ts"]


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


def describe_remove_builder():
    def it_removes_the_typescript_builder_directory(tree):
        remove_builder(directory=tree, language="typescript")
        assert not (tree / "src" / "builder").exists()

    def it_delegates_to_strip_the_index_ts_reexports(tree):
        remove_builder(directory=tree, language="typescript")
        text = (tree / "src" / "index.ts").read_text()
        assert "builder" not in text
        assert "export { GBNF as default, } from './gbnf.js';" in text

    def it_leaves_the_library_in_place(tree):
        remove_builder(directory=tree, language="typescript")
        assert (tree / "src" / "gbnf.ts").is_file()
        assert (tree / "package.json").is_file()

    def it_leaves_the_surviving_bytes_untouched(tree):
        remove_builder(directory=tree, language="typescript")
        assert {name: (tree / name).read_text() for name in SURVIVORS} == {
            name: TREE[name] for name in SURVIVORS
        }

    def it_leaves_a_python_reference_alone(tree):
        """Python has no builder DSL, and rules_builder/ is parser internals, not it."""
        remove_builder(directory=tree, language="python")
        assert relative_files(tree) == sorted(TREE)

    def it_ignores_a_language_it_has_no_builder_for(tree):
        remove_builder(directory=tree, language="rust")
        assert relative_files(tree) == sorted(TREE)

    def it_is_a_no_op_on_an_already_stripped_tree(tree):
        remove_builder(directory=tree, language="typescript")
        before = relative_files(tree)
        before_index = (tree / "src" / "index.ts").read_text()
        remove_builder(directory=tree, language="typescript")
        assert relative_files(tree) == before
        assert (tree / "src" / "index.ts").read_text() == before_index
