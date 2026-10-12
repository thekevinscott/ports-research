import re

RUNTIME = r"(python3?|node|npx|tsx)"
PATTERNS = (
    re.compile(rf"""["']{RUNTIME}["'\s]"""),
    re.compile(rf"^\s*{RUNTIME}\s", re.M),
    re.compile(rf"^#!.*\b{RUNTIME}\b", re.M),
)
NAMES = {"python": "python", "python3": "python", "node": "node", "npx": "node", "tsx": "node"}


def text_runtimes(text: str) -> set[str]:
    """The runtimes a script names as a program: as a string literal, at the start of a line, or in its shebang."""
    return {NAMES[match] for pattern in PATTERNS for match in pattern.findall(text)}
