import shutil
from pathlib import Path
from random import Random

from .build_rename_map import build_rename_map
from .discover_public_symbols import discover_public_symbols
from .generate_synthetic_name import generate_synthetic_name
from .rename_library import rename_library
from .rename_symbols import rename_symbols
from .reshuffle_file_layout import reshuffle_file_layout
from .write_rename_manifest import write_rename_manifest


def perturb_reference_tree(
    source_dir: Path, output_dir: Path, *, library_name: str, seed: int
) -> str:
    """Copies `source_dir` to `output_dir`, renames the library, its public symbols, and layout.

    The library's new name, every symbol's new name, and the new file layout are all
    drawn from `seed`, so the same seed against the same source tree always reproduces
    the same output tree. Returns the new library name — the caller needs it to locate
    the renamed package.

    A separate grading suite that imports the library by its old name is untouched by
    any of this: rope only rewrites imports it can resolve, and by the time symbols are
    renamed the old library name no longer exists on disk for it to resolve against. The
    full mapping is written to `rename-manifest.json` in `output_dir` so a caller can
    apply it to a grading suite independently.
    """
    shutil.copytree(source_dir, output_dir)

    new_library_name = generate_synthetic_name(library_name, Random(seed))
    rename_library(output_dir, library_name, new_library_name)

    sites = discover_public_symbols(output_dir)
    rename_map = build_rename_map([site.name for site in sites], seed=seed)
    rename_symbols(output_dir, sites, rename_map)

    reshuffle_file_layout(output_dir / new_library_name, seed=seed)

    write_rename_manifest(
        output_dir / "rename-manifest.json",
        library_name={"old": library_name, "new": new_library_name},
        symbol_rename_map=rename_map,
    )

    return new_library_name
