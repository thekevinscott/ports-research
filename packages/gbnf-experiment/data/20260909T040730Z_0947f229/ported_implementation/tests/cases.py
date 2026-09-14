"""Loads the case tables extracted from the generated JavaScript suite.

``fixtures/cases.json`` is produced by ``fixtures/extract.mjs`` straight from
/workspace/tests/javascript, so the Python suite runs the same cases as the
JavaScript one.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

_CASES = json.loads((Path(__file__).parent / 'fixtures' / 'cases.json').read_text())


def table(file: str, index: int = 0) -> List[Any]:
    """The ``index``-th ``test.for([...])`` table in the given test file."""
    return _CASES[file][index]
