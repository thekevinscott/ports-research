from judge.source_files import source_files

KEPT = ["gbnf/__init__.py", "gbnf/grammar.py", "src/index.ts", "src/utils/x.ts", "lib/run.mjs"]
DROPPED = [
    "gbnf/grammar_test.py",
    "gbnf/test_grammar.py",
    "conftest.py",
    "tests/generated/a_test.py",
    "test/helpers.ts",
    "integration-tests/generated/a.test.ts",
    "src/index.test.ts",
    "src/index.spec.ts",
    "src/builder/build.ts",
    "dev/node/index.ts",
    "node_modules/pkg/index.js",
    "gbnf/__pycache__/grammar.cpython-314.pyc",
    ".venv/lib/x.py",
    "dist/index.js",
    "dev-deps/build.in",
    "vitest.config.ts",
    "vite.config.esm.ts",
    ".eslintrc.cjs",
    "README.md",
    "package.json",
    "pnpm-lock.yaml",
    "uv.lock",
]


def describe_source_files():
    def it_keeps_source_files_and_drops_tests_dependencies_and_configuration(tmp_path):
        for relative in KEPT + DROPPED:
            (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / relative).write_text("x")
        assert [p.as_posix() for p in source_files(tmp_path)] == sorted(KEPT)

    def it_returns_paths_relative_to_the_root(tmp_path):
        (tmp_path / "a.py").write_text("x")
        assert [p.as_posix() for p in source_files(tmp_path)] == ["a.py"]
