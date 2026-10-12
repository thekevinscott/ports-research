import re

ANSI = re.compile(r"\x1b\[[0-9;]*m")
PYTEST = re.compile(r"^.*\b\d+ (?:passed|failed)\b.* in \d+(?:\.\d+)?s\b.*$", re.M)
VITEST = re.compile(r"^\s*Tests\s+(.*?)\s*\(\d+\)\s*$", re.M)
JEST = re.compile(r"^\s*Tests:\s+(.*\btotal)\s*$", re.M)
NODE = re.compile(r"^[#ℹ]\s*pass (\d+)\s*\n[#ℹ]\s*fail (\d+)", re.M)


def summary_counts(text: str) -> list[dict]:
    """Every test runner summary line in `text`, in order, as passed and failed counts.

    pytest: `N passed, M failed ... in Xs`; vitest: `Tests  M failed | N passed (T)`;
    jest: `Tests: M failed, N passed, T total`; node --test: `# pass N` then `# fail M`.
    A summary with neither a passed nor a failed count is skipped.
    """
    text = ANSI.sub("", text)
    found = []
    for pattern in (PYTEST, VITEST, JEST):
        for match in pattern.finditer(text):
            line = match.group(0)
            if re.search(r"\d+ (?:passed|failed)\b", line):
                counts = {word: re.search(rf"(\d+) {word}\b", line) for word in ("passed", "failed")}
                found.append((match.start(), {word: int(m.group(1)) if m else 0 for word, m in counts.items()}))
    for match in NODE.finditer(text):
        found.append((match.start(), {"passed": int(match.group(1)), "failed": int(match.group(2))}))
    return [counts for _, counts in sorted(found, key=lambda pair: pair[0])]
