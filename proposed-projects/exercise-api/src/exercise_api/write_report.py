import json
from pathlib import Path


def write_report(path: Path, report: dict) -> None:
    staging = path.with_name(path.name + ".tmp")
    staging.write_text(json.dumps(report))
    staging.replace(path)
