import json

import numpy as np
import pytest

from src.Codebase import EMBEDDING_MODEL
from src.embedding_pairs import validate_cache


@pytest.fixture
def cached_tree(tmp_path):
    source = tmp_path / "source"
    cache = tmp_path / "cache"
    source.mkdir()
    cache.mkdir()
    text = b"value = 1\n"
    (source / "main.py").write_bytes(text)
    (cache / "main.py.stripped").write_bytes(text)
    np.save(cache / "main.py.npy", np.array([1.0, 0.0]))
    (cache / "index.json").write_text(json.dumps({
        "language": "python", "model": EMBEDDING_MODEL, "dims": 2,
        "files": ["main.py"], "lengths": [len(text)],
    }))
    return source, cache


def test_cache_fingerprint_changes_when_vector_changes(cached_tree):
    source, cache = cached_tree
    before = validate_cache(cache, source, "python", [])
    np.save(cache / "main.py.npy", np.array([0.0, 1.0]))
    after = validate_cache(cache, source, "python", [])
    assert before["sha256"] != after["sha256"]


def test_cache_rejects_changed_source_even_with_existing_vectors(cached_tree):
    source, cache = cached_tree
    (source / "main.py").write_text("value = 2\n")
    with pytest.raises(ValueError, match="stripped content differs"):
        validate_cache(cache, source, "python", [])


def test_cache_rejects_incomplete_file_selection(cached_tree):
    source, cache = cached_tree
    (source / "extra.py").write_text("extra = 1\n")
    with pytest.raises(ValueError, match="file selection differs"):
        validate_cache(cache, source, "python", [])


def test_cache_rejects_nonfinite_vectors(cached_tree):
    source, cache = cached_tree
    np.save(cache / "main.py.npy", np.array([float("nan"), 0.0]))
    with pytest.raises(ValueError, match="invalid vector"):
        validate_cache(cache, source, "python", [])
