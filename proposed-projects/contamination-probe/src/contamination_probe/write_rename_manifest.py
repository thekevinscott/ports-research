import json
from pathlib import Path


def write_rename_manifest(
    manifest_path: Path, *, library_name: dict[str, str], symbol_rename_map: dict[str, str]
) -> None:
    """Records the seed's full old-name -> new-name mapping alongside the perturbed tree.

    `rename_symbols` only ever applies this mapping inside the copied tree itself, so a
    separate grading suite that imports the library by its old name has no other way to
    learn what its own imports need to become.
    """
    manifest_path.write_text(
        json.dumps({"library_name": library_name, "symbols": symbol_rename_map}, indent=2)
    )
