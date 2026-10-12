import json
from pathlib import Path

import click

from measure_api.compare_cases import compare_cases
from measure_api.generate_corpus import generate_corpus
from measure_api.run_corpus import run_corpus

DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)
FILE = click.Path(exists=True, dir_okay=False, path_type=Path, resolve_path=True)
OUT = click.Path(path_type=Path, resolve_path=True)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--out", type=OUT, required=True)
@click.option("--seed", type=int, required=True)
@click.option("--count", type=int, required=True, help="Number of grammars.")
def generate(out: Path, seed: int, count: int) -> None:
    generate_corpus(out=out, seed=seed, count=count)


@cli.command()
@click.option("--corpus", type=DIRECTORY, required=True)
@click.option("--implementation", type=DIRECTORY, required=True)
@click.option("--language", type=click.Choice(["python", "typescript"]), required=True)
@click.option("--out", type=OUT, required=True)
def run(corpus: Path, implementation: Path, language: str, out: Path) -> None:
    run_corpus(corpus=corpus, implementation=implementation, language=language, out=out)


@cli.command()
@click.option("--reference", type=FILE, required=True)
@click.option("--port", type=FILE, required=True)
@click.option("--out", type=OUT, required=True)
def compare(reference: Path, port: Path, out: Path) -> None:
    try:
        report = compare_cases(reference=reference, port=port)
    except ValueError as e:
        raise click.ClickException(str(e))
    out.write_text(json.dumps(report, indent=2) + "\n")
