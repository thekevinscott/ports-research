import subprocess
from collections import Counter
from pathlib import Path


def git_diff(a: Path, b: Path, *options: str) -> str:
    result = subprocess.run(
        ["git", "diff", "--no-index", "-M", *options, str(a), str(b)], capture_output=True, text=True
    )
    if result.returncode > 1:
        raise RuntimeError(f"git diff exited {result.returncode}: {result.stderr}")
    return result.stdout


def git_diff_stats(a: Path, b: Path) -> dict:
    churn = [line.split("\t", 2)[:2] for line in git_diff(a, b, "--numstat").splitlines()]
    records = iter(git_diff(a, b, "--name-status", "-z").split("\0"))
    statuses = Counter()
    for status in records:
        if not status:
            continue
        next(records)
        if status.startswith("R"):
            next(records)
        statuses[status[0]] += 1
    return {
        "insertions": sum(int(added) for added, _ in churn if added != "-"),
        "deletions": sum(int(removed) for _, removed in churn if removed != "-"),
        "modified": statuses["M"],
        "renamed": statuses["R"],
        "added": statuses["A"],
        "deleted": statuses["D"],
    }
