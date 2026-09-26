"""Compare the Python port against the TypeScript reference implementation.

Two layers:

* against ``tests/golden/*.json``, captured from the reference — always runs;
* against the reference executed live under Node — runs when Node is available.

The single intentional behavioural deviation (see ``KNOWN_DEVIATIONS``) is asserted
explicitly rather than ignored, so it can't drift silently.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TESTS_DIR.parent))

from differential.run_ported import run as run_ported  # noqa: E402
from differential.setup_reference import node_version, prepare  # noqa: E402
from fuzz_cases import build_cases  # noqa: E402

# Case name -> reason. The port raises GrammarParseError where the reference leaks an
# internal symbol-table error; see README.md ("Deviations from the reference").
KNOWN_DEVIATIONS = {"err-no-root"}


def flatten(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Flatten to `case-name.key[index].field -> value` for readable assertions."""
    flat: Dict[str, Any] = {}
    for case in results:
        name = case["name"]
        for key in ("inputs", "code_point_inputs", "steps"):
            for index, entry in enumerate(case.get(key, [])):
                for field, value in entry.items():
                    flat[f"{name}.{key}[{index}].{field}"] = value
    return flat


def compare(
    expected: List[Dict[str, Any]], actual: List[Dict[str, Any]]
) -> List[Tuple[str, Any, Any]]:
    expected_flat, actual_flat = flatten(expected), flatten(actual)
    diffs: List[Tuple[str, Any, Any]] = []
    for path in sorted(set(expected_flat) | set(actual_flat)):
        if path.split(".")[0] in KNOWN_DEVIATIONS:
            continue
        want = expected_flat.get(path, "<missing>")
        got = actual_flat.get(path, "<missing>")
        if want != got:
            diffs.append((path, want, got))
    return diffs


def describe(diffs: List[Tuple[str, Any, Any]]) -> str:
    lines = [f"{len(diffs)} difference(s) from the reference implementation:"]
    for path, want, got in diffs[:20]:
        lines.append(f"  {path}\n    reference: {want!r}\n    ported   : {got!r}")
    if len(diffs) > 20:
        lines.append(f"  ... and {len(diffs) - 20} more")
    return "\n".join(lines)


class GoldenDifferentialTest(unittest.TestCase):
    """The port must reproduce the reference's recorded answers exactly."""

    def test_corpus_matches_golden(self) -> None:
        corpus = json.loads((TESTS_DIR / "corpus.json").read_text())
        golden = json.loads((TESTS_DIR / "golden" / "corpus.json").read_text())
        diffs = compare(golden, run_ported(corpus))
        self.assertEqual([], diffs, describe(diffs))

    def test_fuzz_matches_golden(self) -> None:
        golden = json.loads((TESTS_DIR / "golden" / "fuzz.json").read_text())
        actual = run_ported(build_cases())
        # the golden has the rendered-graph fields stripped to keep it small
        for case in actual:
            for key in ("inputs", "code_point_inputs", "steps"):
                for entry in case.get(key, []):
                    entry.pop("graph", None)
                    entry.pop("graphColored", None)
        diffs = compare(golden, actual)
        self.assertEqual([], diffs, describe(diffs))

    def test_golden_covers_accepting_and_rejecting_states(self) -> None:
        """Guard against a golden that only records failures (which would pass trivially)."""
        golden = json.loads((TESTS_DIR / "golden" / "corpus.json").read_text())
        entries = [
            entry
            for case in golden
            for key in ("inputs", "code_point_inputs", "steps")
            for entry in case.get(key, [])
        ]
        self.assertGreater(sum(1 for e in entries if e["ok"]), 50)
        self.assertGreater(sum(1 for e in entries if not e["ok"]), 10)


class KnownDeviationTest(unittest.TestCase):
    def test_missing_root_raises_grammar_parse_error(self) -> None:
        from gbnf import GBNF, GrammarParseError

        with self.assertRaises(GrammarParseError) as ctx:
            GBNF('foo ::= "a"')
        self.assertIn("does not contain a root symbol", str(ctx.exception))


@unittest.skipIf(node_version() is None, "node is not available")
class LiveDifferentialTest(unittest.TestCase):
    """Re-run the reference under Node and compare, in case the goldens are stale."""

    reference_dir: Path
    _tmp: "tempfile.TemporaryDirectory[str]"

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.reference_dir = prepare(Path(cls._tmp.name) / "reference")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _run_reference(self, corpus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(corpus, handle)
            corpus_path = handle.name
        result = subprocess.run(
            [
                "node",
                "--experimental-transform-types",
                "--disable-warning=ExperimentalWarning",
                str(TESTS_DIR / "differential" / "run_reference.ts"),
                str(self.reference_dir),
                corpus_path,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.skipTest(f"could not run the reference under node:\n{result.stderr}")
        return json.loads(result.stdout)

    def test_corpus_matches_live_reference(self) -> None:
        corpus = json.loads((TESTS_DIR / "corpus.json").read_text())
        diffs = compare(self._run_reference(corpus), run_ported(corpus))
        self.assertEqual([], diffs, describe(diffs))


if __name__ == "__main__":
    unittest.main()
