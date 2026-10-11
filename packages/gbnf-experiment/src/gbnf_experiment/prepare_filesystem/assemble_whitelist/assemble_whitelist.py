"""Compose the one rsync whitelist the prepare image copies with.

rsync takes the first matching rule, so the test includes go ahead of the
whitelist that withholds tests. A language with no lines gets no files. The
image receives the composed text as one build arg and never sees a flag or a
language.
"""

from typing import Literal

from .compose import compose

Language = Literal["python", "javascript"]

OTHER: dict[Language, Language] = {"python": "javascript", "javascript": "python"}
FOOTER = "\n+ */\n- *\n"


def assemble_whitelist(
    source: Language,
    *,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
) -> str:
    source_names = (
        (["unit-tests"] if include_unit_tests else [])
        + (["integration-tests"] if include_source_integration_tests else [])
        + ["source"]
    )
    target_names = ["integration-tests"] if include_target_integration_tests else []
    return compose(source, source_names) + compose(OTHER[source], target_names) + FOOTER
