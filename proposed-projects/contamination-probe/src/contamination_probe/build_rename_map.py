from random import Random

from .generate_synthetic_name import generate_synthetic_name


def build_rename_map(names: list[str], *, seed: int) -> dict[str, str]:
    """A deterministic old-name -> new-name map, one entry per unique name in `names`.

    Iterating a sorted, de-duplicated `names` before drawing keeps the map stable
    regardless of the order symbols were discovered in.
    """
    rng = Random(seed)
    used_names: set[str] = set()
    rename_map: dict[str, str] = {}
    for name in sorted(set(names)):
        candidate = generate_synthetic_name(name, rng)
        while candidate in used_names or candidate == name:
            candidate = generate_synthetic_name(name, rng)
        used_names.add(candidate)
        rename_map[name] = candidate
    return rename_map
