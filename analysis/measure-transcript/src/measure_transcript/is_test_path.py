import posixpath

CODE = (".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".mts", ".cts")
TEST_DIRECTORIES = {"tests", "test", "__tests__", "integration-tests"}


def is_test_path(path: str) -> bool:
    """Whether `path` names a test file: `test_*.py`, `*_test.py`, `*.test.*` or `*.spec.*`, or code under a tests directory."""
    name = posixpath.basename(path)
    if not name.endswith(CODE):
        return False
    stem = name.rsplit(".", 1)[0]
    return (
        name.startswith("test_")
        or stem.endswith("_test")
        or stem.endswith((".test", ".spec"))
        or bool(TEST_DIRECTORIES & set(path.split("/")[:-1]))
    )
