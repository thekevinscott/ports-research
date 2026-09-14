"""The 21 items of one direction as a similarity matrix, and the layouts fitted off it.

Similarity is a percentage, so distance is 100 minus similarity: a port 40% similar to
the reference sits 60 units away from it.
"""

import numpy as np
import polars as pl
from scipy.optimize import minimize
from sklearn.manifold import MDS

REFERENCE_ID = "reference"
FULL = 100.0
TURN = 2 * np.pi


def similarity_matrix(pairs, ports, reference_id=REFERENCE_ID):
    """Run ids and their symmetric similarity matrix, the reference last, diagonal 100.

    `pairs` holds each unordered port pair once, `ports` one row per port with the
    similarity to the reference the run frame already carries.
    """
    ids = [*ports["run_id"], reference_id]
    index = {run_id: position for position, run_id in enumerate(ids)}
    matrix = np.full((len(ids), len(ids)), np.nan)
    np.fill_diagonal(matrix, FULL)
    measured = [
        *pairs.select("run_id_a", "run_id_b", "similarity_pct").iter_rows(),
        *(
            (run_id, reference_id, value)
            for run_id, value in ports.select("run_id", "reference_pct").iter_rows()
        ),
    ]
    for a, b, value in measured:
        matrix[index[a], index[b]] = matrix[index[b], index[a]] = value
    return ids, matrix


def distances(matrix):
    return FULL - matrix


def polar_distances(radii, angles):
    """Every pairwise distance between points given in polar coordinates, by the cosine rule."""
    squared = (
        radii[:, None] ** 2
        + radii[None, :] ** 2
        - 2 * np.outer(radii, radii) * np.cos(angles[:, None] - angles[None, :])
    )
    return np.sqrt(np.clip(squared, 0.0, None))


def focused_layout(ids, matrix, starts=20, seed=0):
    """Ports at their measured distance from the reference, with only the angles fitted.

    Returns the placed points, reference last at the origin, and the residual RMS in
    similarity points.
    """
    target = distances(matrix)
    radii = target[:-1, -1]
    upper = np.triu_indices(len(radii), 1)
    goal = target[:-1, :-1][upper]

    def cost(angles):
        residual = goal - polar_distances(radii, angles)[upper]
        return float(residual @ residual)

    rng = np.random.default_rng(seed)
    best = min(
        (minimize(cost, rng.uniform(0.0, TURN, len(radii))) for _ in range(starts)),
        key=lambda fit: fit.fun,
    )
    placed = pl.DataFrame(
        {
            "run_id": ids,
            "x": [*(radii * np.cos(best.x)), 0.0],
            "y": [*(radii * np.sin(best.x)), 0.0],
        }
    )
    return placed, float(np.sqrt(best.fun / len(goal)))


def mds_layout(ids, matrix, seed=0):
    """Every item placed by metric MDS over the measured distances, and the fitted stress."""
    mds = MDS(
        n_components=2,
        metric="precomputed",
        init="classical_mds",
        normalized_stress=True,
        random_state=seed,
    )
    coordinates = mds.fit_transform(distances(matrix))
    placed = pl.DataFrame(
        {"run_id": ids, "x": coordinates[:, 0], "y": coordinates[:, 1]}
    )
    return placed, float(mds.stress_)


def ring_points(levels, steps=180):
    """A closed polyline per ring, one ring per similarity level, in layout coordinates."""
    angles = np.linspace(0.0, TURN, steps + 1)
    return pl.DataFrame(
        [
            {
                "ring": f"{level}%",
                "step": step,
                "x": float((FULL - level) * np.cos(angle)),
                "y": float((FULL - level) * np.sin(angle)),
            }
            for level in levels
            for step, angle in enumerate(angles)
        ]
    )


def ring_labels(levels):
    """One label per ring, sitting at the top of it."""
    return pl.DataFrame(
        [{"ring": f"{level}%", "x": 0.0, "y": FULL - level} for level in levels]
    )


def medoid_similarity(ids, matrix, ports, group="condition"):
    """Each port against its group's medoid: the member closest to the rest of its group.

    The medoid's own row carries no value, since a port against itself is 100 by definition.
    """
    index = {run_id: position for position, run_id in enumerate(ids)}
    rows = []
    for _key, members in ports.group_by(group, maintain_order=True):
        positions = [index[run_id] for run_id in members["run_id"]]
        block = matrix[np.ix_(positions, positions)]
        medians = [np.median(np.delete(row, place)) for place, row in enumerate(block)]
        medoid = members["run_id"][int(np.argmax(medians))]
        rows.extend(
            {
                "run_id": run_id,
                "medoid": medoid,
                "medoid_similarity_pct": None
                if run_id == medoid
                else float(matrix[index[run_id], index[medoid]]),
            }
            for run_id in members["run_id"]
        )
    return pl.DataFrame(
        rows,
        schema={
            "run_id": pl.String,
            "medoid": pl.String,
            "medoid_similarity_pct": pl.Float64,
        },
    )
