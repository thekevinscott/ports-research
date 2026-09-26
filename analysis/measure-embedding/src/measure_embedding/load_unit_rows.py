import json
from pathlib import Path

import numpy as np


def load_unit_rows(directory: Path) -> np.ndarray:
    index = json.loads((directory / "index.json").read_text())
    rows = np.stack([np.load(directory / f"{name}.npy") for name in index["files"]]).astype(np.float64)
    return rows / np.linalg.norm(rows, axis=1, keepdims=True)
