import json
import os
from pathlib import Path

import numpy as np
import pytest

from measure_embedding.embed_codebase import embed_codebase

EXCLUDE = ["*_test.py", "build"]


class FakeEmbedder:
    def __init__(self):
        self.calls = []

    def __call__(self, source: Path, output: Path, *, model: str) -> None:
        self.calls.append((source, output, model))
        np.save(output, np.array([1.0, 2.0, 3.0], dtype=np.float32))


@pytest.fixture
def embedder():
    return FakeEmbedder()


@pytest.fixture
def python_tree(tmp_path: Path) -> Path:
    target = tmp_path / "target"
    (target / "pkg").mkdir(parents=True)
    (target / "pkg" / "a.py").write_text("a = 1\n")
    (target / "pkg" / "b.py").write_text("b = 2\n")
    (target / "pkg" / "a_test.py").write_text("t = 1\n")
    (target / "pkg" / "notes.md").write_text("not code")
    (target / "build").mkdir()
    (target / "build" / "c.py").write_text("c = 3\n")
    (target / "top.ts").write_text("const t = 1;\n")
    return target


@pytest.fixture
def out(tmp_path: Path) -> Path:
    return tmp_path / "out"


def embed(python_tree, out, embedder, **overrides):
    return embed_codebase(
        **{
            "language": "python",
            "target": python_tree,
            "exclude": EXCLUDE,
            "out": out,
            "model": "m",
            "embed": embedder,
            **overrides,
        }
    )


def describe_embed_codebase():
    def it_embeds_each_counted_file_to_a_mirrored_npy_path(python_tree, out, embedder):
        embed(python_tree, out, embedder)
        assert [c[0] for c in embedder.calls] == [python_tree / "pkg" / "a.py", python_tree / "pkg" / "b.py"]
        assert [c[1] for c in embedder.calls] == [out / "pkg" / "a.py.npy", out / "pkg" / "b.py.npy"]

    def it_passes_the_model_to_the_embedder(python_tree, out, embedder):
        embed(python_tree, out, embedder)
        assert {c[2] for c in embedder.calls} == {"m"}

    def it_embeds_ts_and_tsx_for_typescript(python_tree, out, embedder):
        (python_tree / "view.tsx").write_text("const v = 1;\n")
        embed(python_tree, out, embedder, language="typescript")
        assert [c[0].name for c in embedder.calls] == ["top.ts", "view.tsx"]

    def it_writes_an_index_of_files_lengths_model_and_dims(python_tree, out, embedder):
        embed(python_tree, out, embedder)
        assert json.loads((out / "index.json").read_text()) == {
            "language": "python",
            "target": str(python_tree),
            "model": "m",
            "dims": 3,
            "files": ["pkg/a.py", "pkg/b.py"],
            "lengths": [6, 6],
        }

    def it_returns_the_index_with_embedded_and_skipped_counts(python_tree, out, embedder):
        report = embed(python_tree, out, embedder)
        assert report["files"] == ["pkg/a.py", "pkg/b.py"]
        assert (report["embedded"], report["skipped"]) == (2, 0)

    def it_skips_a_file_whose_npy_is_newer_than_the_source(python_tree, out, embedder):
        embed(python_tree, out, embedder)
        embedder.calls.clear()
        report = embed(python_tree, out, embedder)
        assert embedder.calls == []
        assert (report["embedded"], report["skipped"]) == (0, 2)

    def it_re_embeds_a_file_whose_source_is_newer_than_its_npy(python_tree, out, embedder):
        embed(python_tree, out, embedder)
        embedder.calls.clear()
        stale = out / "pkg" / "a.py.npy"
        os.utime(stale, (0, 0))
        embed(python_tree, out, embedder)
        assert [c[0].name for c in embedder.calls] == ["a.py"]

    def it_still_lists_skipped_files_in_the_index(python_tree, out, embedder):
        embed(python_tree, out, embedder)
        embed(python_tree, out, embedder)
        assert json.loads((out / "index.json").read_text())["files"] == ["pkg/a.py", "pkg/b.py"]

    def it_raises_when_no_file_is_counted(tmp_path, out, embedder):
        with pytest.raises(FileNotFoundError, match="no python source"):
            embed(tmp_path, out, embedder)
        assert embedder.calls == []


def describe_strip_comments():
    def it_embeds_the_source_file_itself_by_default(python_tree, out, embedder):
        (python_tree / "pkg" / "a.py").write_text("a = 1  # note\n")
        embed(python_tree, out, embedder)
        assert embedder.calls[0][0] == python_tree / "pkg" / "a.py"
        assert list(out.rglob("*.stripped")) == []

    def it_embeds_the_stripped_text_written_beside_the_vector(python_tree, out, embedder):
        (python_tree / "pkg" / "a.py").write_text("a = 1  # note\n")
        embed(python_tree, out, embedder, strip_comments=True)
        assert embedder.calls[0][0] == out / "pkg" / "a.py.stripped"
        assert (out / "pkg" / "a.py.stripped").read_text() == "a = 1  \n"

    def it_counts_index_lengths_from_the_stripped_text(python_tree, out, embedder):
        (python_tree / "pkg" / "a.py").write_text("a = 1  # note\n")
        embed(python_tree, out, embedder, strip_comments=True)
        assert json.loads((out / "index.json").read_text())["lengths"] == [8, 6]

    def it_still_skips_a_file_whose_npy_is_newer_than_the_source(python_tree, out, embedder):
        embed(python_tree, out, embedder, strip_comments=True)
        embedder.calls.clear()
        report = embed(python_tree, out, embedder, strip_comments=True)
        assert embedder.calls == []
        assert (report["embedded"], report["skipped"]) == (0, 2)

    def it_still_lists_a_skipped_file_length_in_the_index(python_tree, out, embedder):
        embed(python_tree, out, embedder, strip_comments=True)
        embed(python_tree, out, embedder, strip_comments=True)
        assert json.loads((out / "index.json").read_text())["lengths"] == [6, 6]
