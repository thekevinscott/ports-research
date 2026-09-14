from pathlib import Path

TEST_SUITE_DIRECTORY_NAMES = {
    "python": "python",
    "typescript": "typescript",
    "javascript": "typescript",
}


def locate_test_suite(
    language: str, *, derivations_directory: Path, derivation_cache_key: str
) -> Path:
    """The derivation cache's test suite for a port written in `language`.

    typescript and javascript share one suite: the derivation only ever writes a
    "typescript" tree — vitest specs run against a TS entry shim — so a javascript
    port is graded against the same files a typescript port would be.
    """
    directory = (
        derivations_directory
        / derivation_cache_key
        / "tests"
        / TEST_SUITE_DIRECTORY_NAMES[language]
    )
    if not directory.is_dir():
        raise FileNotFoundError(
            f"no {language} test suite at {directory} — "
            "has gbnf-experiment's reference implementation been derived yet?"
        )
    return directory
