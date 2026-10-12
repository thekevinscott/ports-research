import posixpath
from fnmatch import fnmatchcase

from measure_transcript.grep_filter import grep_filter
from measure_transcript.resolve_path import resolve_path

TESTS = {"-name", "-path", "-type"}


def find_output(segments: list[list[str]], cwd: str, files: set[str]) -> list[str] | None:
    """The paths a `$(find ...)` substitution prints, worked out from `files`, the reference's listing.

    None unless the substitution is one `find` over start directories under
    /input, testing only `-name`, `-path` and `-type f`, each possibly negated
    by `!` or `-not`, then piped through `sort` and otherwise only `grep [-v]`
    with patterns free of regex characters. An unsorted find is None: the
    transcript does not record the directory order it prints in.
    """
    if not segments or segments[0][:1] != ["find"] or ["sort"] not in segments[1:]:
        return None
    filters = [grep_filter(stage) for stage in segments[1:] if stage != ["sort"]]
    if None in filters:
        return None
    words = segments[0][1:]
    starts = []
    while words and not words[0].startswith("-") and words[0] not in ("!", "("):
        starts.append(words.pop(0))
    tests = []
    while words:
        negate = words[0] in ("!", "-not")
        if negate:
            words.pop(0)
        if len(words) < 2 or words[0] not in TESTS or (words[0] == "-type" and words[1] != "f"):
            return None
        tests.append((negate, words.pop(0), words.pop(0)))
    printed = []
    for start in starts or ["."]:
        root = resolve_path(start, cwd)
        if root != "/input" and not root.startswith("/input/"):
            return None
        for file in (f for f in files if f.startswith(root + "/")):
            path = start.rstrip("/") + file[len(root):]
            values = {"-name": posixpath.basename(file), "-path": path}
            if all(negate != (test == "-type" or fnmatchcase(values[test], pattern)) for negate, test, pattern in tests):
                printed.append(path)
    return sorted(path for path in printed if all(keep(path) for keep in filters))

