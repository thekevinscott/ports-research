"""Measure the handwritten reference the same way run_metrics.py measures a port.

  uv run --project <notebook> --locked python slides/2026-10-29-nyc-ai-coworking/scripts/reference_metrics.py \
    --notebook <notebook> --output slides/2026-10-29-nyc-ai-coworking/public/reference.json
"""

import argparse
import json
import sys
from pathlib import Path

NOTEBOOK = Path(sys.argv[sys.argv.index("--notebook") + 1]).resolve()
sys.path.insert(0, str(NOTEBOOK))

from src.Codebase import Codebase, pinned_reference  # noqa: E402
from src.corpus import EXCLUDE_BY_LANGUAGE, REFERENCE  # noqa: E402

DIRECTIONS = {"python→javascript": "javascript", "javascript→python": "python"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pinned_reference()
    metrics = {}
    for direction, target in DIRECTIONS.items():
        codebase = Codebase(REFERENCE / target, EXCLUDE_BY_LANGUAGE[target], language=target)
        metrics[direction] = {"file_count": codebase.file_count, "loc": codebase.loc}
    args.output.write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
