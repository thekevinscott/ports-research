import json

import numpy as np
import pytest

from measure_embedding.load_unit_rows import load_unit_rows


@pytest.fixture
def directory(tmp_path):
    (tmp_path / "pkg").mkdir()
    np.save(tmp_path / "pkg" / "a.py.npy", np.array([3, 0, 0], dtype=np.float32))
    np.save(tmp_path / "b.py.npy", np.array([0, 0, 2], dtype=np.float32))
    np.save(tmp_path / "stray.py.npy", np.array([0, 1, 0], dtype=np.float32))
    (tmp_path / "index.json").write_text(json.dumps({"files": ["pkg/a.py", "b.py"]}))
    return tmp_path


def describe_load_unit_rows():
    def it_stacks_the_indexed_vectors_in_index_order(directory):
        assert load_unit_rows(directory).shape == (2, 3)
        np.testing.assert_allclose(load_unit_rows(directory)[0], [1, 0, 0])
        np.testing.assert_allclose(load_unit_rows(directory)[1], [0, 0, 1])

    def it_normalises_each_row_to_unit_length(directory):
        np.testing.assert_allclose(np.linalg.norm(load_unit_rows(directory), axis=1), [1, 1])

    def it_returns_float64(directory):
        assert load_unit_rows(directory).dtype == np.float64
