import json
import os
import subprocess
from itertools import chain
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args) -> dict:
    result = subprocess.run(
        ["uv", "run", "measure-embedding", *args],
        cwd=PACKAGE_ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def embed(language: str, target: Path, exclude: list[str], out: Path, model: str) -> dict:
    return run_cli(
        "embed", "--language", language, "--target", str(target), "--out", str(out), "--model", model,
        *chain.from_iterable(("--exclude", pattern) for pattern in exclude),
    )


@pytest.fixture(scope="session")
def embedded_references(tmp_path_factory, python_reference, typescript_reference, exclude_by_language, model):
    out = tmp_path_factory.mktemp("embeddings")
    return {
        "python": (embed("python", python_reference, exclude_by_language["python"], out / "python", model), out / "python"),
        "typescript": (
            embed("typescript", typescript_reference, exclude_by_language["typescript"], out / "typescript", model),
            out / "typescript",
        ),
    }


def describe_measure_embedding():
    def it_embeds_kevins_python_reference(embedded_references, capsys):
        report, out = embedded_references["python"]
        assert report["embedded"] == len(report["files"]) > 0
        assert report["dims"] > 0
        assert len(list(out.rglob("*.npy"))) == len(report["files"])
        with capsys.disabled():
            print(f"\npython reference: files={len(report['files'])} model={report['model']} dims={report['dims']}")

    def it_embeds_kevins_typescript_reference(embedded_references, capsys):
        report, out = embedded_references["typescript"]
        assert report["embedded"] == len(report["files"]) > 0
        assert report["dims"] > 0
        assert len(list(out.rglob("*.npy"))) == len(report["files"])
        with capsys.disabled():
            print(f"\ntypescript reference: files={len(report['files'])} model={report['model']} dims={report['dims']}")

    def it_compares_the_two_references(embedded_references, capsys):
        python_out, typescript_out = embedded_references["python"][1], embedded_references["typescript"][1]
        report = run_cli("compare", "--a", str(python_out), "--b", str(typescript_out))
        assert 0 <= report["mean_cosine_distance"] <= 2
        assert 0 <= report["mean_nearest_file_distance"] <= 2
        assert report["file_count_a"] == len(embedded_references["python"][0]["files"])
        assert report["file_count_b"] == len(embedded_references["typescript"][0]["files"])
        with capsys.disabled():
            print(f"\npython vs typescript reference: {json.dumps(report)}")
