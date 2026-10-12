import json
import shutil
import subprocess

import pytest


def tree(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes() for p in directory.rglob("*") if p.is_file()}


def records(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write_records(path, outcomes):
    path.write_text("".join(json.dumps({"grammar": "g0000", "input": i, "outcome": o, "error": None}) + "\n" for i, o in enumerate(outcomes)))
    return path


def describe_generate():
    def it_writes_the_same_corpus_for_the_same_seed(run_cli, tmp_path):
        assert run_cli("generate", "--out", tmp_path / "a", "--seed", 5, "--count", 30).returncode == 0
        assert run_cli("generate", "--out", tmp_path / "b", "--seed", 5, "--count", 30).returncode == 0
        assert tree(tmp_path / "a") == tree(tmp_path / "b")

    def it_records_the_seed_in_the_manifest(run_cli, tmp_path):
        run_cli("generate", "--out", tmp_path, "--seed", 5, "--count", 3)
        assert json.loads((tmp_path / "manifest.json").read_text())["seed"] == 5

    def it_regenerates_the_committed_corpus_from_its_manifest(run_cli, committed_corpus, tmp_path):
        manifest = json.loads((committed_corpus / "manifest.json").read_text())
        run_cli("generate", "--out", tmp_path, "--seed", manifest["seed"], "--count", manifest["count"])
        committed = {k: v for k, v in tree(committed_corpus).items() if not k.startswith("reference-")}
        assert tree(tmp_path) == committed


@pytest.mark.parametrize("language", ["python", "typescript"])
def describe_run():
    def it_writes_one_outcome_per_pair(run_cli, make_corpus, implementations, tmp_path, language):
        corpus = make_corpus(["accept", "prefix", "reject", "error", "exit"])
        result = run_cli("run", "--corpus", corpus, "--implementation", implementations[language], "--language", language, "--out", tmp_path / "o.jsonl")
        assert result.returncode == 0, result.stderr
        written = records(tmp_path / "o.jsonl")
        assert [(r["grammar"], r["input"], r["outcome"]) for r in written] == [
            ("g0000", 0, "accept"),
            ("g0000", 1, "reject"),
            ("g0000", 2, "reject"),
            ("g0000", 3, "error"),
            ("g0000", 4, "crash"),
        ]
        assert [r["error"] for r in written[:2]] == [None, None]
        assert "rejected at 0" in written[2]["error"]
        assert "bad grammar" in written[3]["error"]

    def it_calls_a_hang_a_crash_and_moves_on(run_cli, make_corpus, implementations, tmp_path, language):
        corpus = make_corpus(["hang", "accept"])
        run_cli("run", "--corpus", corpus, "--implementation", implementations[language], "--language", language, "--out", tmp_path / "o.jsonl")
        written = records(tmp_path / "o.jsonl")
        assert [r["outcome"] for r in written] == ["crash", "accept"]
        assert "timed out" in written[0]["error"]

    def it_leaves_no_process_behind_after_a_hang(run_cli, make_corpus, implementations, tmp_path, language):
        implementation = shutil.copytree(implementations[language], tmp_path / "hanging")
        run_cli("run", "--corpus", make_corpus(["hang"]), "--implementation", implementation, "--language", language, "--out", tmp_path / "o.jsonl")
        survivors = subprocess.run(["pgrep", "-f", str(implementation)], capture_output=True, text=True).stdout.split()
        subprocess.run(["kill", "-9", *survivors])
        assert survivors == []

    def it_calls_an_implementation_that_does_not_load_a_crash(run_cli, make_corpus, tmp_path, language):
        corpus = make_corpus(["accept"])
        (tmp_path / "empty" / "src").mkdir(parents=True)
        run_cli("run", "--corpus", corpus, "--implementation", tmp_path / "empty", "--language", language, "--out", tmp_path / "o.jsonl")
        assert [r["outcome"] for r in records(tmp_path / "o.jsonl")] == ["crash"]


def describe_compare():
    def it_writes_agreement_and_the_confusion_table(run_cli, tmp_path):
        reference = write_records(tmp_path / "r.jsonl", ["accept", "reject", "error", "accept"])
        port = write_records(tmp_path / "p.jsonl", ["accept", "accept", "crash", "accept"])
        result = run_cli("compare", "--reference", reference, "--port", port, "--out", tmp_path / "c.json")
        assert result.returncode == 0, result.stderr
        report = json.loads((tmp_path / "c.json").read_text())
        assert (report["pairs"], report["agreements"], report["agreement_rate"]) == (4, 2, 0.5)
        assert report["confusion"]["reject"]["accept"] == 1
        assert report["confusion"]["error"]["crash"] == 1

    def it_agrees_fully_with_itself(run_cli, tmp_path):
        reference = write_records(tmp_path / "r.jsonl", ["accept", "reject", "error", "crash"])
        run_cli("compare", "--reference", reference, "--port", reference, "--out", tmp_path / "c.json")
        assert json.loads((tmp_path / "c.json").read_text())["agreement_rate"] == 1.0

    def it_fails_on_outcome_files_over_different_pairs(run_cli, tmp_path):
        reference = write_records(tmp_path / "r.jsonl", ["accept"])
        port = write_records(tmp_path / "p.jsonl", ["accept", "accept"])
        result = run_cli("compare", "--reference", reference, "--port", port, "--out", tmp_path / "c.json")
        assert result.returncode != 0
        assert "different pairs" in result.stderr
