from measure_transcript.classify_path import OTHER, classify_path
from measure_transcript.may_hold_tests import may_hold_tests
from measure_transcript.reference_path import reference_path

TESTS = {"source_tests", "target_tests"}


def under(path: str, directory: str) -> bool:
    return path == directory or path.startswith(directory.rstrip("/") + "/")


def suite_class(paths: list[str], source_language: str, copies: dict[str, str], own_files: list[str]) -> str:
    """Which tests a suite run over `paths` reaches: `source_tests`, `target_tests`, `own_tests`, or `unknown` when it is more than one.

    A path inside a shipped suite, or a copy of one, is that suite. A directory
    reaches every shipped suite under it or copied into it, plus the agent's own
    tests when its written test files are under it. A path the reference reaches
    nowhere is the agent's own.
    """
    found = set()
    for path in paths:
        cls = classify_path(path, source_language, copies)
        if cls in TESTS:
            found.add(cls)
            continue
        origins = [reference_path(path, copies)] + [
            origin for destination, origin in copies.items() if destination != path and under(destination, path) and may_hold_tests(origin)
        ]
        classes = set()
        for origin in origins:
            for language, suite in ((source_language, "source_tests"), (OTHER[source_language], "target_tests")):
                if under(origin, f"/input/{language}") or under(f"/input/{language}", origin):
                    classes.add(suite)
        if not classes or any(under(f, path) for f in own_files):
            classes.add("own_tests")
        found |= classes
    return found.pop() if len(found) == 1 else "unknown"
