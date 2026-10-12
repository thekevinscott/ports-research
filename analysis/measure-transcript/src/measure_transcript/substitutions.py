PLACEHOLDER = "__substitution__"


def substitutions(text: str) -> tuple[str, list[str]]:
    """`text` with each `$(...)` outside single quotes replaced by a placeholder, and the commands they held."""
    out, inner, i, quoted = [], [], 0, False
    while i < len(text):
        if text[i] == "'":
            quoted = not quoted
        if not quoted and text.startswith("$(", i):
            depth, j = 1, i + 2
            while j < len(text) and depth:
                depth += {"(": 1, ")": -1}.get(text[j], 0)
                j += 1
            inner.append(text[i + 2:j - 1])
            out.append(PLACEHOLDER)
            i = j
            continue
        out.append(text[i])
        i += 1
    return "".join(out), inner
