from pathlib import Path

import numpy as np

from .chamfer_distance import chamfer_distance
from .load_lengths import load_lengths
from .load_unit_rows import load_unit_rows


def cosine_distance(u: np.ndarray, v: np.ndarray) -> float:
    return float(1 - np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))


def compare_embeddings(*, a: Path, b: Path) -> dict:
    rows_a, rows_b = load_unit_rows(a), load_unit_rows(b)
    if rows_a.shape[1] != rows_b.shape[1]:
        raise ValueError(f"dims mismatch: {a} has {rows_a.shape[1]}, {b} has {rows_b.shape[1]}")
    similarities = rows_a @ rows_b.T
    return {
        "mean_cosine_distance": cosine_distance(rows_a.mean(axis=0), rows_b.mean(axis=0)),
        "mean_nearest_file_distance": float(np.mean(1 - similarities.max(axis=1))),
        **chamfer_distance(rows_a, rows_b, load_lengths(a), load_lengths(b)),
    }
