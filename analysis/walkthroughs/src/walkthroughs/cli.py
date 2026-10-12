import json
from pathlib import Path

import click

from walkthroughs.compare_walkthroughs import compare_walkthroughs
from walkthroughs.pick_similarity import pick_similarity
from walkthroughs.reference_lines import reference_lines
from walkthroughs.sweep_thresholds import sweep_thresholds
from walkthroughs.write_walkthrough import write_walkthrough

DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)
FILE = click.Path(exists=True, dir_okay=False, path_type=Path, resolve_path=True)
OUT = click.Path(path_type=Path, resolve_path=True)
MODEL = click.option("--model", default="claude-opus-5-5", show_default=True)
EFFORT = click.option("--effort", default="high", show_default=True)
EMBEDDINGS_URL = click.option("--embeddings-url", default=None, help="An OpenAI-compatible /v1 base url.")
NO_EMBEDDINGS = click.option("--no-embeddings", is_flag=True, help="Align by word-set Jaccard instead of embeddings.")
THRESHOLD = click.option("--threshold", type=float, default=None, help="Match threshold; 0.8 for embeddings, 0.5 for Jaccard.")


def similarity_or_fail(url: str | None, no_embeddings: bool, threshold: float | None) -> dict:
    try:
        return pick_similarity(url=url, no_embeddings=no_embeddings, threshold=threshold)
    except ValueError as e:
        raise click.UsageError(str(e))


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--implementation", type=DIRECTORY, required=True)
@click.option("--language", type=click.Choice(["python", "typescript"]), required=True)
@click.option("--out", type=OUT, required=True)
@MODEL
@EFFORT
@click.option("--tag", default="", help="Asks for a repeat walkthrough of the same implementation; never shown to the model.")
def write(implementation: Path, language: str, out: Path, model: str, effort: str, tag: str) -> None:
    click.echo(str(write_walkthrough(implementation, language=language, out=out, model=model, effort=effort, tag=tag)))


@cli.command()
@click.option("--reference", type=FILE, required=True)
@click.option("--port", type=FILE, required=True)
@EMBEDDINGS_URL
@NO_EMBEDDINGS
@THRESHOLD
def compare(reference: Path, port: Path, embeddings_url: str | None, no_embeddings: bool, threshold: float | None) -> None:
    similarity = similarity_or_fail(embeddings_url, no_embeddings, threshold)
    walkthroughs = [json.loads(path.read_text())["walkthrough"] for path in (reference, port)]
    compared = compare_walkthroughs(*walkthroughs, similarity)
    swept = sweep_thresholds(*walkthroughs, similarity)
    click.echo(json.dumps({"reference": str(reference), "port": str(port), **compared, "sweep": swept}, indent=2))


@cli.command("reference-lines")
@click.option("--out", type=OUT, required=True)
@EMBEDDINGS_URL
@NO_EMBEDDINGS
@THRESHOLD
@MODEL
@EFFORT
def reference_lines_command(out: Path, embeddings_url: str | None, no_embeddings: bool, threshold: float | None, model: str, effort: str) -> None:
    similarity = similarity_or_fail(embeddings_url, no_embeddings, threshold)
    click.echo(json.dumps(reference_lines(out=out, similarity=similarity, model=model, effort=effort), indent=2))
