from pathlib import Path

import click

from judge.report import report
from judge.run_judge import run_judge

DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)
OUT = click.Path(path_type=Path, resolve_path=True)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--rubric", type=click.Choice(["code", "transcript"]), required=True)
@click.option("--runs", type=DIRECTORY, multiple=True, required=True, help="A run directory, or a directory of runs.")
@click.option("--out", type=OUT, required=True)
@click.option("--limit", type=int, default=None, help="Judge only the first N items in shuffled order.")
@click.option("--model", default="claude-opus-5-5", show_default=True)
@click.option("--effort", default="max", show_default=True)
@click.option("-k", "concurrency", type=int, default=2, show_default=True, help="Concurrent claude calls.")
def run(rubric: str, runs: tuple[Path, ...], out: Path, limit: int | None, model: str, effort: str, concurrency: int) -> None:
    try:
        run_judge(rubric=rubric, runs=list(runs), out=out, limit=limit, model=model, effort=effort, concurrency=concurrency)
    except RuntimeError as e:
        raise click.ClickException(str(e))


@cli.command("report")
@click.option("--out", type=DIRECTORY, required=True)
def report_command(out: Path) -> None:
    click.echo(report(out), nl=False)
