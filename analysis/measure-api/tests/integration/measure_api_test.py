import json
import shutil
import subprocess

import pytest

DIRECTORIES = {"python": "python", "typescript": "javascript"}
TYPES = {"python": ("RuleChar", "RuleEnd"), "typescript": ("char", "end")}


def tree(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes() for p in directory.rglob("*") if p.is_file()}


def records(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write_records(path, cases):
    path.write_text("".join(json.dumps({"grammar": "g0000", "input": i, "steps": s, "crash": None}) + "\n" for i, s in enumerate(cases)))
    return path


def rules(language, seen):
    char, end = TYPES[language]
    return [{"type": char, "value": [ord(c) for c in seen]}, {"type": end, "value": None}]


def describe_generate():
    def it_writes_the_same_corpus_for_the_same_seed(run_cli, tmp_path):
        assert run_cli("generate", "--out", tmp_path / "a", "--seed", 5, "--count", 10).returncode == 0
        assert run_cli("generate", "--out", tmp_path / "b", "--seed", 5, "--count", 10).returncode == 0
        assert tree(tmp_path / "a") == tree(tmp_path / "b")

    def it_regenerates_the_committed_corpus_from_its_manifest(run_cli, committed_corpus, tmp_path):
        manifest = json.loads((committed_corpus / "manifest.json").read_text())
        run_cli("generate", "--out", tmp_path, "--seed", manifest["seed"], "--count", manifest["count"])
        committed = {k: v for k, v in tree(committed_corpus).items() if not k.startswith("reference-")}
        assert tree(tmp_path) == committed


@pytest.mark.parametrize("language", ["python", "typescript"])
def describe_run():
    def it_records_every_step_and_stops_a_prefix_path_at_its_first_error(run_cli, make_corpus, implementations, tmp_path, language):
        corpus = make_corpus("ok", ["ab", "a!c"])
        result = run_cli("run", "--corpus", corpus, "--implementation", implementations[language], "--language", language, "--out", tmp_path / "o.jsonl")
        assert result.returncode == 0, result.stderr
        assert records(tmp_path / "o.jsonl") == [
            {"grammar": "g0000", "input": 0, "crash": None, "steps": [
                {"step": "construct", "rules": rules(language, "")},
                {"step": "whole", "rules": rules(language, "ab")},
                {"step": "prefix 1", "rules": rules(language, "a")},
                {"step": "prefix 2", "rules": rules(language, "ab")},
            ]},
            {"grammar": "g0000", "input": 1, "crash": None, "steps": [
                {"step": "construct", "rules": rules(language, "")},
                {"step": "whole", "error": {"class": "InputParseError", "pos": 1}},
                {"step": "prefix 1", "rules": rules(language, "a")},
                {"step": "prefix 2", "error": {"class": "InputParseError", "pos": 0}},
            ]},
        ]

    def it_records_an_error_without_a_position_and_stops_at_construction(run_cli, make_corpus, implementations, tmp_path, language):
        run_cli("run", "--corpus", make_corpus("error", ["a"]), "--implementation", implementations[language], "--language", language, "--out", tmp_path / "o.jsonl")
        [record] = records(tmp_path / "o.jsonl")
        assert record["steps"] == [{"step": "construct", "error": {"class": {"python": "ValueError", "typescript": "TypeError"}[language], "pos": None}}]

    def it_calls_a_non_zero_exit_a_crash(run_cli, make_corpus, implementations, tmp_path, language):
        run_cli("run", "--corpus", make_corpus("exit", ["a"]), "--implementation", implementations[language], "--language", language, "--out", tmp_path / "o.jsonl")
        [record] = records(tmp_path / "o.jsonl")
        assert record["steps"] is None
        assert record["crash"]

    def it_calls_a_hang_a_crash(run_cli, make_corpus, implementations, tmp_path, language):
        run_cli("run", "--corpus", make_corpus("hang", ["a"]), "--implementation", implementations[language], "--language", language, "--out", tmp_path / "o.jsonl")
        [record] = records(tmp_path / "o.jsonl")
        assert record["steps"] is None
        assert "timed out" in record["crash"]

    def it_leaves_no_process_behind_after_a_hang(run_cli, make_corpus, implementations, tmp_path, language):
        implementation = shutil.copytree(implementations[language], tmp_path / "hanging")
        run_cli("run", "--corpus", make_corpus("hang", ["a"]), "--implementation", implementation, "--language", language, "--out", tmp_path / "o.jsonl")
        survivors = subprocess.run(["pgrep", "-f", str(implementation)], capture_output=True, text=True).stdout.split()
        subprocess.run(["kill", "-9", *survivors])
        assert survivors == []

    def it_calls_an_implementation_that_does_not_load_a_crash(run_cli, make_corpus, tmp_path, language):
        (tmp_path / "empty" / "src").mkdir(parents=True)
        run_cli("run", "--corpus", make_corpus("ok", ["a"]), "--implementation", tmp_path / "empty", "--language", language, "--out", tmp_path / "o.jsonl")
        assert records(tmp_path / "o.jsonl")[0]["steps"] is None


def describe_compare():
    def it_writes_agreement_outcomes_and_the_confusion_table(run_cli, tmp_path):
        ok = [{"step": "construct", "rules": []}]
        other = [{"step": "construct", "rules": [{"type": "end", "value": None}]}]
        reference = write_records(tmp_path / "r.jsonl", [ok, ok])
        port = write_records(tmp_path / "p.jsonl", [ok, other])
        result = run_cli("compare", "--reference", reference, "--port", port, "--out", tmp_path / "c.json")
        assert result.returncode == 0, result.stderr
        report = json.loads((tmp_path / "c.json").read_text())
        assert (report["cases"], report["agreements"], report["agreement_rate"]) == (2, 1, 0.5)
        assert (report["outcomes"]["match"], report["outcomes"]["mismatch"], report["confusion"]["ok"]["ok"]) == (1, 1, 2)
        assert report["disagreements"][0]["step"] == 0

    def it_fails_on_output_files_over_different_cases(run_cli, tmp_path):
        ok = [{"step": "construct", "rules": []}]
        reference = write_records(tmp_path / "r.jsonl", [ok])
        port = write_records(tmp_path / "p.jsonl", [ok, ok])
        result = run_cli("compare", "--reference", reference, "--port", port, "--out", tmp_path / "c.json")
        assert result.returncode != 0
        assert "different cases" in result.stderr


@pytest.mark.parametrize("language", ["python", "typescript"])
def describe_reference():
    def it_reproduces_the_committed_reference_outputs(run_cli, reference_checkout, committed_corpus, tmp_path, language):
        out = tmp_path / "outputs.jsonl"
        result = run_cli("run", "--corpus", committed_corpus, "--implementation", reference_checkout / DIRECTORIES[language], "--language", language, "--out", out)
        assert result.returncode == 0, result.stderr
        run_cli("compare", "--reference", committed_corpus / f"reference-{language}.jsonl", "--port", out, "--out", tmp_path / "c.json")
        assert json.loads((tmp_path / "c.json").read_text())["agreement_rate"] == 1.0
