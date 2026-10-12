import posixpath

from measure_transcript.resolve_path import resolve_path

GLOB = set("*?[")


def copy_targets(words: list[str], cwd: str, directories: set[str]) -> list[tuple[str, str]]:
    """For a `cp` segment, each (destination, origin) pair it creates; empty for any other command.

    The destination is a directory when it ends in `/`, when several sources go
    to it, or when it is one of `directories`. A glob or `.` source maps the
    destination to the directory it names.
    """
    if not words or words[0] != "cp":
        return []
    paths = [w for w in words[1:] if not w.startswith("-")]
    if len(paths) < 2:
        return []
    *sources, destination = paths
    into = destination.endswith("/") or len(sources) > 1 or resolve_path(destination, cwd) in directories
    destination = resolve_path(destination, cwd)
    pairs = []
    for source in sources:
        name = posixpath.basename(source.rstrip("/"))
        if GLOB & set(name) or name == ".":
            pairs.append((destination, resolve_path(posixpath.dirname(source), cwd)))
        else:
            pairs.append((posixpath.join(destination, name) if into else destination, resolve_path(source, cwd)))
    return pairs
