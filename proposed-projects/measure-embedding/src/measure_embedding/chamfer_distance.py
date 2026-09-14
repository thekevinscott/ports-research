import numpy as np


def chamfer_distance(
    rows_a: np.ndarray, rows_b: np.ndarray, weights_a: np.ndarray, weights_b: np.ndarray
) -> dict:
    similarities = rows_a @ rows_b.T
    a_to_b = float(np.average(1 - similarities.max(axis=1), weights=weights_a))
    b_to_a = float(np.average(1 - similarities.max(axis=0), weights=weights_b))
    return {
        "chamfer_distance": (a_to_b + b_to_a) / 2,
        "chamfer_a_to_b": a_to_b,
        "chamfer_b_to_a": b_to_a,
        "file_count_a": int(rows_a.shape[0]),
        "file_count_b": int(rows_b.shape[0]),
    }
