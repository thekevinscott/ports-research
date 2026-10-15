import shutil
from pathlib import Path

JAVASCRIPT_GLOBS = {
    "unit": "src/**/*.test.ts",
    "integration": "integration-tests/generated/**/*.test.ts",
}
TEST_FILE_GLOBS = {
    "python": {"unit": "gbnf/**/*_test.py", "integration": "tests/generated/**/*_test.py"},
    "typescript": JAVASCRIPT_GLOBS,
    "javascript": JAVASCRIPT_GLOBS,
}


def stage_test_suite(
    *, language: str, suite: str, test_suite_directory: Path, target: Path, destination: Path
) -> list[Path]:
    """Copy target to destination, overlay the suite's reference test files, return them.

    Each file lands at its path in the reference tree, overwriting any copy the port
    has. Unit tests import their neighbours relatively, so a port laid out differently
    fails at import and counts against it.
    """
    shutil.copytree(target, destination, symlinks=True)
    staged = []
    for source in sorted(test_suite_directory.glob(TEST_FILE_GLOBS[language][suite])):
        path = destination / source.relative_to(test_suite_directory)
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, path)
        staged.append(path)
    return staged
