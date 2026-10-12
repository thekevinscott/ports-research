import json
import shutil

import pytest

# Real claude calls on the subscription; CI has no claude.
pytestmark = pytest.mark.skipif(shutil.which("claude") is None, reason="claude CLI absent")
SECTIONS = ("happy_path", "error_paths", "invariants")


def describe_reference_lines():
    def it_explains_both_pinned_references_twice_and_compares_them(run_cli, out, alignment):
        result = run_cli("reference-lines", "--out", out, *alignment)
        assert result.returncode == 0, result.stderr
        lines = json.loads((out / "reference-lines.json").read_text())
        for name, tags in lines["walkthroughs"].items():
            for tag in ("a", "b"):
                written = json.loads((out / tags[tag]).read_text())
                assert (written["tag"], written["model"], written["effort"]) == (tag, "claude-opus-5-5", "high")
                assert written["walkthrough"]["entry_points"], name
                for entry in written["walkthrough"]["entry_points"]:
                    assert all(isinstance(step, str) for section in SECTIONS for step in entry[section])
        for compared in [*lines["noise_floor"].values(), *lines["baseline"].values()]:
            assert compared["entry_points_matched"] > 0
            assert 0 <= compared["mean_coverage"] <= 1
