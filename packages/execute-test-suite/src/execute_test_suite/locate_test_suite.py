from pathlib import Path

TEST_SUITE_DIRECTORY_NAMES = {
    "python": "python",
    "typescript": "typescript",
    "javascript": "typescript",
}


def locate_test_suite(language: str, *, test_suites_directory: Path) -> Path:
    """The generated test suite for a port written in `language`.

    typescript and javascript share one suite: the prepare stage only ever writes a
    "typescript" tree — vitest specs run against a TS entry shim — so a javascript
    port is graded against the same files a typescript port would be.
    """
    directory = test_suites_directory / TEST_SUITE_DIRECTORY_NAMES[language]
    if not directory.is_dir():
        raise FileNotFoundError(f"no {language} test suite at {directory}")
    return directory
