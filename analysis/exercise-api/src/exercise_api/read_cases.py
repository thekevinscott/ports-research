import json
from pathlib import Path

OPTIONAL = {"rung", "repeat", "warmup"}


def read_cases(path: Path) -> list[dict]:
    cases = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for case in cases:
        if not isinstance(case, dict) or set(case) - OPTIONAL != {"grammar", "input"}:
            raise ValueError(
                f"{path}: every case must be an object with grammar, input and an optional rung, repeat or warmup"
            )
    return cases
