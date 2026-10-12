import json
import shutil
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
# A V2 run: javascript source, both integration suites shipped, exit 0. Its transcript is
# committed beside its manifest; the run layout is assembled in a temporary directory.
FIXTURE = PACKAGE_ROOT / "tests" / "fixtures" / "20261012T042251Z_7afe691e"


def run_cli(*args):
    return subprocess.run(["uv", "run", "measure-transcript", *map(str, args)], cwd=PACKAGE_ROOT, capture_output=True, text=True)


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    run = tmp_path_factory.mktemp("run")
    shutil.copy(FIXTURE / "manifest.json", run / "manifest.json")
    transcripts = run / "transcript" / ".claude" / "projects" / "-target"
    transcripts.mkdir(parents=True)
    shutil.copy(FIXTURE / "transcript.jsonl", transcripts / "aabaa9ad-c4f4-4b2a-9d05-ac49ae9614c5.jsonl")
    return run


@pytest.fixture(scope="module")
def report(run):
    result = run_cli("--run", run)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def describe_measure_transcript():
    def it_counts_turns_and_tool_calls(report):
        assert {k: report[k] for k in ("turns", "bash_calls", "read_calls", "write_calls", "edit_calls", "search_calls")} == {
            "turns": 43, "bash_calls": 40, "read_calls": 1, "write_calls": 1, "edit_calls": 0, "search_calls": 0,
        }

    def it_counts_reads_of_the_reference_and_its_suites(report):
        assert (report["read_source"], report["read_source_tests"], report["read_target_tests"]) == (3, 3, 10)
        assert (report["touched_source_tests"], report["touched_target_tests"]) == (True, True)

    def it_lists_suite_runs_with_their_class_and_counts(report):
        assert report["suite_run_count"] == 5
        assert report["suite_runs"][1] == {
            "turn": 14,
            "command": "PYTHONPATH=/target pytest tests/generated -q -p no:cacheprovider",
            "suite": "target_tests",
            "passed": 320,
            "failed": 0,
        }
        assert report["last_suite_counts"]["target_tests"] == {"passed": 320, "failed": 0}
        assert report["last_suite_run_turn"] == 41

    def it_lists_the_agents_own_test_files(report):
        assert report["own_test_files"] == ["/target/tests/extra/grammars_test.py"]

    def it_quotes_the_first_differential_script(report):
        assert report["differential_script"] is True
        assert report["differential_evidence"]["turn"] == 20
        assert report["differential_evidence"]["command"].startswith("mkdir -p /tmp/diff && cd /tmp/diff")

    def it_sums_tokens_and_splits_them_at_the_first_write(report):
        assert {k: report[k] for k in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens")} == {
            "input_tokens": 86, "output_tokens": 43954, "cache_read_tokens": 3258591, "cache_creation_tokens": 398443,
        }
        assert (report["first_write_turn"], report["tokens_before_first_write"], report["tokens_after_first_write"]) == (9, 296468, 3404606)

    def it_finds_no_fetch_attempts(report):
        assert (report["fetch_attempts"], report["fetch_commands"]) == (0, [])

    def it_exits_non_zero_without_a_transcript(tmp_path):
        shutil.copy(FIXTURE / "manifest.json", tmp_path / "manifest.json")
        result = run_cli("--run", tmp_path)
        assert result.returncode != 0
        assert "no transcript" in result.stderr


def describe_reading_order():
    def it_names_the_first_read_and_the_source_read_order(report):
        assert (report["first_read_path"], report["first_read_class"]) == ("/input/*.md", "other")
        assert report["read_order"] == ["/input/javascript/README.md", "/input/javascript/package.json", "/input/javascript/src/$f"]
        # The source is read through a `for f in ...; do cat $f` loop: no code file is named.
        assert report["first_read_is_entry_point"] is None

    def it_counts_files_read_before_the_first_write(report):
        assert (report["files_read_before_first_write"], report["source_files_read_before_first_write"]) == (15, 3)

    def it_counts_rereads(report):
        assert (report["reread_count"], report["max_rereads_of_one_file"]) == (12, 3)
        assert report["max_rereads_path"] == "/tmp/claude-1000/-target/*/tasks/bxqix6v8j.output"

    def it_relates_searches_and_late_reads(report):
        assert (report["search_calls_per_file_read"], report["reads_after_last_write"]) == (0.0, 0)
