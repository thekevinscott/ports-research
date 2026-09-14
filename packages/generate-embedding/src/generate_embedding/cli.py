import json
from pathlib import Path

import click

from .config import Settings
from .embed_file import embed_file
from .write_vector import write_vector


@click.command()
@click.argument(
    "path", type=click.Path(exists=True, dir_okay=False, path_type=Path, resolve_path=True)
)
@click.option("--model", required=True, help="Model name to send to the embeddings endpoint.")
@click.option(
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write the embedding as a float32 .npy array here instead of printing JSON.",
)
def cli(path: Path, model: str, output: Path | None) -> None:
    try:
        settings = Settings()
        result = embed_file(
            path,
            model=model,
            base_url=settings.base_url,
            api_key=settings.api_key.get_secret_value() if settings.api_key else None,
        )
        if output is not None:
            write_vector(output, result["embedding"])
            click.echo(str(output))
        else:
            click.echo(json.dumps(result))
    except Exception as e:
        raise click.ClickException(str(e))
