"""Regenerate the golden files by running the TypeScript reference implementation.

    python3 tests/differential/generate_golden.py

Requires Node >= 22.6 (for `--experimental-transform-types`). The goldens are
checked in so that `tests/test_differential.py` can verify the port against the
reference's answers even where Node isn't available.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from differential.setup_reference import prepare  # noqa: E402
from fuzz_cases import build_cases  # noqa: E402

TESTS_DIR = Path(__file__).resolve().parents[1]
GOLDEN_DIR = TESTS_DIR / "golden"
RUNNER = Path(__file__).resolve().parent / "run_reference.ts"


def run_reference(corpus: List[Dict[str, Any]], reference_dir: Path) -> List[Dict[str, Any]]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(corpus, handle)
        corpus_path = handle.name
    result = subprocess.run(
        [
            "node",
            "--experimental-transform-types",
            "--disable-warning=ExperimentalWarning",
            str(RUNNER),
            str(reference_dir),
            corpus_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"reference runner failed:\n{result.stderr}")
    return json.loads(result.stdout)


def strip_graphs(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop the (large) rendered-graph fields; the main corpus already covers them."""
    for case in results:
        for key in ("inputs", "code_point_inputs", "steps"):
            for entry in case.get(key, []):
                entry.pop("graph", None)
                entry.pop("graphColored", None)
    return results


def main() -> None:
    GOLDEN_DIR.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        reference_dir = prepare(Path(tmp) / "reference")

        corpus = json.loads((TESTS_DIR / "corpus.json").read_text())
        golden = run_reference(corpus, reference_dir)
        (GOLDEN_DIR / "corpus.json").write_text(
            json.dumps(golden, ensure_ascii=False) + "\n"
        )
        print(f"wrote golden/corpus.json ({len(golden)} cases)")

        fuzz = strip_graphs(run_reference(build_cases(), reference_dir))
        (GOLDEN_DIR / "fuzz.json").write_text(json.dumps(fuzz, ensure_ascii=False) + "\n")
        print(f"wrote golden/fuzz.json ({len(fuzz)} cases)")


if __name__ == "__main__":
    main()
