"""What the derivation container leaves in the data tree after a real run.

The reference implementation the agent is handed comes out of that container.
If it is missing a language, a suite or the scaffolding a suite needs to run,
the port was graded against something the pipeline never built.
"""

from pathlib import Path

import pytest

from gbnf_experiment.config import derivation_cache_key


@pytest.fixture
def derivation(completed_run: Path, derivations: Path) -> Path:
    """The derivation the run was assembled from."""
    return derivations / derivation_cache_key


def describe_the_derivation():
    def it_derives_a_source_tree_for_both_languages(derivation: Path):
        assert (derivation / "source" / "typescript" / "src").is_dir()
        assert (derivation / "source" / "python" / "gbnf").is_dir()

    def it_derives_a_test_suite_for_both_languages(derivation: Path):
        assert sorted((derivation / "tests" / "typescript").rglob("*.test.ts"))
        assert sorted((derivation / "tests" / "python").rglob("*_test.py"))

    def it_ships_grammar_fixtures_beside_the_python_suite(derivation: Path):
        grammars = derivation / "tests" / "python" / "iteration" / "grammars"
        assert len(list(grammars.glob("*.gbnf"))) == 8
        assert len(list(grammars.glob("*.json"))) == 8

    def it_excludes_installed_dependencies_from_the_source_trees(derivation: Path):
        source = derivation / "source"
        assert not list(source.rglob("node_modules"))
        assert not [path for path in source.rglob("*") if path.is_symlink()]

    def it_ships_a_readme_and_a_runner_config_with_the_typescript_suite(
        derivation: Path,
    ):
        suite = derivation / "tests" / "typescript"
        assert (suite / "README.md").is_file()
        assert (suite / "vitest.config.unit.ts").is_file()

    def it_ships_a_readme_with_the_python_suite(derivation: Path):
        assert (derivation / "tests" / "python" / "README.md").is_file()
