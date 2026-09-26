import json

from exercise_api.write_report import write_report

REPORT = {"cases": 1, "targets": {"/ports/a": {"agree_with_reference": 1}}}


def describe_write_report():
    def it_writes_the_report_as_json(tmp_path):
        path = tmp_path / "report.json"
        write_report(path, REPORT)
        assert json.loads(path.read_text()) == REPORT

    def it_replaces_an_existing_file(tmp_path):
        path = tmp_path / "report.json"
        path.write_text("stale")
        write_report(path, REPORT)
        assert json.loads(path.read_text()) == REPORT

    def it_leaves_only_the_report_behind(tmp_path):
        path = tmp_path / "report.json"
        write_report(path, REPORT)
        assert [p.name for p in tmp_path.iterdir()] == ["report.json"]
