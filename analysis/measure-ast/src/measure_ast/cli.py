import json
import sys
from pathlib import Path

import click

from measure_ast.compare import compare
from measure_ast.measure_ast import measure_ast

LANGUAGE = click.Choice(["python", "typescript"])
DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)
EXCLUDE_HELP = "fnmatch pattern against each relative path and its parts"


@click.command(hidden=True)
@click.option("--language", type=LANGUAGE, required=True)
@click.option("--target", type=DIRECTORY, required=True)
@click.option("--exclude", multiple=True, help=EXCLUDE_HELP)
def cli(language: str, target: Path, exclude: tuple[str, ...]) -> None:
    """Measure one tree."""
    try:
        report = measure_ast(language=language, target=target, exclude=list(exclude))
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))
    sys.exit(0)


@click.command("compare")
@click.option("--language", type=LANGUAGE, required=True)
@click.option("--port", type=DIRECTORY, required=True)
@click.option("--reference", type=DIRECTORY, required=True)
@click.option("--exclude", multiple=True, help=EXCLUDE_HELP)
def compare_cli(language: str, port: Path, reference: Path, exclude: tuple[str, ...]) -> None:
    """Measure a port relative to a reference tree."""
    try:
        report = compare(language=language, port=port, reference=reference, exclude=list(exclude))
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))


class MeasureByDefault(click.Group):
    """`measure-ast --language ... --target ...` keeps meaning the one-tree measure."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        if args and args[0] not in self.commands and args[0] != "--help":
            args = ["measure", *args]
        return super().parse_args(ctx, args)


main = MeasureByDefault(commands={"measure": cli, "compare": compare_cli})
