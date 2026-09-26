from pathlib import Path

import numpy as np


def write_vector(path: Path, embedding: list[float]) -> None:
    """Write embedding to path as a float32 .npy array — numpy's own format, exact and round-trippable with np.load."""
    np.save(path, np.array(embedding, dtype=np.float32))
