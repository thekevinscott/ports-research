"""Compose the one rsync whitelist the prepare image copies with.

The rule files live beside this module, one folder per upstream package
directory, every pattern anchored to that directory. rsync takes the first
matching rule, so the test includes go ahead of the whitelist that withholds
tests. A language with no lines gets no files. The image receives the composed
text as one build arg and never sees a flag or a language.
"""

from pathlib import Path
from typing import Literal

Language = Literal["python", "javascript"]

OTHER: dict[Language, Language] = {"python": "javascript", "javascript": "python"}
FILTERS = Path(__file__).parent / "reference-filters"
FOOTER = "\n+ */\n- *\n"


def compose(filters: Path, language: Language, names: list[str]) -> str:
    return "".join((filters / language / f"{name}.rules").read_text() for name in names)


def assemble_whitelist(
    source: Language,
    *,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    filters: Path | None = None,
) -> str:
    filters = filters or FILTERS
    source_names = (
        (["unit-tests"] if include_unit_tests else [])
        + (["integration-tests"] if include_source_integration_tests else [])
        + ["source"]
    )
    target_names = ["integration-tests"] if include_target_integration_tests else []
    return (
        compose(filters, source, source_names)
        + compose(filters, OTHER[source], target_names)
        + FOOTER
    )
