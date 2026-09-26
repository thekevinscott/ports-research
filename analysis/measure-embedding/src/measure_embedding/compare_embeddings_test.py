import json
from pathlib import Path

import numpy as np
import pytest

from measure_embedding.compare_embeddings import compare_embeddings


def write_embeddings(directory: Path, vectors: dict[str, list[float]], lengths: list[int] | None = None) -> Path:
    for relative, vector in vectors.items():
        path = directory / f"{relative}.npy"
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, np.array(vector, dtype=np.float32))
    index = {
        "language": "python",
        "target": "/t",
        "model": "m",
        "dims": len(next(iter(vectors.values()))),
        "files": list(vectors),
        "lengths": lengths or [1] * len(vectors),
    }
    (directory / "index.json").write_text(json.dumps(index))
    return directory


@pytest.fixture
def a(tmp_path):
    return write_embeddings(tmp_path / "a", {"pkg/a.py": [1, 0, 0], "pkg/b.py": [0, 1, 0]})


@pytest.fixture
def b(tmp_path):
    return write_embeddings(tmp_path / "b", {"c.py": [2, 0, 0]})


def describe_compare_embeddings():
    def it_reports_the_cosine_distance_between_centroids(a, b):
        assert compare_embeddings(a=a, b=b)["mean_cosine_distance"] == pytest.approx(1 - 2**-0.5)

    def it_reports_the_mean_distance_from_each_file_in_a_to_its_nearest_in_b(a, b):
        assert compare_embeddings(a=a, b=b)["mean_nearest_file_distance"] == pytest.approx(0.5)

    def it_is_not_symmetric_in_the_nearest_file_distance(a, b):
        assert compare_embeddings(a=b, b=a)["mean_nearest_file_distance"] == pytest.approx(0.0)

    def it_reports_the_chamfer_distance_in_both_directions_and_their_mean(a, b):
        report = compare_embeddings(a=a, b=b)
        assert report["chamfer_a_to_b"] == pytest.approx(0.5)
        assert report["chamfer_b_to_a"] == pytest.approx(0.0)
        assert report["chamfer_distance"] == pytest.approx(0.25)

    def it_weights_the_chamfer_mean_by_the_index_lengths(tmp_path, b):
        weighted = write_embeddings(tmp_path / "weighted", {"pkg/a.py": [1, 0, 0], "pkg/b.py": [0, 1, 0]}, [3, 1])
        report = compare_embeddings(a=weighted, b=b)
        assert report["chamfer_a_to_b"] == pytest.approx(0.25)
        assert report["chamfer_distance"] == pytest.approx(0.125)

    def it_reports_file_counts(a, b):
        report = compare_embeddings(a=a, b=b)
        assert (report["file_count_a"], report["file_count_b"]) == (2, 1)

    def it_reports_zero_distances_for_identical_embeddings(a):
        report = compare_embeddings(a=a, b=a)
        assert report["mean_cosine_distance"] == pytest.approx(0.0)
        assert report["mean_nearest_file_distance"] == pytest.approx(0.0)
        assert report["chamfer_distance"] == pytest.approx(0.0)

    def it_reads_only_the_files_listed_in_the_index(a, b):
        np.save(b / "stray.py.npy", np.array([0, 1, 0], dtype=np.float32))
        assert compare_embeddings(a=a, b=b)["mean_nearest_file_distance"] == pytest.approx(0.5)

    def it_raises_on_a_dims_mismatch(a, tmp_path):
        other = write_embeddings(tmp_path / "other", {"x.py": [1, 0]})
        with pytest.raises(ValueError, match="dims"):
            compare_embeddings(a=a, b=other)
