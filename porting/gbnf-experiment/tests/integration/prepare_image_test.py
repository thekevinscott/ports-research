"""What /shared holds in the real prepare image, per condition.

The clone, the patch, both generated suites, the rule files and the rules
arriving intact through the build arg, all at once. The fixtures are the
listing /shared must hold per condition. One clone and install, then sixteen
builds that rerun only the copy layer.
"""

from itertools import product
from pathlib import Path

import pytest
from python_on_whales import docker

from gbnf_experiment.config import settings
from gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist import (
    assemble_whitelist,
)

FIXTURES = Path(__file__).parent / "fixtures" / "shared"
CONDITIONS = list(product(("python", "javascript"), (False, True), (False, True), (False, True)))


def condition_name(source, unit, source_integration, target_integration) -> str:
    return (
        f"{source}_unit-{unit}_source-integration-{source_integration}"
        f"_target-integration-{target_integration}".lower()
    )


def describe_the_prepare_image():
    @pytest.mark.parametrize(
        "source, unit, source_integration, target_integration",
        CONDITIONS,
        ids=[condition_name(*c) for c in CONDITIONS],
    )
    def it_leaves_the_fixture_listing_in_shared(
        source, unit, source_integration, target_integration
    ):
        name = condition_name(source, unit, source_integration, target_integration)
        rules = assemble_whitelist(
            source,
            include_unit_tests=unit,
            include_source_integration_tests=source_integration,
            include_target_integration_tests=target_integration,
        )
        tag = f"gbnf-prepare-test:{name}"
        docker.build(
            settings.prepare_docker_directory,
            tags=tag,
            build_args={"GBNF_COMMIT": settings.gbnf_commit, "RULES": rules},
            progress=False,
        )
        output = docker.run(tag, ["find", "/shared", "-type", "f"], remove=True)
        listing = sorted(line.removeprefix("/shared/") for line in output.splitlines())

        assert listing == (FIXTURES / f"{name}.txt").read_text().splitlines()
