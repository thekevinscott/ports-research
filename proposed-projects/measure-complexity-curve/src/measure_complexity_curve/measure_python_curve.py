import shlex
import tempfile
from pathlib import Path

from .hyperfine_mean import hyperfine_mean

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PACKAGE_ROOT / "scripts" / "parse_grammar.py"


def measure_python_curve(*, target: Path, corpus: list[dict], iterations: int) -> list[dict]:
    """Per-parse seconds for each corpus entry, timed with hyperfine wrapping
    scripts/parse_grammar.py.

    That script's execution strategy — sys.path-insert target, then a bare
    `import gbnf` — is execute-test-suite's own host-subprocess strategy for
    python ports (`PYTHONPATH=target`), not a second one invented for
    measurement.

    A single baseline measurement (`--iterations 0`, so the process still
    starts and imports the target but never parses) is taken once and
    subtracted from every point: `uv run --no-project`'s own startup cost
    otherwise swamps the actual parse cost for small grammars, which would
    flatten exactly the low end of the curve the shape fit most depends on.
    """
    with tempfile.TemporaryDirectory() as scratch:
        scratch_path = Path(scratch)

        baseline_grammar_file = scratch_path / "baseline.gbnf"
        baseline_grammar_file.write_text(corpus[0]["grammar"])
        baseline_seconds = hyperfine_mean(
            command=shlex.join(
                [
                    "uv",
                    "run",
                    "--no-project",
                    "python",
                    str(SCRIPT),
                    "--target",
                    str(target),
                    "--grammar-file",
                    str(baseline_grammar_file),
                    "--iterations",
                    "0",
                ]
            ),
            scratch=scratch_path,
        )

        curve = []
        for entry in corpus:
            grammar_file = scratch_path / f"{entry['size']}.gbnf"
            grammar_file.write_text(entry["grammar"])
            raw_seconds = hyperfine_mean(
                command=shlex.join(
                    [
                        "uv",
                        "run",
                        "--no-project",
                        "python",
                        str(SCRIPT),
                        "--target",
                        str(target),
                        "--grammar-file",
                        str(grammar_file),
                        "--iterations",
                        str(iterations),
                    ]
                ),
                scratch=scratch_path,
            )
            curve.append({"size": entry["size"], "seconds": (raw_seconds - baseline_seconds) / iterations})
        return curve
