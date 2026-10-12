import re
import shlex

from measure_transcript.resolve_path import resolve_path
from measure_transcript.substitutions import PLACEHOLDER, substitutions

HEREDOC = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][\w-]*)\2")
PUNCTUATION = ";&|()<>\n"
WRITE_REDIRECTS = {">", ">>", ">|", "&>", "&>>"}


def split_command(command: str, cwd: str) -> dict:
    """A Bash tool command as segments of words, each with the cwd it runs in and the files it writes.

    Heredoc bodies are cut out first and returned on their own. A `$(...)`
    substitution becomes segments of its own, ahead of the rest, and leaves
    `$(...)` in its place. Segments split
    at `;`, `&&`, `||`, `|`, parentheses and newlines. `cd` moves the cwd of the
    segments after it. Redirect operators and their targets leave the words; a
    `>` or `>>` target and a `tee` argument are writes.
    """
    lines, heredocs, pending = [], [], []
    for line in command.split("\n"):
        if pending:
            strip, delimiter = pending[0]
            if (line.lstrip("\t") if strip else line) == delimiter:
                pending.pop(0)
                heredocs.append("")
            else:
                heredocs[-1] += line + "\n"
            continue
        lines.append(line)
        pending = [(bool(strip), delimiter) for strip, _, delimiter in HEREDOC.findall(line)]
        if pending:
            heredocs.append("")
    heredocs = [h for h in heredocs if h]
    text, inner = substitutions("\n".join(lines))
    segments = [segment for command in inner for segment in split_command(command, cwd)["segments"]]
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=PUNCTUATION)
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        tokens = text.split()
    tokens = [token.replace(PLACEHOLDER, "$(...)") for token in tokens]

    words, writes, i = [], [], 0

    def close():
        nonlocal words, writes, cwd
        if words and words[0] == "cd" and len(words) > 1:
            cwd = resolve_path(words[1], cwd)
        if words or writes:
            segments.append({"words": words, "cwd": cwd, "writes": writes})
        words, writes = [], []

    while i < len(tokens):
        token = tokens[i]
        if token and set(token) <= set(PUNCTUATION):
            if "<" in token or ">" in token:
                if words and words[-1].isdigit():
                    words.pop()
                target = tokens[i + 1] if i + 1 < len(tokens) else ""
                if token in WRITE_REDIRECTS and target != "/dev/null":
                    writes.append(resolve_path(target, cwd))
                i += 2
                continue
            close()
        else:
            words.append(token)
        i += 1
    close()
    for segment in segments:
        if segment["words"] and segment["words"][0] == "tee":
            segment["writes"] += [resolve_path(w, segment["cwd"]) for w in segment["words"][1:] if not w.startswith("-")]
    return {"segments": segments, "heredocs": heredocs}
