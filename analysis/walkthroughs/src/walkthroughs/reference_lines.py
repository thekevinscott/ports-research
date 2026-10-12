import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from judge.clone_reference import clone_reference

from walkthroughs.compare_walkthroughs import compare_walkthroughs
from walkthroughs.sweep_thresholds import sweep_thresholds
from walkthroughs.write_walkthrough import write_walkthrough

REFERENCES = {"python": "python", "javascript": "typescript"}
TAGS = ("a", "b")


def reference_lines(*, out: Path, similarity: dict, model: str, effort: str) -> dict:
    """Explain each pinned reference twice; compare each with itself (the noise floor) and the two with each other (the baseline)."""
    out.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as checkout:
        gbnf = clone_reference(Path(checkout))
        jobs = [(name, tag) for name in REFERENCES for tag in TAGS]
        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            paths = list(pool.map(
                lambda job: write_walkthrough(gbnf / job[0], language=REFERENCES[job[0]], out=out, model=model, effort=effort, tag=job[1]),
                jobs,
            ))
    path = dict(zip(jobs, paths))
    walkthrough = {job: json.loads(p.read_text())["walkthrough"] for job, p in path.items()}

    def compare(reference: tuple[str, str], port: tuple[str, str]) -> dict:
        pair = walkthrough[reference], walkthrough[port]
        return {**compare_walkthroughs(*pair, similarity), "sweep": sweep_thresholds(*pair, similarity)}

    lines = {
        "walkthroughs": {name: {tag: path[name, tag].name for tag in TAGS} for name in REFERENCES},
        "noise_floor": {name: compare((name, "a"), (name, "b")) for name in REFERENCES},
        "baseline": {
            "python_to_javascript": compare(("python", "a"), ("javascript", "a")),
            "javascript_to_python": compare(("javascript", "a"), ("python", "a")),
        },
    }
    (out / "reference-lines.json").write_text(json.dumps(lines, indent=2) + "\n")
    return lines
