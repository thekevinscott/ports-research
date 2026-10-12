import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from judge.build_items import build_items
from judge.clone_reference import clone_reference
from judge.find_runs import find_runs
from judge.judge_item import judge_item
from judge.shuffle_items import shuffle_items

RUBRICS = Path(__file__).resolve().parents[2] / "rubrics"


def run_judge(*, rubric: str, runs: list[Path], out: Path, limit: int | None, model: str, effort: str, concurrency: int) -> None:
    """Build the rubric's items blind, record the private manifest, and judge each item not yet in judgments.jsonl."""
    text = (RUBRICS / f"{rubric}.md").read_text()
    schema = json.loads((RUBRICS / f"{rubric}.schema.json").read_text())
    with TemporaryDirectory() as checkout:
        reference = clone_reference(Path(checkout)) if rubric == "code" else None
        items = shuffle_items(build_items(rubric=rubric, runs=find_runs(runs), reference=reference))[:limit]
    prompts = {item["id"]: f"{text}\n---\n\n{item['content']}" for item in items}

    out.mkdir(parents=True, exist_ok=True)
    manifest_path, judgments_path = out / "manifest.json", out / "judgments.jsonl"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for item in items:
        chars = len(prompts[item["id"]])
        manifest[item["id"]] = {**item["entry"], "prompt_chars": chars, "tokens_estimate": chars // 4}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    done = {json.loads(line)["id"] for line in judgments_path.read_text().splitlines()} if judgments_path.exists() else set()
    lock, failures = threading.Lock(), []

    def judge(item_id: str) -> None:
        try:
            judged = judge_item(prompts[item_id], schema=schema, model=model, effort=effort)
        except Exception as e:
            print(f"{item_id}: {e}", file=sys.stderr)
            failures.append(f"{item_id}: {e}")
            return
        line = {"id": item_id, "rubric": rubric, "model": model, "effort": effort, **judged}
        with lock, judgments_path.open("a") as f:
            f.write(json.dumps(line) + "\n")
        print(f"{item_id}: {judged['wall_seconds']}s", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(judge, [item["id"] for item in items if item["id"] not in done]))
    if failures:
        raise RuntimeError(f"{len(failures)} item(s) failed: " + "; ".join(failures))
