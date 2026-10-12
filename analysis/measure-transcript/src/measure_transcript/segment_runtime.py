import posixpath

from measure_transcript.command_word import command_word

NODE = {"node", "npx", "tsx"}
VERSION = {"--version", "-v", "-V", "-VV"}


def segment_runtime(words: list[str]) -> str | None:
    """`python` or `node` when the segment's program is that runtime (`python*`; `node`, `npx`, `tsx`), unless it only asks for the version."""
    i = command_word(words)
    if i >= len(words) or (words[i + 1:] and set(words[i + 1:]) <= VERSION):
        return None
    program = posixpath.basename(words[i])
    if program.startswith("python"):
        return "python"
    if program in NODE:
        return "node"
    return None
