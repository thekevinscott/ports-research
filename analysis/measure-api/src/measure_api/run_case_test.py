import json
import signal
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from measure_api.run_case import PREFIX_CAP, TIMEOUT_SECONDS, run_case

IMPLEMENTATION = Path("/impl")
STEPS = [{"step": "construct", "rules": []}]


@pytest.fixture
def popen():
    with patch("measure_api.run_case.subprocess.Popen", autospec=True) as m:
        yield m


@pytest.fixture
def killpg():
    with patch("measure_api.run_case.os.killpg", autospec=True) as m:
        yield m


def answer(popen, returncode=0, stdout="", stderr=""):
    process = popen.return_value
    process.pid = 42
    process.returncode = returncode
    process.communicate.return_value = (stdout, stderr)
    return process


def answered(popen):
    return answer(popen, stdout=json.dumps(STEPS))


def describe_run_case():
    def it_returns_the_drivers_steps(popen):
        answered(popen)
        assert run_case("python", IMPLEMENTATION, "g", "i") == {"steps": STEPS, "crash": None}

    def it_sends_the_case_and_its_code_points_up_to_the_cap(popen):
        process = answered(popen)
        text = "é😀" + "a" * PREFIX_CAP
        run_case("python", IMPLEMENTATION, 'root ::= "a"', text)
        sent = json.loads(process.communicate.call_args.args[0])
        assert sent == {"grammar": 'root ::= "a"', "input": text, "chunks": ["é", "😀", *["a"] * (PREFIX_CAP - 2)]}

    def it_waits_the_per_case_timeout(popen):
        process = answered(popen)
        run_case("python", IMPLEMENTATION, "g", "i")
        assert process.communicate.call_args.kwargs["timeout"] == TIMEOUT_SECONDS

    def it_puts_the_implementation_on_the_python_path(popen):
        answered(popen)
        run_case("python", IMPLEMENTATION, "g", "i")
        assert popen.call_args.kwargs["env"]["PYTHONPATH"] == str(IMPLEMENTATION)

    def it_hands_the_typescript_entry_to_the_driver(popen):
        answered(popen)
        run_case("typescript", IMPLEMENTATION, "g", "i")
        assert popen.call_args.args[0][-1] == str(IMPLEMENTATION / "src" / "index.ts")

    def it_runs_the_driver_in_its_own_session(popen):
        answered(popen)
        run_case("typescript", IMPLEMENTATION, "g", "i")
        assert popen.call_args.kwargs["start_new_session"] is True

    def it_kills_the_whole_session_and_calls_a_timeout_a_crash(popen, killpg):
        process = answer(popen)
        process.communicate.side_effect = [subprocess.TimeoutExpired(cmd=[], timeout=TIMEOUT_SECONDS), ("", "")]
        assert run_case("python", IMPLEMENTATION, "g", "i") == {"steps": None, "crash": f"timed out after {TIMEOUT_SECONDS}s"}
        killpg.assert_called_once_with(42, signal.SIGKILL)

    def it_calls_a_non_zero_exit_a_crash_with_the_stderr(popen):
        answer(popen, returncode=1, stderr="Traceback\nModuleNotFoundError: gbnf\n")
        assert run_case("python", IMPLEMENTATION, "g", "i") == {"steps": None, "crash": "Traceback\nModuleNotFoundError: gbnf"}

    def it_calls_an_exit_without_an_answer_a_crash(popen):
        answer(popen)
        assert run_case("python", IMPLEMENTATION, "g", "i") == {"steps": None, "crash": "exit 0 with no answer"}
