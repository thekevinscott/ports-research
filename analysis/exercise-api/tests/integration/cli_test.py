import json
import os
import signal
import subprocess
import sys
import time

from click.testing import CliRunner
from exercise_api.cli import cli

from conftest import CASES, LADDER_RUNGS, OFF_BY_ONE_DISAGREEMENTS

REPORT_KEYS = {
    "cases",
    "agree_with_reference",
    "disagree_with_reference",
    "disagreements",
    "reference_error_cases",
    "target_error_cases",
    "reference_mean_elapsed_ns",
    "reference_p50_elapsed_ns",
    "reference_p95_elapsed_ns",
    "target_mean_elapsed_ns",
    "target_p50_elapsed_ns",
    "target_p95_elapsed_ns",
}


def invoke(language, reference, *targets, cases, extra=()):
    args = ["--language", language, "--reference", str(reference), "--cases", str(cases), *extra]
    for target in targets:
        args += ["--target", str(target)]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def describe_python():
    def it_agrees_with_itself_on_every_case(python_reference, cases_file):
        report = invoke("python", python_reference, python_reference, cases=cases_file)
        target = report["targets"][str(python_reference)]
        assert target["agree_with_reference"] == len(CASES)
        assert target["disagree_with_reference"] == 0

    def it_treats_class_instances_and_plain_dicts_with_the_same_content_as_equal(python_reference, python_plain_dicts, cases_file):
        report = invoke("python", python_reference, python_plain_dicts, cases=cases_file)
        assert report["targets"][str(python_plain_dicts)]["disagree_with_reference"] == 0

    def it_reports_a_shifted_error_position_as_a_disagreement_with_both_outputs(python_reference, python_off_by_one, cases_file):
        report = invoke("python", python_reference, python_off_by_one, cases=cases_file)
        target = report["targets"][str(python_off_by_one)]
        assert target["disagree_with_reference"] == OFF_BY_ONE_DISAGREEMENTS
        [disagreement] = target["disagreements"]
        assert disagreement["case"] == {"grammar": 'root ::= "a"', "input": "axb"}
        assert disagreement["reference"]["error_pos"] == 1
        assert disagreement["target"]["error_pos"] == 2
        assert disagreement["target"]["error_type"] == "InputParseError"

    def it_counts_error_cases_on_both_sides(python_reference, python_off_by_one, cases_file):
        report = invoke("python", python_reference, python_off_by_one, cases=cases_file)
        target = report["targets"][str(python_off_by_one)]
        assert target["reference_error_cases"] == 2
        assert target["target_error_cases"] == 2

    def it_reports_timing_for_reference_and_target(python_reference, python_plain_dicts, cases_file):
        report = invoke("python", python_reference, python_plain_dicts, cases=cases_file)
        target = report["targets"][str(python_plain_dicts)]
        for side in ("reference", "target"):
            assert target[f"{side}_mean_elapsed_ns"] > 0
            assert target[f"{side}_p50_elapsed_ns"] <= target[f"{side}_p95_elapsed_ns"]

    def it_records_every_case_as_driver_failed_when_the_driver_exits_non_zero(python_reference, python_exiting, cases_file):
        report = invoke("python", python_reference, python_exiting, cases=cases_file)
        target = report["targets"][str(python_exiting)]
        assert target["agree_with_reference"] == 0
        assert target["target_error_cases"] == len(CASES)
        assert [d["target"]["error_type"] for d in target["disagreements"]] == ["driver_failed"] * len(CASES)

    def it_caps_a_target_that_allocates_without_bound(python_reference, python_allocating, cases_file):
        report = invoke("python", python_reference, python_allocating, cases=cases_file, extra=["--memory-limit-bytes", str(1 << 30)])
        target = report["targets"][str(python_allocating)]
        assert target["agree_with_reference"] == len(CASES) - 1
        [disagreement] = target["disagreements"]
        assert disagreement["case"]["input"] == "abab"
        assert disagreement["target"]["error_type"] == "MemoryError"

    def it_cannot_load_a_flat_module_port_without_adapt(python_reference, python_flat, cases_file):
        report = invoke("python", python_reference, python_flat, cases=cases_file)
        target = report["targets"][str(python_flat)]
        assert target["target_error_cases"] == len(CASES)
        assert {d["target"]["error_type"] for d in target["disagreements"]} == {"LoadError"}

    def it_loads_a_flat_module_port_with_adapt(python_reference, python_flat, cases_file):
        report = invoke("python", python_reference, python_flat, cases=cases_file, extra=["--adapt"])
        assert report["targets"][str(python_flat)]["disagree_with_reference"] == 0

    def it_counts_agreement_among_several_targets(python_reference, python_plain_dicts, python_off_by_one, python_flat, cases_file):
        report = invoke("python", python_reference, python_plain_dicts, python_off_by_one, python_flat, cases=cases_file, extra=["--adapt"])
        assert report["agree_all_targets"] == len(CASES) - OFF_BY_ONE_DISAGREEMENTS
        assert report["agree_all_targets_not_reference"] == 0

    def it_counts_unanimous_targets_that_differ_from_the_reference(python_reference, python_plain_dicts, python_off_by_one, cases_file):
        report = invoke("python", python_off_by_one, python_reference, python_plain_dicts, cases=cases_file)
        assert report["agree_all_targets"] == len(CASES)
        assert report["agree_all_targets_not_reference"] == OFF_BY_ONE_DISAGREEMENTS

    def it_omits_cross_target_counts_for_a_single_target(python_reference, python_plain_dicts, cases_file):
        report = invoke("python", python_reference, python_plain_dicts, cases=cases_file)
        assert "agree_all_targets" not in report


def describe_repeat():
    def it_reports_per_phase_timings_per_rung_with_repeat(python_reference, ladder_cases_file):
        report = invoke("python", python_reference, python_reference, cases=ladder_cases_file, extra=["--repeat", "5", "--warmup", "2"])
        target = report["targets"][str(python_reference)]
        assert [entry["rung"] for entry in target["timings"]] == LADDER_RUNGS
        assert [entry["rung"] for entry in target["reference_timings"]] == LADDER_RUNGS
        for entry in target["timings"]:
            for phase in ("construct_ns", "add_ns"):
                assert entry[phase]["min"] <= entry[phase]["median"] <= entry[phase]["p90"]
                assert entry[phase]["spread"] >= 0

    def it_measures_the_input_length_of_every_rung(python_reference, ladder_cases_file):
        report = invoke("python", python_reference, python_reference, cases=ladder_cases_file, extra=["--repeat", "3"])
        target = report["targets"][str(python_reference)]
        assert [entry["input_len"] for entry in target["timings"]] == [1, 2, 4]

    def it_excludes_a_raising_rung_from_timings_and_counts_it(python_reference, python_off_by_one, ladder_cases_file):
        report = invoke("python", python_reference, python_off_by_one, cases=ladder_cases_file, extra=["--repeat", "3"])
        target = report["targets"][str(python_off_by_one)]
        assert [entry["rung"] for entry in target["timings"]] == LADDER_RUNGS
        assert target["target_error_cases"] == 1

    def it_takes_a_repeat_budget_from_the_case_when_the_flag_is_absent(python_reference, ladder_budget_cases_file):
        report = invoke("python", python_reference, python_reference, cases=ladder_budget_cases_file)
        target = report["targets"][str(python_reference)]
        assert [entry["rung"] for entry in target["timings"]] == LADDER_RUNGS
        [once, *repeated] = target["timings"]
        for phase in ("construct_ns", "add_ns"):
            assert once[phase]["min"] == once[phase]["median"] == once[phase]["p90"]
            assert all(entry[phase]["min"] <= entry[phase]["p90"] for entry in repeated)

    def it_leaves_existing_reports_unchanged_without_repeat(python_reference, python_plain_dicts, cases_file):
        report = invoke("python", python_reference, python_plain_dicts, cases=cases_file)
        assert set(report["targets"][str(python_plain_dicts)]) == REPORT_KEYS

    def it_still_caps_a_target_that_allocates_without_bound_under_repeat(python_reference, python_allocating, cases_file):
        report = invoke("python", python_reference, python_allocating, cases=cases_file, extra=["--repeat", "5", "--memory-limit-bytes", str(1 << 30)])
        target = report["targets"][str(python_allocating)]
        [disagreement] = target["disagreements"]
        assert disagreement["case"]["input"] == "abab"
        assert disagreement["target"]["error_type"] == "MemoryError"

    def it_still_records_a_driver_that_exits_as_driver_failed_under_repeat(python_reference, python_exiting, cases_file):
        report = invoke("python", python_reference, python_exiting, cases=cases_file, extra=["--repeat", "5"])
        target = report["targets"][str(python_exiting)]
        assert target["target_error_cases"] == len(CASES)
        assert [d["target"]["error_type"] for d in target["disagreements"]] == ["driver_failed"] * len(CASES)


def describe_out():
    def it_writes_the_report_to_out_and_leaves_no_partial(python_reference, python_plain_dicts, cases_file, tmp_path):
        out = tmp_path / "report.json"
        report = invoke("python", python_reference, python_plain_dicts, cases=cases_file, extra=["--out", str(out)])
        assert json.loads(out.read_text()) == report
        assert not (tmp_path / "report.partial.json").exists()

    def it_keeps_finished_targets_in_the_partial_report_when_killed(python_reference, python_plain_dicts, python_sleeping, cases_file, tmp_path):
        out, partial = tmp_path / "report.json", tmp_path / "report.partial.json"
        args = ["--language", "python", "--reference", str(python_reference), "--target", str(python_plain_dicts), "--target", str(python_sleeping), "--cases", str(cases_file), "--out", str(out)]
        process = subprocess.Popen([sys.executable, "-c", "from exercise_api.cli import cli; cli()", *args], start_new_session=True)
        deadline = time.monotonic() + 30
        while not partial.exists() and time.monotonic() < deadline:
            time.sleep(0.1)
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        report = json.loads(partial.read_text())
        assert list(report["targets"]) == [str(python_plain_dicts)]
        assert report["targets"][str(python_plain_dicts)]["disagree_with_reference"] == 0
        assert not out.exists()


def describe_typescript():
    def it_agrees_with_itself_on_every_case(typescript_reference, cases_file):
        report = invoke("typescript", typescript_reference, typescript_reference, cases=cases_file)
        assert report["targets"][str(typescript_reference)]["agree_with_reference"] == len(CASES)

    def it_treats_class_instances_and_plain_objects_with_the_same_content_as_equal(typescript_reference, typescript_plain_objects, cases_file):
        report = invoke("typescript", typescript_reference, typescript_plain_objects, cases=cases_file)
        assert report["targets"][str(typescript_plain_objects)]["disagree_with_reference"] == 0

    def it_reports_a_shifted_error_position_as_a_disagreement(typescript_reference, typescript_off_by_one, cases_file):
        report = invoke("typescript", typescript_reference, typescript_off_by_one, cases=cases_file)
        target = report["targets"][str(typescript_off_by_one)]
        assert target["disagree_with_reference"] == OFF_BY_ONE_DISAGREEMENTS
        [disagreement] = target["disagreements"]
        assert disagreement["reference"] == {"ok": False, "error_type": "InputParseError", "error_pos": 1, "rules": None}
        assert disagreement["target"]["error_pos"] == 2

    def it_caps_a_target_that_allocates_without_bound(typescript_reference, typescript_allocating, cases_file):
        report = invoke("typescript", typescript_reference, typescript_allocating, cases=cases_file)
        target = report["targets"][str(typescript_allocating)]
        [allocating] = [d["target"] for d in target["disagreements"] if d["case"]["input"] == "abab"]
        assert allocating["ok"] is False
        assert allocating["error_type"] in {"RangeError", "driver_failed"}

    def it_cannot_load_a_named_only_export_without_adapt(typescript_reference, typescript_named_only, cases_file):
        report = invoke("typescript", typescript_reference, typescript_named_only, cases=cases_file)
        target = report["targets"][str(typescript_named_only)]
        assert {d["target"]["error_type"] for d in target["disagreements"]} == {"LoadError"}

    def it_loads_a_named_only_export_with_adapt(typescript_reference, typescript_named_only, cases_file):
        report = invoke("typescript", typescript_reference, typescript_named_only, cases=cases_file, extra=["--adapt"])
        assert report["targets"][str(typescript_named_only)]["disagree_with_reference"] == 0


def describe_generate():
    def it_writes_exactly_count_cases_and_is_deterministic(tmp_path):
        first, second = tmp_path / "first.jsonl", tmp_path / "second.jsonl"
        for path in (first, second):
            result = CliRunner().invoke(cli, ["generate", "--seed", "1", "--count", "40", "--out", str(path)])
            assert result.exit_code == 0, result.output
        assert first.read_text() == second.read_text()
        assert len(first.read_text().splitlines()) == 40

    def it_produces_different_cases_for_a_different_seed(tmp_path):
        paths = []
        for seed in ("1", "2"):
            path = tmp_path / f"{seed}.jsonl"
            CliRunner().invoke(cli, ["generate", "--seed", seed, "--count", "40", "--out", str(path)])
            paths.append(path)
        assert paths[0].read_text() != paths[1].read_text()

    def it_emits_cases_the_run_command_accepts(python_reference, tmp_path):
        path = tmp_path / "generated.jsonl"
        CliRunner().invoke(cli, ["generate", "--seed", "0", "--count", "20", "--out", str(path)])
        report = invoke("python", python_reference, python_reference, cases=path)
        assert report["cases"] == 20


def describe_fixtures():
    def it_pairs_each_fixture_grammar_with_its_inputs(grammars_dir, tmp_path):
        out = tmp_path / "fixtures.jsonl"
        result = CliRunner().invoke(cli, ["fixtures", "--grammars", str(grammars_dir), "--out", str(out)])
        assert result.exit_code == 0, result.output
        assert [json.loads(line) for line in out.read_text().splitlines()] == [
            {"grammar": 'root ::= "a"\n', "input": "a"},
            {"grammar": 'root ::= "a"\n', "input": "ab"},
        ]
