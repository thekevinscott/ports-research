from fnmatch import fnmatchcase

GLOB = set("*?[")


def expand_glob(path: str, files: set[str]) -> list[str]:
    """The files among `files` an absolute glob `path` names, sorted as the shell sorts them; `[path]` when it has no glob or names none.

    Each component matches one directory level, and a component starting with
    a dot is matched only by a pattern starting with one.
    """
    if not GLOB & set(path):
        return [path]
    patterns = path.split("/")
    matches = sorted(
        file for file in files
        if len(names := file.split("/")) == len(patterns)
        and all(fnmatchcase(name, pattern) and (pattern.startswith(".") or not name.startswith(".")) for name, pattern in zip(names, patterns))
    )
    return matches or [path]
