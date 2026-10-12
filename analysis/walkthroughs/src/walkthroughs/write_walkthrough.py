import json
from pathlib import Path

from judge.judge_item import judge_item

from walkthroughs.build_prompt import build_prompt
from walkthroughs.content_hash import content_hash

SCHEMA = json.loads((Path(__file__).resolve().parents[2] / "prompts" / "walkthrough.schema.json").read_text())


def write_walkthrough(implementation: Path, *, language: str, out: Path, model: str, effort: str, tag: str) -> Path:
    """One claude call explaining one implementation, written to <out>/<content hash>.json; skipped when that file exists."""
    prompt, files = build_prompt(implementation, language)
    path = out / f"{content_hash(prompt, model, effort, tag)}.json"
    if path.exists():
        return path
    judged = judge_item(prompt, schema=SCHEMA, model=model, effort=effort)
    record = {
        "implementation": str(implementation),
        "language": language,
        "tag": tag,
        "model": model,
        "effort": effort,
        "files": files,
        "prompt_chars": len(prompt),
        "walkthrough": judged["verdicts"],
        "raw": judged["raw"],
        "usage": judged["usage"],
        "wall_seconds": judged["wall_seconds"],
    }
    out.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n")
    return path
