import numpy as np

from generate_embedding.write_vector import write_vector


def describe_write_vector():
    def it_writes_a_float32_npy_array(tmp_path):
        path = tmp_path / "vec.npy"
        write_vector(path, [0.1, 0.2, 0.3])
        loaded = np.load(path)
        assert loaded.dtype == np.float32
        np.testing.assert_allclose(loaded, [0.1, 0.2, 0.3], rtol=1e-6)

    def it_does_not_double_the_npy_extension(tmp_path):
        path = tmp_path / "vec.npy"
        write_vector(path, [1.0])
        assert path.exists()
        assert not (tmp_path / "vec.npy.npy").exists()
