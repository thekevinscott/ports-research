def reference_path(path: str, copies: dict[str, str]) -> str:
    """`path` mapped back through the copies the agent made: a path under a copy's destination becomes the same path under its origin."""
    for destination in sorted(copies, key=len, reverse=True):
        if path == destination or path.startswith(destination + "/"):
            return copies[destination] + path[len(destination):]
    return path
