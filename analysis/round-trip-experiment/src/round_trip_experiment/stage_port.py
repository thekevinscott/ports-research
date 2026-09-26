import shutil
from pathlib import Path

BUILD_ARTEFACTS = ["node_modules", "__pycache__", ".venv", ".pytest_cache", "dist"]


def stage_port(
    run_directory: Path,
    *,
    source_language: str,
    derivation_cache_key: str,
    derivations_directory: Path,
    staging_directory: Path,
) -> Path:
    """run-gbnf-experiment reads its reference from the derivation cache and nowhere else,
    so the port is staged as a derivation of its own under a per-run cache root and the
    harness is pointed at that root. The forward reference comes from `git archive` and
    carries no build output; a port does, hence the ignore list.
    """
    staged = staging_directory / run_directory.name / derivation_cache_key
    shutil.copytree(
        run_directory / "ported_implementation",
        staged / "source" / source_language,
        ignore=shutil.ignore_patterns(*BUILD_ARTEFACTS),
        dirs_exist_ok=True,
    )
    suites = staged / "tests"
    if not suites.is_symlink():
        suites.symlink_to(derivations_directory / derivation_cache_key / "tests")
    return staged
