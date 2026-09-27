"""Compose the rsync whitelists the prepare image copies with.

The rule files live beside the Dockerfile. rsync takes the first matching rule,
so the test includes go ahead of the whitelist that withholds tests. The image
receives the composed text as build args and never sees a flag.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ...config import settings

Language = Literal["python", "javascript"]

OTHER: dict[Language, Language] = {"python": "javascript", "javascript": "python"}
FILTERS = settings.prepare_docker_directory / "reference-filters"


@dataclass(frozen=True)
class Whitelist:
    source_language: Language
    source_rules: str
    target_language: Language
    target_rules: str

    @property
    def build_args(self) -> dict[str, str]:
        return {
            "SOURCE_LANGUAGE": self.source_language,
            "SOURCE_RULES": self.source_rules,
            "TARGET_LANGUAGE": self.target_language,
            "TARGET_RULES": self.target_rules,
        }


def compose(filters: Path, language: Language, names: list[str]) -> str:
    return "".join((filters / language / f"{name}.rules").read_text() for name in names)


def assemble_whitelist(
    source: Language,
    *,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    filters: Path = FILTERS,
) -> Whitelist:
    source_names = (
        (["unit-tests"] if include_unit_tests else [])
        + (["integration-tests"] if include_source_integration_tests else [])
        + ["source"]
    )
    target = OTHER[source]
    return Whitelist(
        source_language=source,
        source_rules=compose(filters, source, source_names),
        target_language=target,
        target_rules=(
            compose(filters, target, ["integration-tests", "harness"])
            if include_target_integration_tests
            else ""
        ),
    )
