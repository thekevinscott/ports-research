"""What the prepare image puts at /reference, for all sixteen conditions.

Kevin, 2026-09-26: "We _will_ want tests on the gbnf-experiment container,
specifically that the reference folder produced for the 8 conditions is what we
expect."

This builds the real image. The listings in `fixtures/reference/` are the corpus
contract: a change to the filter rules, the patches or the pin shows up here as
a diff, and a reviewer reads the diff rather than trusting the rules.
"""

from pathlib import Path

import pytest
from python_on_whales import docker

from gbnf_experiment.config import settings

DOCKER_DIRECTORY = Path(__file__).parents[2] / "docker" / "gbnf-prepare"
FIXTURES = Path(__file__).parent / "fixtures" / "reference"

INTEGRATION_SUITES = {
    "none": (False, False),
    "python": (True, False),
    "typescript": (False, True),
    "both": (True, True),
}
CONDITIONS = {
    f"source-{source_language}_unit-{str(unit).lower()}_integration-{integration}": (
        source_language,
        unit,
        *INTEGRATION_SUITES[integration],
    )
    for source_language in ("typescript", "python")
    for unit in (False, True)
    for integration in INTEGRATION_SUITES
}


def expected_listing(condition: str) -> list[str]:
    return (FIXTURES / f"{condition}.txt").read_text().split()


def build_reference(condition: str, destination: Path) -> list[str]:
    """Build the image for one condition and list what it left at /reference."""
    source_language, unit, python, typescript = CONDITIONS[condition]
    tag = f"gbnf-prepare:test-{condition}"
    docker.build(
        DOCKER_DIRECTORY,
        tags=tag,
        build_args={
            "GBNF_COMMIT": settings.gbnf_commit,
            "SOURCE_LANGUAGE": source_language,
            "INCLUDE_UNIT_TESTS": str(unit).lower(),
            "INCLUDE_PYTHON_TESTS": str(python).lower(),
            "INCLUDE_TYPESCRIPT_TESTS": str(typescript).lower(),
        },
        progress=False,
    )
    container = docker.create(tag)
    try:
        docker.copy((container, "/reference"), destination)
    finally:
        container.remove()
    reference = destination / "reference"
    return sorted(
        str(path.relative_to(reference))
        for path in reference.rglob("*")
        if path.is_file() and not path.is_symlink()
    )


def describe_the_reference_the_prepare_image_produces():
    @pytest.mark.parametrize("condition", CONDITIONS, ids=list(CONDITIONS))
    def it_holds_exactly_the_files_the_condition_calls_for(tmp_path, condition):
        assert build_reference(condition, tmp_path) == expected_listing(condition)
