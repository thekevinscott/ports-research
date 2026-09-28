import click

from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent

from .run_gbnf_experiment import run_gbnf_experiment

DEFAULT_MODEL = "claude-opus-5"

@click.command()
@click.option(
    "--source-language",
    type=click.Choice(["javascript", "python"]),
    required=True,
)
@click.option("--include-unit-tests", is_flag=True, default=False)
@click.option("--include-source-integration-tests", is_flag=True, default=False)
@click.option("--include-target-integration-tests", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
@click.option("--agent", "agent_name", type=click.Choice(['pi', 'claude']), default="claude")
# Both free text: effort levels are per-agent, and claude errors on an unknown model instead of warning and running the default.
@click.option("--effort", default="high", show_default=True)
@click.option("--model", default=DEFAULT_MODEL, show_default=True)
def cli(
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    debug: bool,
    agent_name: str,
    effort: str,
    model: str,
) -> None:
    if agent_name != "claude":
        raise click.ClickException(
            f"--agent {agent_name} is not wired up: PiAgent requires a provider the CLI cannot supply"
        )
    agent = ClaudeAgent()
    try:
        run_directory = run_gbnf_experiment(
            agent=agent,
            source_language=source_language,
            include_unit_tests=include_unit_tests,
            include_source_integration_tests=include_source_integration_tests,
            include_target_integration_tests=include_target_integration_tests,
            debug=debug,
            effort=effort,
            model=model,
        )
        click.echo(f"Run directory: {run_directory}")
    except Exception as e:
        raise click.ClickException(str(e))
