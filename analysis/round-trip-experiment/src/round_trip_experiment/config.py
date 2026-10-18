from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
# Back-translations bank here and never in a data/, so they cannot be mistaken for
# forward ports or muddy the banked corpus.
REVERSE_DIRECTORY = PACKAGE_ROOT / "reverse"
STAGING_DIRECTORY = Path.home() / ".cache" / "ports" / "round-trip-experiment" / "derivations"
