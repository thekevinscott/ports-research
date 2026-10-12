import posixpath

from measure_transcript.is_test_path import is_test_path

# Copied files that hold no tests; any other copied name without an extension is taken for a directory.
CONFIG_NAMES = {"Makefile", "justfile", "Justfile", "LICENSE", "Dockerfile"}


def may_hold_tests(origin: str) -> bool:
    """Whether a copied path can hold tests: a test file, or a name without an extension (a directory) that is not a known config file."""
    name = posixpath.basename(origin)
    return is_test_path(origin) or ("." not in name and name not in CONFIG_NAMES)
