import click
from dotenv import dotenv_values

from botbox import Agent, ClaudeAgent, CodexAgent

from gbnf_experiment import config


def make_agent(*, model: str, effort: str, auth: str) -> Agent:
    if model.startswith("claude-"):
        return ClaudeAgent(model=model, effort=effort, api_key=api_key("ANTHROPIC_API_KEY", auth))
    if model.startswith("gpt-"):
        return CodexAgent(model=model, effort=effort, api_key=api_key("OPENAI_API_KEY", auth))
    raise click.ClickException(f"No agent for model {model!r}: expected claude-* or gpt-*")


def api_key(name: str, auth: str) -> str | None:
    if auth != "api":
        return None
    env_path = config.REPO_ROOT / ".env"
    if not env_path.is_file():
        raise click.ClickException(f"Missing {env_path}; {name} is required for --auth api")
    key = dotenv_values(env_path, interpolate=False).get(name)
    if not key or not key.strip():
        raise click.ClickException(f"Missing or blank {name} in {env_path}")
    return key
