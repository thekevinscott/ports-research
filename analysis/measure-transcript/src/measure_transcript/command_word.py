import re

ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*=")
WRAPPERS = {"time", "nice", "exec", "command", "env"}
TIMEOUT_VALUES = {"-s", "-k", "--signal", "--kill-after"}
UV_RUN_VALUES = {"--with", "--python", "-p", "--directory", "--project", "--env-file", "--extra", "--group", "--package"}


def command_word(words: list[str]) -> int:
    """The index of the program a segment runs, past environment assignments and `env`, `time`, `timeout` and `uv run`."""
    i = 0
    while i < len(words):
        word = words[i]
        if ASSIGNMENT.match(word) or word in WRAPPERS:
            i += 1
        elif word == "timeout":
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 2 if words[i] in TIMEOUT_VALUES else 1
            i += 1
        elif word == "uv" and i + 1 < len(words) and words[i + 1] == "run":
            i += 2
            while i < len(words) and words[i].startswith("-"):
                i += 2 if words[i] in UV_RUN_VALUES else 1
        else:
            return i
    return i
