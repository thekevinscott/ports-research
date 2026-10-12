import json
from pathlib import Path

OUTCOMES = ("accept", "reject", "error", "crash")


def compare_outcomes(*, reference: Path, port: Path) -> dict:
    def read(path: Path) -> dict:
        records = (json.loads(line) for line in path.read_text().splitlines() if line.strip())
        return {(record["grammar"], record["input"]): record["outcome"] for record in records}

    expected, actual = read(reference), read(port)
    if expected.keys() != actual.keys():
        raise ValueError("reference and port outcomes cover different pairs")
    confusion = {row: dict.fromkeys(OUTCOMES, 0) for row in OUTCOMES}
    for key, outcome in expected.items():
        confusion[outcome][actual[key]] += 1
    agreements = sum(confusion[outcome][outcome] for outcome in OUTCOMES)
    return {
        "pairs": len(expected),
        "agreements": agreements,
        "agreement_rate": agreements / len(expected) if expected else None,
        "confusion": confusion,
    }
