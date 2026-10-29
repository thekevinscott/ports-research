"""How each TypeScript→Python port defines RuleEnd, next to its held-out driver status.

The Python driver does `from gbnf import RuleEnd` and `isinstance(rule, RuleEnd)`; the
TypeScript driver duck-types `rule.type === "end"`. This script classifies the Python
ports so the two can be compared.
"""

import argparse
import csv
import re
from pathlib import Path

FIELDS = ["run_id", "model", "effort", "status", "definition", "exported"]


def classify(port: Path) -> tuple[str, str]:
    text = "\n".join(p.read_text(errors="ignore") for p in port.rglob("*.py") if "test" not in p.name)
    match = re.search(r"class RuleEnd\(([^)]*)\)", text)
    if match:
        definition = "TypedDict" if "TypedDict" in match.group(1) else "class"
    elif re.search(r"^\s*RuleEnd\s*(:|=)", text, re.M):
        definition = "alias"
    elif "RuleEnd" in text:
        definition = "mentioned only"
    else:
        definition = "absent"
    init = port / "gbnf" / "__init__.py"
    exported = "no gbnf/__init__.py" if not init.exists() else ("yes" if "RuleEnd" in init.read_text(errors="ignore") else "no")
    return definition, exported


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", type=Path, required=True, help="models-effort-status.csv")
    parser.add_argument("--runs-root", type=Path, required=True, help=".../experiments/v2-models-effort/runs")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for row in csv.DictReader(args.status.open()):
        if not row["direction"].startswith("javascript"):
            continue
        definition, exported = classify(args.runs_root / row["run_id"] / "ported_implementation")
        rows.append({"run_id": row["run_id"], "model": row["model"], "effort": row["effort"], "status": row["status"], "definition": definition, "exported": exported})
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} rows -> {args.output}")


if __name__ == "__main__":
    main()
