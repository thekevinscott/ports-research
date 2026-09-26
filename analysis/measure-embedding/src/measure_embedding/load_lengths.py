import json
from pathlib import Path

import numpy as np


def load_lengths(directory: Path) -> np.ndarray:
    index = json.loads((directory / "index.json").read_text())
    return np.array(index["lengths"], dtype=np.float64)
