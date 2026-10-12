import json
from pathlib import Path

from measure_api.classify_case import classify_case

OUTCOMES = ("match", "mismatch", "error_match", "error_mismatch", "crash")
AGREEMENTS = ("match", "error_match")
STATUSES = ("ok", "error", "crash")


def compare_cases(*, reference: Path, port: Path) -> dict:
    def read(path: Path) -> dict:
        records = (json.loads(line) for line in path.read_text().splitlines() if line.strip())
        return {(record["grammar"], record["input"]): record for record in records}

    def status(record: dict) -> str:
        if record["crash"] is not None:
            return "crash"
        return "error" if any("error" in step for step in record["steps"]) else "ok"

    def at(record: dict, step: int) -> dict | None:
        return record["steps"][step] if step < len(record["steps"]) else None

    expected, actual = read(reference), read(port)
    if expected.keys() != actual.keys():
        raise ValueError("reference and port outputs cover different cases")
    outcomes = dict.fromkeys(OUTCOMES, 0)
    confusion = {row: dict.fromkeys(STATUSES, 0) for row in STATUSES}
    disagreements = []
    for (grammar, index), record in sorted(expected.items()):
        other = actual[(grammar, index)]
        outcome, step = classify_case(record, other)
        outcomes[outcome] += 1
        confusion[status(record)][status(other)] += 1
        if step is not None:
            disagreements.append({"grammar": grammar, "input": index, "outcome": outcome, "step": step, "reference": at(record, step), "port": at(other, step)})
    agreements = sum(outcomes[outcome] for outcome in AGREEMENTS)
    return {
        "cases": len(expected),
        "agreements": agreements,
        "agreement_rate": agreements / len(expected) if expected else None,
        "outcomes": outcomes,
        "confusion": confusion,
        "disagreements": disagreements,
    }
