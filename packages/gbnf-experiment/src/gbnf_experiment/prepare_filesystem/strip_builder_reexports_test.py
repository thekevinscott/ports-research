from gbnf_experiment.prepare_filesystem.strip_builder_reexports import (
    strip_builder_reexports,
)

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


def describe_strip_builder_reexports():
    def it_removes_the_single_line_wildcard_reexport(tmp_path):
        index_ts = tmp_path / "index.ts"
        index_ts.write_text(INDEX_TS)
        strip_builder_reexports(index_ts)
        assert "./builder/index.js" not in index_ts.read_text()

    def it_removes_the_multiline_named_reexport(tmp_path):
        index_ts = tmp_path / "index.ts"
        index_ts.write_text(INDEX_TS)
        strip_builder_reexports(index_ts)
        text = index_ts.read_text()
        assert "ToStringArgs" not in text
        assert "./builder/types.js" not in text

    def it_leaves_unrelated_exports_in_place(tmp_path):
        index_ts = tmp_path / "index.ts"
        index_ts.write_text(INDEX_TS)
        strip_builder_reexports(index_ts)
        text = index_ts.read_text()
        assert "export { GBNF as default, } from './gbnf.js';" in text
        assert "isRange" in text
        assert "ParseState" in text

    def it_collapses_the_blank_lines_the_removal_leaves_behind(tmp_path):
        index_ts = tmp_path / "index.ts"
        index_ts.write_text(INDEX_TS)
        strip_builder_reexports(index_ts)
        assert "\n\n\n" not in index_ts.read_text()

    def it_is_a_no_op_when_nothing_references_builder(tmp_path):
        index_ts = tmp_path / "index.ts"
        index_ts.write_text("export { GBNF as default } from './gbnf.js';\n")
        before = index_ts.read_text()
        strip_builder_reexports(index_ts)
        assert index_ts.read_text() == before

    def it_tolerates_a_missing_index_ts(tmp_path):
        strip_builder_reexports(tmp_path / "index.ts")
        assert not (tmp_path / "index.ts").exists()

    def it_is_idempotent(tmp_path):
        index_ts = tmp_path / "index.ts"
        index_ts.write_text(INDEX_TS)
        strip_builder_reexports(index_ts)
        once = index_ts.read_text()
        strip_builder_reexports(index_ts)
        assert index_ts.read_text() == once
