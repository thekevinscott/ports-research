import json
from pathlib import Path

import click

from .measure_code_distance import measure_code_distance
from .measure_git_diff import measure_git_diff

DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)
LANGUAGE = click.option("--language", type=click.Choice(["python", "typescript"]), required=True)
A = click.option("--a", type=DIRECTORY, required=True)
B = click.option("--b", type=DIRECTORY, required=True)
EXCLUDE = click.option("--exclude", multiple=True, help="fnmatch pattern against each relative path and its parts")


def report(measure, language: str, a: Path, b: Path, exclude: tuple[str, ...]) -> None:
    try:
        result = measure(language=language, a=a, b=b, exclude=list(exclude))
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(result))


@click.group()
def cli() -> None:
    pass


@cli.command()
@LANGUAGE
@A
@B
@EXCLUDE
def levenshtein(language: str, a: Path, b: Path, exclude: tuple[str, ...]) -> None:
    """Token, character and path edit distance between two codebases."""
    report(measure_code_distance, language, a, b, exclude)


@cli.command("git-diff")
@LANGUAGE
@A
@B
@EXCLUDE
def git_diff(language: str, a: Path, b: Path, exclude: tuple[str, ...]) -> None:
    """Normalized git diffstat from the reference `a` to the port `b`."""
    report(measure_git_diff, language, a, b, exclude)
