import json
from pathlib import Path


def read_adapt_report(path: Path) -> tuple[str, ...]:
    """The rules a shim recorded, or none if the suite never loaded the shim."""
    if not path.is_file():
        return ()
    return tuple(json.loads(path.read_text())["rules_fired"])
