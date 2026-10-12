import json
import shutil

import pytest

# Real claude calls on the subscription; CI has no claude.
pytestmark = pytest.mark.skipif(shutil.which("claude") is None, reason="claude CLI absent")
EXPECTED = {"code": (4, 2), "transcript": (2, 0)}


def labels(verdict):
    return verdict if isinstance(verdict, list) else [verdict]


@pytest.mark.parametrize("rubric", ["code", "transcript"])
def describe_dry_run():
    def it_judges_the_baseline_and_each_run_with_verdicts_from_the_fixed_sets(run_cli, runs, out, schema, rubric):
        args = [x for run in runs for x in ("--runs", run)]
        result = run_cli("run", "--rubric", rubric, *args, "--out", out)
        assert result.returncode == 0, result.stderr
        manifest = json.loads((out / "manifest.json").read_text())
        judgments = [json.loads(line) for line in (out / "judgments.jsonl").read_text().splitlines()]
        entries = {i: e for i, e in manifest.items() if e["rubric"] == rubric}
        items, baselines = EXPECTED[rubric]
        assert (len(entries), sum(e["baseline"] for e in entries.values())) == (items, baselines)
        judged = [j for j in judgments if j["rubric"] == rubric]
        assert sorted(j["id"] for j in judged) == sorted(entries)
        for judgment in judged:
            for name, item in schema(rubric)["properties"].items():
                verdict = item["properties"]["verdict"]
                allowed = verdict.get("enum") or verdict["items"]["enum"]
                assert set(labels(judgment["verdicts"][name]["verdict"])) <= set(allowed)

    def it_reports_the_judgments(run_cli, out, rubric):
        result = run_cli("report", "--out", out)
        assert result.returncode == 0, result.stderr
        assert f"{rubric} structure" in result.stdout
