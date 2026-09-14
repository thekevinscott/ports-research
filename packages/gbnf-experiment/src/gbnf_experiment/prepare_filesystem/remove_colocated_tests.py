from collections.abc import Iterable
from pathlib import Path

COLOCATED_TEST_PATTERNS = {"typescript": "*.test.ts", "python": "*_test.py"}


def remove_colocated_tests(*, directory: Path, languages: Iterable[str]) -> None:
    """Delete the named languages' tests from beside the code they cover.

    Scoped to test files. The reference is otherwise left exactly as upstream
    wrote it, badges and repo URLs included, per the standing decision that a
    doctored codebase is its own confound.
    """
    for language in languages:
        for path in directory.rglob(COLOCATED_TEST_PATTERNS[language]):
            path.unlink()
