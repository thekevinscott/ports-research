import json

from src.matrix_run_ids import matrix_run_ids


def describe_matrix_run_ids():
    def it_takes_the_run_id_from_each_recorded_directory_across_logs(tmp_path):
        (tmp_path / "a.jsonl").write_text(
            json.dumps({"run_directory": "/w/one/data/runs/20261012T021310Z_60f23495"}) + "\n"
            + json.dumps({"run_directory": None, "exit_code": 1}) + "\n\n"
        )
        (tmp_path / "b.jsonl").write_text(json.dumps({"run_directory": "/w/two/data/runs/20261012T094953Z_370ab98a"}) + "\n")
        assert matrix_run_ids(tmp_path, ["a.jsonl", "b.jsonl"]) == {
            "20261012T021310Z_60f23495",
            "20261012T094953Z_370ab98a",
        }
