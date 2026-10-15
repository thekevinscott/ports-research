from pathlib import Path

from gbnf_experiment.config import compute_prepare_cache_key, settings
from gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist import (
    assemble_whitelist,
)

TREE_NAMES = {"python": "python", "typescript": "javascript", "javascript": "javascript"}


def locate_test_suite(language: str) -> Path:
    """The prepared reference tree that carries every gbnf test for `language`.

    gbnf_experiment keys each prepared tree by what it copied; the one with unit and
    source integration tests holds the language's whole suite. typescript is graded
    against the javascript tree.
    """
    tree = TREE_NAMES[language]
    key = compute_prepare_cache_key(
        settings.gbnf_commit,
        settings.prepare_docker_directory,
        assemble_whitelist(
            tree,
            include_unit_tests=True,
            include_source_integration_tests=True,
            include_target_integration_tests=False,
        ),
    )
    directory = settings.prepared_directory / key / tree
    if not directory.is_dir():
        raise FileNotFoundError(
            f"no {language} test suite at {directory} — has gbnf_experiment prepared it yet?"
        )
    return directory
