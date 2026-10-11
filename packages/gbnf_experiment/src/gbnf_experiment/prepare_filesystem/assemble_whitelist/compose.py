from pathlib import Path

FILTERS = Path(__file__).parent / "reference-filters"


def compose(language: str, names: list[str]) -> str:
    return "".join((FILTERS / language / f"{name}.rules").read_text() for name in names)
