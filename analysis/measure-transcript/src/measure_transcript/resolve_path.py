import posixpath


def resolve_path(path: str, cwd: str) -> str:
    """`path` as the shell in `cwd` would resolve it, without touching a filesystem."""
    return posixpath.normpath(posixpath.join(cwd, path))
