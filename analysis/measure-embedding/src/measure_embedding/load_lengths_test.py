import json

import numpy as np
import pytest

from measure_embedding.load_lengths import load_lengths


@pytest.fixture
def directory(tmp_path):
    (tmp_path / "index.json").write_text(json.dumps({"files": ["pkg/a.py", "b.py"], "lengths": [10, 4]}))
    return tmp_path


def describe_load_lengths():
    def it_reads_the_lengths_in_index_order(directory):
        np.testing.assert_allclose(load_lengths(directory), [10, 4])

    def it_returns_float64(directory):
        assert load_lengths(directory).dtype == np.float64
