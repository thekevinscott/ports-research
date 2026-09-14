from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SymbolSite:
    """One module-scope public definition: where it lives and what it's called."""

    path: Path
    lineno: int
    name: str
