from pathlib import Path


def included_files(reference: Path) -> list[Path]:
    """Every file the prepare image put under reference, relative and sorted.

    Read back rather than predicted: the image is what decided the corpus, so
    the manifest records what came out of it and not what the host asked for.
    """
    return sorted(
        path.relative_to(reference)
        for path in reference.rglob("*")
        if path.is_file() and not path.is_symlink()
    )
