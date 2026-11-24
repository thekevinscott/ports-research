import json

from botbox import Agent, ClaudeAgent, CodexAgent


def reported_error(agent: Agent, stdout: str) -> str | None:
    if isinstance(agent, ClaudeAgent):
        report = json.loads(stdout) if stdout else {}
        return report.get("result", "the agent reported an error") if report.get("is_error") else None
    if isinstance(agent, CodexAgent):
        for line in stdout.splitlines():
            event = json.loads(line)
            if event.get("type") == "turn.failed":
                return event["error"]["message"]
        return None
    raise TypeError(f"No report format for {type(agent).__name__}")
