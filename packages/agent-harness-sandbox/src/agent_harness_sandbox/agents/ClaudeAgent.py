import shutil
from pathlib import Path

from ..config import SANDBOX_DIR
from ..errors import AgentHarnessSandboxError

EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")

DENIED_TOOLS = ("WebSearch", "WebFetch")

CREDENTIALS_FILENAME = ".credentials.json"

CLAUDE_HOME = Path.home() / ".claude"


class ClaudeAgent:
    image = "agent-harness-sandbox-claude:latest"
    dockerfile = SANDBOX_DIR / "Dockerfile.claude"
    home = "/home/node/.claude"
    transcripts = "/home/node/.claude/projects"
    allow = ("api.anthropic.com",)

    def command(self, prompt: str, *, effort: str, model: str) -> list[str]:
        if effort not in EFFORT_LEVELS:
            raise AgentHarnessSandboxError(
                f"unknown effort {effort!r}: expected {', '.join(EFFORT_LEVELS)}"
            )
        return [
            "claude",
            "-p",
            "--dangerously-skip-permissions",
            # Variadic, so one token or it eats the prompt.
            f"--disallowed-tools={','.join(DENIED_TOOLS)}",
            "--effort",
            effort,
            "--output-format",
            "json",
            "--model",
            model,
            prompt,
        ]

    def stage_auth(self, destination: Path) -> None:
        source = CLAUDE_HOME / CREDENTIALS_FILENAME
        if not source.exists():
            raise AgentHarnessSandboxError(f"{source} does not exist")
        shutil.copy(source, destination)
