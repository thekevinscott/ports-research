from pathlib import Path
from tempfile import TemporaryDirectory

from .git_diff_stats import git_diff_stats
from .normalize_tree import normalize_tree

SCRATCH = Path("/tmp/claude")


def measure_git_diff(*, language: str, a: Path, b: Path, exclude: list[str]) -> dict:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="measure-git-diff-", dir=SCRATCH) as scratch:
        sides = {
            side: normalize_tree(language=language, source=source, destination=Path(scratch, side), exclude=exclude)
            for side, source in (("a", a), ("b", b))
        }
        stats = git_diff_stats(Path(scratch, "a"), Path(scratch, "b"))
    reference_lines = sides["a"]["lines"]
    churn = stats["insertions"] + stats["deletions"]
    shared = reference_lines - stats["deletions"]
    total_lines = reference_lines + shared + stats["insertions"]
    return {
        "language": language,
        "a": str(a),
        "b": str(b),
        **stats,
        "reference_lines": reference_lines,
        "diff_ratio": churn / reference_lines if reference_lines else None,
        "similarity_pct": 100 * 2 * shared / total_lines if total_lines else None,
        "identical": len(set(sides["a"]["paths"]) & set(sides["b"]["paths"])) - stats["modified"],
        "formatter_failures": [
            {"side": side, "path": path} for side, report in sides.items() for path in report["formatter_failures"]
        ],
    }
