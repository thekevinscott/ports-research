import json
import os
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def python_tree(tmp_path: Path) -> Path:
    root = tmp_path.resolve() / "python"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "a.py").write_text("a = 1\n")
    (root / "pkg" / "b.py").write_text("b = 2\n")
    (root / "pkg" / "a_test.py").write_text("c = 3\n")
    (root / "pkg" / "notes.md").write_text("not code")
    (root / "build").mkdir()
    (root / "build" / "c.py").write_text("c = 3\n")
    (root / "top.ts").write_text("const t = 1;\n")
    return root


@pytest.fixture
def other_tree(tmp_path: Path) -> Path:
    root = tmp_path.resolve() / "other"
    root.mkdir()
    (root / "c.py").write_text("c = 3\n")
    return root


def embed_args(tree, out, language="python", strip_comments=False):
    return [
        "embed", "--language", language, "--target", str(tree), "--out", str(out), "--model", "m",
        "--exclude", "*_test.py", "--exclude", "build",
        *(["--strip-comments"] if strip_comments else []),
    ]


def describe_embed():
    def it_writes_one_npy_per_counted_file_at_the_mirrored_path(run_cli, python_tree, tmp_path):
        out = tmp_path / "out"
        result = run_cli(*embed_args(python_tree, out))
        assert result.returncode == 0, result.stderr
        assert sorted(p.relative_to(out).as_posix() for p in out.rglob("*.npy")) == ["pkg/a.py.npy", "pkg/b.py.npy"]
        loaded = np.load(out / "pkg" / "a.py.npy")
        assert loaded.dtype == np.float32
        np.testing.assert_allclose(loaded, [1.0, 0.0, 0.0])

    def it_writes_an_index_with_files_lengths_model_and_dims(run_cli, python_tree, tmp_path):
        out = tmp_path / "out"
        run_cli(*embed_args(python_tree, out))
        assert json.loads((out / "index.json").read_text()) == {
            "language": "python",
            "target": str(python_tree),
            "model": "m",
            "dims": 3,
            "files": ["pkg/a.py", "pkg/b.py"],
            "lengths": [6, 6],
        }

    def it_embeds_the_text_left_after_stripping_comments(run_cli, python_tree, tmp_path):
        (python_tree / "pkg" / "a.py").write_text("# note\na = 1\n")
        out = tmp_path / "out"
        result = run_cli(*embed_args(python_tree, out, strip_comments=True))
        assert result.returncode == 0, result.stderr
        assert (out / "pkg" / "a.py.stripped").read_text() == "\na = 1\n"
        np.testing.assert_allclose(np.load(out / "pkg" / "a.py.npy"), [1.0, 0.0, 0.0])

    def it_prints_the_index_with_embedded_and_skipped_counts(run_cli, python_tree, tmp_path):
        result = run_cli(*embed_args(python_tree, tmp_path / "out"))
        report = json.loads(result.stdout)
        assert report["files"] == ["pkg/a.py", "pkg/b.py"]
        assert (report["embedded"], report["skipped"]) == (2, 0)

    def it_embeds_ts_and_tsx_for_typescript(run_cli, python_tree, tmp_path):
        out = tmp_path / "out"
        result = run_cli(*embed_args(python_tree, out, language="typescript"))
        assert result.returncode == 0, result.stderr
        assert json.loads((out / "index.json").read_text())["files"] == ["top.ts"]

    def it_does_not_call_the_embedder_for_an_up_to_date_npy(run_cli, embeddings_server, python_tree, tmp_path):
        out = tmp_path / "out"
        run_cli(*embed_args(python_tree, out))
        calls_after_first = len(embeddings_server.log)
        result = run_cli(*embed_args(python_tree, out))
        assert len(embeddings_server.log) == calls_after_first
        assert (json.loads(result.stdout)["embedded"], json.loads(result.stdout)["skipped"]) == (0, 2)

    def it_re_embeds_a_source_newer_than_its_npy(run_cli, embeddings_server, python_tree, tmp_path):
        out = tmp_path / "out"
        run_cli(*embed_args(python_tree, out))
        os.utime(out / "pkg" / "a.py.npy", (0, 0))
        calls_after_first = len(embeddings_server.log)
        run_cli(*embed_args(python_tree, out))
        assert len(embeddings_server.log) == calls_after_first + 1

    def it_fails_with_a_message_when_no_file_is_counted(run_cli, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = run_cli(*embed_args(empty, tmp_path / "out"))
        assert result.returncode != 0
        assert result.stdout == ""
        assert "no python source" in result.stderr

    def it_fails_with_a_message_when_the_target_does_not_exist(run_cli, tmp_path):
        result = run_cli(*embed_args(tmp_path / "nowhere", tmp_path / "out"))
        assert result.returncode != 0
        assert "nowhere" in result.stderr


def describe_compare():
    def it_reports_centroid_and_nearest_file_distances_and_counts(run_cli, python_tree, other_tree, tmp_path):
        run_cli(*embed_args(python_tree, tmp_path / "a"))
        run_cli(*embed_args(other_tree, tmp_path / "b"))
        result = run_cli("compare", "--a", str(tmp_path / "a"), "--b", str(tmp_path / "b"))
        assert result.returncode == 0, result.stderr
        report = json.loads(result.stdout)
        assert set(report) == {
            "mean_cosine_distance",
            "mean_nearest_file_distance",
            "chamfer_distance",
            "chamfer_a_to_b",
            "chamfer_b_to_a",
            "file_count_a",
            "file_count_b",
        }
        assert report["mean_cosine_distance"] == pytest.approx(1 - 2**-0.5)
        assert report["mean_nearest_file_distance"] == pytest.approx(0.5)
        assert report["chamfer_a_to_b"] == pytest.approx(0.5)
        assert report["chamfer_b_to_a"] == pytest.approx(0.0)
        assert report["chamfer_distance"] == pytest.approx(0.25)
        assert (report["file_count_a"], report["file_count_b"]) == (2, 1)

    def it_reports_zero_distances_for_the_same_directory(run_cli, python_tree, tmp_path):
        run_cli(*embed_args(python_tree, tmp_path / "a"))
        result = run_cli("compare", "--a", str(tmp_path / "a"), "--b", str(tmp_path / "a"))
        report = json.loads(result.stdout)
        assert report["mean_cosine_distance"] == pytest.approx(0.0)
        assert report["mean_nearest_file_distance"] == pytest.approx(0.0)
        assert report["chamfer_distance"] == pytest.approx(0.0)

    def it_fails_with_a_message_when_a_directory_does_not_exist(run_cli, tmp_path):
        result = run_cli("compare", "--a", str(tmp_path / "nowhere"), "--b", str(tmp_path / "nowhere"))
        assert result.returncode != 0
        assert "nowhere" in result.stderr
