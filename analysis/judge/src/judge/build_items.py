import json
from pathlib import Path

from judge.code_item import code_item
from judge.item_id import item_id
from judge.transcript_item import transcript_item

FLAGS = ("include_unit_tests", "include_source_integration_tests", "include_target_integration_tests")
OTHER = {"python": "javascript", "javascript": "python"}
TRANSCRIPTS = Path("transcript") / ".claude" / "projects" / "-target"


def build_items(*, rubric: str, runs: list[Path], reference: Path | None) -> list[dict]:
    """Every item for the rubric, each with its content, its opaque id and its private manifest entry.

    For the code rubric the human pair comes first, both ways, built the same way as every run.
    """

    def item(content: str, run: str | None, source: str, condition: dict) -> dict:
        entry = {"rubric": rubric, "run": run, "baseline": run is None, "source_language": source, "target_language": OTHER[source]}
        return {"id": item_id(content), "content": content, "entry": {**entry, **{flag: condition.get(flag) for flag in FLAGS}}}

    conditions = [(run, json.loads((run / "manifest.json").read_text())["condition"]) for run in runs]
    if rubric == "code":
        baseline = [item(code_item(reference / source, reference / OTHER[source]), None, source, {}) for source in ("python", "javascript")]
        return baseline + [
            item(code_item(reference / c["source_language"], run / "ported_implementation"), run.name, c["source_language"], c)
            for run, c in conditions
        ]
    if rubric == "transcript":
        return [item(transcript_item(sorted((run / TRANSCRIPTS).glob("*.jsonl"))), run.name, c["source_language"], c) for run, c in conditions]
    raise ValueError(f"unknown rubric {rubric!r}")
