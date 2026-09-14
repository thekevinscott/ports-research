import json
from pathlib import Path


def write_cases(cases: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(case) + "\n" for case in cases))
