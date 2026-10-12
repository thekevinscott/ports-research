from measure_transcript.reference_path import reference_path

OTHER = {"python": "javascript", "javascript": "python"}
# Where each language's shipped tests sit under /input: a whole directory, or a file name pattern beside the source.
TEST_DIRECTORIES = {"python": "tests", "javascript": "integration-tests"}
TEST_SUFFIXES = {"python": "_test.py", "javascript": ".test.ts"}


def classify_path(path: str | None, source_language: str, copies: dict[str, str]) -> str:
    """Which part of the sandbox `path` is in: `source`, `source_tests`, `target_tests`, `port` or `other`.

    The reference is mounted at /input in gbnf's layout (`python/`, `javascript/`)
    and the port is written to /target. A path under a copy is classified as the
    path it was copied from.
    """
    if not path:
        return "other"
    path = reference_path(path, copies)
    if path == "/target" or path.startswith("/target/"):
        return "port"
    for language, side in ((source_language, "source"), (OTHER[source_language], "target")):
        root = f"/input/{language}"
        if path != root and not path.startswith(root + "/"):
            continue
        tests = root + "/" + TEST_DIRECTORIES[language]
        if path == tests or path.startswith(tests + "/") or path.endswith(TEST_SUFFIXES[language]):
            return f"{side}_tests"
        return "source" if side == "source" else "other"
    return "other"
