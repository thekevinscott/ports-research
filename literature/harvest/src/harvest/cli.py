import pathlib

import click

from harvest import citations, phase2

papers_option = click.option(
    "--papers",
    type=click.Path(file_okay=False, path_type=pathlib.Path),
    default=pathlib.Path("papers"),
    show_default=True,
    help="Corpus directory, resolved against the working directory.",
)


@click.group()
def cli() -> None:
    """Harvest the arXiv paper corpus behind the literature survey."""


@cli.command("citations")
@papers_option
def citations_command(papers: pathlib.Path) -> None:
    """Phase 1: download papers cited by inline arXiv id in the seeds."""
    citations.harvest(papers)


@cli.command("resolve")
@papers_option
def resolve_command(papers: pathlib.Path) -> None:
    """Phase 2A: title-resolve seed references that lack an inline arXiv id."""
    phase2.resolve(papers)


@cli.command("convert")
@papers_option
def convert_command(papers: pathlib.Path) -> None:
    """Phase 2B: convert every harvested PDF to markdown."""
    phase2.convert(papers)


@cli.command("phase2")
@papers_option
def phase2_command(papers: pathlib.Path) -> None:
    """Phase 2A then 2B, the original harvest_phase2.py entry point."""
    phase2.resolve(papers)
    phase2.convert(papers)
