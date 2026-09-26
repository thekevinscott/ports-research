import shlex
import tempfile
from pathlib import Path

from .hyperfine_mean import hyperfine_mean

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PACKAGE_ROOT / "scripts" / "parse-grammar.ts"
TSX_VERSION = "4.19.2"


def measure_typescript_curve(*, target: Path, corpus: list[dict], iterations: int) -> list[dict]:
    """Per-parse seconds for each corpus entry, timed with hyperfine wrapping
    scripts/parse-grammar.ts run through `pnpm dlx tsx`.

    That script's execution strategy — dynamic-import target's src/index.ts,
    the same PORT_ENTRY_FILE run_vitest_suite uses — is execute-test-suite's
    own host-subprocess strategy for typescript ports, not a second one
    invented for measurement.

    A single baseline measurement (`--iterations 0`, so the process still
    starts and imports the target but never parses) is taken once and
    subtracted from every point: `pnpm dlx`'s own startup cost otherwise
    swamps the actual parse cost for small grammars, which would flatten
    exactly the low end of the curve the shape fit most depends on.
    """
    with tempfile.TemporaryDirectory() as scratch:
        scratch_path = Path(scratch)

        baseline_grammar_file = scratch_path / "baseline.gbnf"
        baseline_grammar_file.write_text(corpus[0]["grammar"])
        baseline_seconds = hyperfine_mean(
            command=shlex.join(
                [
                    "pnpm",
                    "dlx",
                    f"tsx@{TSX_VERSION}",
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
                        "pnpm",
                        "dlx",
                        f"tsx@{TSX_VERSION}",
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
