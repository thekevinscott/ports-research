from unittest.mock import patch

import pytest

from generate_embedding.write_vector import write_vector


@pytest.fixture
def np():
    with patch("generate_embedding.write_vector.np") as mock_np:
        yield mock_np


def describe_write_vector():
    def it_converts_the_embedding_to_float32(np, tmp_path):
        write_vector(tmp_path / "vec.npy", [0.1, 0.2, 0.3])
        np.array.assert_called_once_with([0.1, 0.2, 0.3], dtype=np.float32)

    def it_saves_the_converted_array_at_the_path(np, tmp_path):
        path = tmp_path / "vec.npy"
        write_vector(path, [0.1])
        np.save.assert_called_once_with(path, np.array.return_value)
