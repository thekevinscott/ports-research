from pathlib import Path


def prepared_directory(cache_directory: Path) -> Path:
    return cache_directory / "ports" / "gbnf-experiment" / "prepared"


def staging_directory(cache_directory: Path) -> Path:
    return cache_directory / "ports" / "round-trip-experiment" / "derivations"
