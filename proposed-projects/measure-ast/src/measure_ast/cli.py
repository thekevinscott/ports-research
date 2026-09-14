import json
import sys
from pathlib import Path

import click

from .measure_ast import measure_ast


@click.command()
@click.option("--language", type=click.Choice(["python", "typescript"]), required=True)
@click.option(
    "--target",
    type=click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True),
    required=True,
)
@click.option("--exclude", multiple=True, help="fnmatch pattern against each relative path and its parts")
def cli(language: str, target: Path, exclude: tuple[str, ...]) -> None:
    try:
        report = measure_ast(language=language, target=target, exclude=list(exclude))
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))
    sys.exit(0)
