import os
import shutil
from pathlib import Path

from ..config import SANDBOX_DIR
from ..errors import AgentHarnessSandboxError

EFFORT_LEVELS = ("off", "minimal", "low", "medium", "high", "xhigh")

PROVIDER_HOSTS = {"openrouter": ("openrouter.ai",)}

PROVIDER_HOST_VARIABLES = {"tower": "PI_AGENT_HOST"}

PROVIDERS = (*PROVIDER_HOSTS, *PROVIDER_HOST_VARIABLES)

AUTH_FILENAMES = ("auth.json", "models.json")

PI_HOME = Path.home() / ".pi" / "agent"


def resolve_allow(provider: str) -> tuple[str, ...]:
    if provider in PROVIDER_HOSTS:
        return PROVIDER_HOSTS[provider]
    variable = PROVIDER_HOST_VARIABLES[provider]
    host = os.environ.get(variable)
    if not host:
        raise AgentHarnessSandboxError(
            f"provider {provider!r} needs {variable} set to the host it serves from"
        )
    return (host,)


class PiAgent:
    image = "agent-harness-sandbox-pi:latest"
    dockerfile = SANDBOX_DIR / "Dockerfile.pi"
    home = "/home/node/.pi/agent"
    transcripts = "/home/node/.pi/agent/sessions"

    def __init__(self, provider: str, *, host_home: Path = PI_HOME):
        if provider not in PROVIDERS:
            raise AgentHarnessSandboxError(
                f"unknown provider {provider!r}: expected {', '.join(PROVIDERS)}"
            )
        self.provider = provider
        self.allow = resolve_allow(provider)
        self.host_home = host_home

    def command(self, prompt: str, *, effort: str, model: str) -> list[str]:
        if effort not in EFFORT_LEVELS:
            raise AgentHarnessSandboxError(
                f"unknown effort {effort!r}: expected {', '.join(EFFORT_LEVELS)}"
            )
        return [
            "pi",
            "-p",
            "--mode",
            "json",
            "--provider",
            self.provider,
            "--thinking",
            effort,
            "--model",
            model,
            prompt,
        ]

    def stage_auth(self, destination: Path) -> None:
        for name in AUTH_FILENAMES:
            source = self.host_home / name
            if not source.exists():
                raise AgentHarnessSandboxError(f"{source} does not exist")
            shutil.copy(source, destination)
