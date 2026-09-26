import json
from pathlib import Path

import click

from .compare_embeddings import compare_embeddings
from .embed_codebase import embed_codebase

EXISTING_DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--language", type=click.Choice(["python", "typescript"]), required=True)
@click.option("--target", type=EXISTING_DIRECTORY, required=True)
@click.option("--exclude", multiple=True, help="fnmatch pattern against each relative path and its parts")
@click.option("--out", type=click.Path(file_okay=False, path_type=Path, resolve_path=True), required=True)
@click.option("--model", required=True, help="Model name passed through to generate-embedding.")
@click.option("--strip-comments", is_flag=True, help="Embed each file with its comments removed.")
def embed(
    language: str, target: Path, exclude: tuple[str, ...], out: Path, model: str, strip_comments: bool
) -> None:
    try:
        report = embed_codebase(
            language=language,
            target=target,
            exclude=list(exclude),
            out=out,
            model=model,
            strip_comments=strip_comments,
        )
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))


@cli.command()
@click.option("--a", "a", type=EXISTING_DIRECTORY, required=True)
@click.option("--b", "b", type=EXISTING_DIRECTORY, required=True)
def compare(a: Path, b: Path) -> None:
    try:
        report = compare_embeddings(a=a, b=b)
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))
