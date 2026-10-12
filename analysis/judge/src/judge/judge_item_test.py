import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from judge.judge_item import judge_item

SCHEMA = {"type": "object"}
STDOUT = json.dumps({"is_error": False, "result": '{"a": 1}', "structured_output": {"a": 1}, "usage": {"output_tokens": 3}})


@pytest.fixture
def run_function():
    with patch("judge.judge_item.subprocess.run", autospec=True) as m:
        m.return_value = subprocess.CompletedProcess([], 0, stdout=STDOUT, stderr="")
        yield m


def describe_judge_item():
    def it_calls_the_claude_cli_without_tools_on_the_prompt_with_the_schema(run_function):
        judge_item("the prompt", schema=SCHEMA, model="m", effort="e")
        args, kwargs = run_function.call_args
        command = args[0]
        assert command[:2] == ["claude", "-p"]
        assert command[command.index("--output-format") + 1] == "json"
        assert command[command.index("--tools") + 1] == ""
        assert json.loads(command[command.index("--json-schema") + 1]) == SCHEMA
        assert command[command.index("--model") + 1] == "m"
        assert command[command.index("--effort") + 1] == "e"
        assert {"--safe-mode", "--no-session-persistence"} <= set(command)
        assert kwargs["input"] == "the prompt"

    def it_runs_without_an_api_key_so_the_subscription_pays(run_function, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        judge_item("p", schema=SCHEMA, model="m", effort="e")
        env = run_function.call_args.kwargs["env"]
        assert "ANTHROPIC_API_KEY" not in env
        assert "PATH" in env

    def it_runs_in_an_empty_directory_outside_the_repository(run_function):
        judge_item("p", schema=SCHEMA, model="m", effort="e")
        cwd = Path(run_function.call_args.kwargs["cwd"])
        assert Path(__file__).resolve().parents[3] not in cwd.resolve().parents

    def it_returns_the_parsed_output_and_the_wall_seconds(run_function):
        judged = judge_item("p", schema=SCHEMA, model="m", effort="e")
        assert judged["verdicts"] == {"a": 1}
        assert judged["usage"] == {"output_tokens": 3}
        assert judged["wall_seconds"] >= 0

    def it_raises_with_stderr_when_the_cli_fails(run_function):
        run_function.return_value = subprocess.CompletedProcess([], 1, stdout="", stderr="not logged in")
        with pytest.raises(RuntimeError, match="not logged in"):
            judge_item("p", schema=SCHEMA, model="m", effort="e")
