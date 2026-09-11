from random import Random

_WORD_BANK = [
    "anchor", "harbor", "lattice", "meadow", "quartz", "cinder", "willow", "granite",
    "beacon", "thicket", "hollow", "ember", "copper", "marsh", "orchard", "ridge",
    "silo", "timber", "vessel", "wharf", "basin", "grove", "kiln", "loam",
    "moraine", "pinnacle", "quarry", "ravine", "spindle", "trellis", "vault", "yarrow",
    "bramble", "cistern", "furrow", "glade", "hearth", "inlet", "juniper", "knoll",
]


def generate_synthetic_name(original: str, rng: Random) -> str:
    """A neutral two-word replacement identifier matching `original`'s casing style."""
    first, second = rng.choice(_WORD_BANK), rng.choice(_WORD_BANK)
    if original.isupper():
        return f"{first}_{second}".upper()
    if original[:1].isupper():
        return f"{first.capitalize()}{second.capitalize()}"
    return f"{first}_{second}"
