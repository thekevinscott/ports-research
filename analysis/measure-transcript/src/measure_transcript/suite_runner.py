import posixpath

from measure_transcript.command_word import command_word

RUNNERS = {"pytest", "py.test", "vitest", "jest"}
LAUNCHERS = {"npx", "pnpx"}
# Options whose next word is their value, not a path.
VALUE_OPTIONS = {
    "-p", "-k", "-m", "-c", "-o", "-t", "-n", "--config", "--rootdir", "--root", "--dir", "--reporter",
    "--deselect", "--ignore", "--maxfail", "--project", "--testNamePattern",
}
SUBCOMMANDS = {"run", "watch", "related"}
NOT_A_RUN = {"--version", "-V", "--help", "-h", "--collect-only", "--co", "--list", "--listTests"}


def suite_runner(words: list[str]) -> list[str] | None:
    """The path arguments of a segment that runs a test suite, or None when it runs none.

    A suite run is pytest (also as `python -m pytest`), vitest, jest, `node --test`,
    `npm test`, `pnpm test` (and `run test*`), or `just test*`, after any
    environment, `timeout` or `uv run` prefix and an `npx` or `pnpm exec` launcher.
    """
    i = command_word(words)
    if i < len(words) and words[i] in LAUNCHERS:
        i += 1
    if i + 1 < len(words) and words[i] == "pnpm" and words[i + 1] in {"exec", "dlx"}:
        i += 2
    if i >= len(words):
        return None
    program, rest = posixpath.basename(words[i]), words[i + 1:]
    if program.startswith("python") and rest[:2] == ["-m", "pytest"]:
        program, rest = "pytest", rest[2:]
    elif program == "pnpm" and rest and rest[0] in RUNNERS:
        program, rest = rest[0], rest[1:]
    if program in {"npm", "pnpm"}:
        script = rest[1:2] if rest[:1] == ["run"] else rest[:1]
        return [] if script and script[0].startswith("test") else None
    if program == "just":
        return [] if rest and rest[0].startswith("test") else None
    if program == "node":
        if "--test" not in rest:
            return None
    elif program not in RUNNERS:
        return None
    if NOT_A_RUN & set(rest):
        return None
    paths, skip = [], False
    for word in rest:
        if skip:
            skip = False
        elif word in VALUE_OPTIONS:
            skip = True
        elif not word.startswith("-") and word not in SUBCOMMANDS:
            paths.append(word)
    return paths
