import sys
from pathlib import Path

import click

from .render import render_transcript


@click.command()
@click.argument(
    "path",
    type=click.Path(exists=True, dir_okay=True, file_okay=True, path_type=Path, resolve_path=True),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write the HTML page here instead of printing it to stdout.",
)
@click.option(
    "--title",
    default=None,
    help="Page title and header heading. Defaults to the transcript file or directory name.",
)
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    default=False,
    help="Open the rendered page in the default web browser (implies --output when none is given).",
)
def cli(path: Path, output: Path | None, title: str | None, open_browser: bool) -> None:
    """Render a Claude session transcript (.jsonl) as a self-contained HTML page.

    PATH is a transcript file or a directory containing one or more .jsonl
    files (such as a run's transcript/ tree). The page is printed to stdout
    unless --output is given.
    """
    try:
        html_page = render_transcript(path, title=title)
    except Exception as e:
        raise click.ClickException(str(e))

    if open_browser and output is None:
        output = Path.cwd() / "transcript.html"

    if output is not None:
        output.write_text(html_page, encoding="utf-8")
        click.echo(str(output))
        if open_browser:
            _open(output)
    else:
        sys.stdout.write(html_page)


def _open(path: Path) -> None:
    import webbrowser

    webbrowser.open(path.as_uri())
