import json
import resource
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from exercise_api.run_driver import run_driver

TARGET = Path("/data/run/ported_implementation")
CASES = [{"grammar": 'root ::= "a"', "input": "a"}, {"grammar": 'root ::= "b"', "input": "x"}]
OK = {"ok": True, "error_type": None, "error_pos": None, "rules": [{"type": "end"}], "elapsed_ns": 10}
FAILED = {"ok": False, "error_type": "InputParseError", "error_pos": 0, "rules": None, "elapsed_ns": 20}
DRIVER_FAILED = {"ok": False, "error_type": "driver_failed", "error_pos": None, "rules": None, "elapsed_ns": None}
LIMIT = 4 * 1024**3


@pytest.fixture
def driver_command_function():
    with patch("exercise_api.run_driver.driver_command", autospec=True) as m:
        m.return_value = ["driver", "--target", str(TARGET)]
        yield m


@pytest.fixture
def subprocess_run():
    with patch("exercise_api.run_driver.subprocess.run", autospec=True) as m:
        m.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(OK) + "\n" + json.dumps(FAILED) + "\n", stderr=""
        )
        yield m


@pytest.fixture
def setrlimit():
    with patch("exercise_api.run_driver.resource.setrlimit", autospec=True) as m:
        yield m


def run(**overrides):
    kwargs = {"language": "python", "target": TARGET, "cases": CASES, "adapt": False, "timeout": 60, "memory_limit_bytes": LIMIT}
    return run_driver(**{**kwargs, **overrides})


def describe_run_driver():
    def it_returns_one_result_per_case_in_order(driver_command_function, subprocess_run):
        assert run() == [OK, FAILED]

    def it_feeds_the_cases_as_json_lines_on_stdin(driver_command_function, subprocess_run):
        run()
        stdin = subprocess_run.call_args.kwargs["input"]
        assert [json.loads(line) for line in stdin.splitlines()] == CASES

    def it_runs_the_command_the_language_and_target_resolve_to(driver_command_function, subprocess_run):
        run(language="typescript", adapt=True)
        assert driver_command_function.call_args.kwargs == {"language": "typescript", "target": TARGET, "adapt": True, "repeat": 1, "warmup": 0}
        assert subprocess_run.call_args.args[0] == ["driver", "--target", str(TARGET)]

    def it_passes_repeat_and_warmup_to_the_driver_command(driver_command_function, subprocess_run):
        run(repeat=30, warmup=3)
        assert driver_command_function.call_args.kwargs["repeat"] == 30
        assert driver_command_function.call_args.kwargs["warmup"] == 3

    def it_passes_the_timeout_through(driver_command_function, subprocess_run):
        run(timeout=7)
        assert subprocess_run.call_args.kwargs["timeout"] == 7

    def it_caps_the_driver_address_space_before_exec(driver_command_function, subprocess_run, setrlimit):
        run(memory_limit_bytes=123)
        subprocess_run.call_args.kwargs["preexec_fn"]()
        setrlimit.assert_called_once_with(resource.RLIMIT_AS, (123, 123))

    def it_marks_cases_the_driver_never_answered_as_driver_exit(driver_command_function, subprocess_run):
        subprocess_run.return_value.stdout = json.dumps(OK) + "\n"
        results = run()
        assert results[0] == OK
        assert results[1] == {"ok": False, "error_type": "driver_exit", "error_pos": None, "rules": None, "elapsed_ns": None}

    def it_records_every_case_as_driver_failed_when_the_driver_exits_non_zero(driver_command_function, subprocess_run):
        subprocess_run.return_value.returncode = 3
        assert run() == [DRIVER_FAILED, DRIVER_FAILED]

    def it_records_every_case_as_driver_failed_when_the_driver_is_killed(driver_command_function, subprocess_run):
        subprocess_run.return_value.returncode = -9
        subprocess_run.return_value.stdout = json.dumps(OK) + "\n"
        assert run() == [DRIVER_FAILED, DRIVER_FAILED]

    def it_records_every_case_as_driver_failed_after_a_timeout(driver_command_function, subprocess_run):
        subprocess_run.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=60, output=(json.dumps(OK) + "\n").encode())
        assert run() == [DRIVER_FAILED, DRIVER_FAILED]

    def it_ignores_trailing_output_beyond_the_case_count(driver_command_function, subprocess_run):
        subprocess_run.return_value.stdout = "\n".join(json.dumps(OK) for _ in range(3)) + "\n"
        assert len(run()) == 2
