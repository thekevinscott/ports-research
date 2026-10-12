import json

from judge.find_runs import find_runs


def run(path, exit_code=0):
    path.mkdir(parents=True)
    (path / "manifest.json").write_text(json.dumps({"exit_code": exit_code}))
    return path


def describe_find_runs():
    def it_takes_a_run_directory_as_itself(tmp_path):
        assert find_runs([run(tmp_path / "r1")]) == [tmp_path / "r1"]

    def it_takes_a_directory_of_runs_as_its_runs_in_name_order(tmp_path):
        run(tmp_path / "runs" / "r2")
        run(tmp_path / "runs" / "r1")
        (tmp_path / "runs" / "matrix.jsonl").write_text("")
        (tmp_path / "runs" / "empty").mkdir()
        assert find_runs([tmp_path / "runs"]) == [tmp_path / "runs" / "r1", tmp_path / "runs" / "r2"]

    def it_skips_runs_whose_agent_did_not_exit_0(tmp_path):
        run(tmp_path / "runs" / "ok")
        run(tmp_path / "runs" / "killed", exit_code=137)
        (tmp_path / "runs" / "raised").mkdir()
        (tmp_path / "runs" / "raised" / "manifest.json").write_text(json.dumps({"error": "boom"}))
        assert find_runs([tmp_path / "runs"]) == [tmp_path / "runs" / "ok"]

    def it_takes_each_run_once(tmp_path):
        r1 = run(tmp_path / "runs" / "r1")
        assert find_runs([tmp_path / "runs", r1]) == [r1]
