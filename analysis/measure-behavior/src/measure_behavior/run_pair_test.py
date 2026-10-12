import json
import signal
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from measure_behavior.run_pair import TIMEOUT_SECONDS, run_pair

IMPLEMENTATION = Path("/impl")


@pytest.fixture
def popen():
    with patch("measure_behavior.run_pair.subprocess.Popen", autospec=True) as m:
        yield m


@pytest.fixture
def killpg():
    with patch("measure_behavior.run_pair.os.killpg", autospec=True) as m:
        yield m


def answer(popen, returncode=0, stdout="", stderr=""):
    process = popen.return_value
    process.pid = 42
    process.returncode = returncode
    process.communicate.return_value = (stdout, stderr)
    return process


def accepted(popen):
    return answer(popen, stdout=json.dumps({"outcome": "accept", "error": None}))


def describe_run_pair():
    def it_returns_the_drivers_outcome(popen):
        answer(popen, stdout=json.dumps({"outcome": "reject", "error": "InputParseError: x"}))
        assert run_pair("python", IMPLEMENTATION, "g", "i") == {"outcome": "reject", "error": "InputParseError: x"}

    def it_sends_the_pair_on_stdin_with_the_per_pair_timeout(popen):
        process = accepted(popen)
        run_pair("python", IMPLEMENTATION, 'root ::= "a"', "a")
        assert json.loads(process.communicate.call_args.args[0]) == {"grammar": 'root ::= "a"', "input": "a"}
        assert process.communicate.call_args.kwargs["timeout"] == TIMEOUT_SECONDS

    def it_puts_the_implementation_on_the_python_path(popen):
        accepted(popen)
        run_pair("python", IMPLEMENTATION, "g", "i")
        assert popen.call_args.kwargs["env"]["PYTHONPATH"] == str(IMPLEMENTATION)

    def it_hands_the_typescript_entry_to_the_driver(popen):
        accepted(popen)
        run_pair("typescript", IMPLEMENTATION, "g", "i")
        assert popen.call_args.args[0][-1] == str(IMPLEMENTATION / "src" / "index.ts")

    def it_runs_the_driver_in_its_own_session(popen):
        accepted(popen)
        run_pair("typescript", IMPLEMENTATION, "g", "i")
        assert popen.call_args.kwargs["start_new_session"] is True

    def it_kills_the_whole_session_and_calls_a_timeout_a_crash(popen, killpg):
        process = answer(popen)
        process.communicate.side_effect = [subprocess.TimeoutExpired(cmd=[], timeout=TIMEOUT_SECONDS), ("", "")]
        assert run_pair("python", IMPLEMENTATION, "g", "i") == {
            "outcome": "crash",
            "error": f"timed out after {TIMEOUT_SECONDS}s",
        }
        killpg.assert_called_once_with(42, signal.SIGKILL)

    def it_calls_a_non_zero_exit_a_crash_with_the_stderr(popen):
        answer(popen, returncode=1, stderr="Traceback\nModuleNotFoundError: gbnf\n")
        assert run_pair("python", IMPLEMENTATION, "g", "i") == {
            "outcome": "crash",
            "error": "Traceback\nModuleNotFoundError: gbnf",
        }

    def it_calls_an_exit_without_an_outcome_a_crash(popen):
        answer(popen)
        assert run_pair("python", IMPLEMENTATION, "g", "i")["outcome"] == "crash"
