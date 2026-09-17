"""What the gbnf-prepare container leaves in the data tree after a real run.

The reference implementation the agent is handed comes out of that container.
If it is missing a language, a suite or the scaffolding a suite needs to run,
the port was graded against something the pipeline never built.
"""

from pathlib import Path

import pytest

from gbnf_experiment.config import prepare_cache_key


@pytest.fixture
def prepared(completed_run: Path, prepared_cache: Path) -> Path:
    """The prepared corpus the run was assembled from."""
    return prepared_cache / prepare_cache_key


def describe_the_prepared_corpus():
    def it_prepares_a_source_tree_for_both_languages(prepared: Path):
        assert (prepared / "source" / "typescript" / "src").is_dir()
        assert (prepared / "source" / "python" / "gbnf").is_dir()

    def it_prepares_a_test_suite_for_both_languages(prepared: Path):
        assert sorted((prepared / "tests" / "typescript").rglob("*.test.ts"))
        assert sorted((prepared / "tests" / "python").rglob("*_test.py"))

    def it_ships_grammar_fixtures_beside_the_python_suite(prepared: Path):
        grammars = prepared / "tests" / "python" / "iteration" / "grammars"
        assert len(list(grammars.glob("*.gbnf"))) == 8
        assert len(list(grammars.glob("*.json"))) == 8

    def it_excludes_installed_dependencies_from_the_source_trees(prepared: Path):
        source = prepared / "source"
        assert not list(source.rglob("node_modules"))
        assert not [path for path in source.rglob("*") if path.is_symlink()]

    def it_ships_a_readme_and_a_runner_config_with_the_typescript_suite(
        prepared: Path,
    ):
        suite = prepared / "tests" / "typescript"
        assert (suite / "README.md").is_file()
        assert (suite / "vitest.config.unit.ts").is_file()

    def it_ships_a_readme_with_the_python_suite(prepared: Path):
        assert (prepared / "tests" / "python" / "README.md").is_file()
