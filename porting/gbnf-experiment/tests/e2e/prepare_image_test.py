"""What /shared holds in the real prepare image, per condition.

The host-side layout_test proves what the rule files mean to rsync. This
proves the image agrees: the clone, the patch, both generated suites, and
the rules arriving intact through the build arg. One clone and install,
then sixteen builds that rerun only the copy layer.
"""

from itertools import product
from pathlib import Path

import pytest
from python_on_whales import docker

from gbnf_experiment.config import settings
from gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist import (
    assemble_whitelist,
)

FIXTURES = (
    Path(__file__).resolve().parents[2]
    / "src/gbnf_experiment/prepare_filesystem/assemble_whitelist/fixtures/shared"
)
CONDITIONS = {
    f"{source}_unit-{unit}_source-integration-{source_integration}"
    f"_target-integration-{target_integration}".lower(): (
        source,
        unit,
        source_integration,
        target_integration,
    )
    for source, unit, source_integration, target_integration in product(
        ("python", "javascript"), (False, True), (False, True), (False, True)
    )
}


@pytest.fixture(params=CONDITIONS, ids=list(CONDITIONS))
def shared_listing(request) -> tuple[str, list[str]]:
    name = request.param
    source, unit, source_integration, target_integration = CONDITIONS[name]
    rules = assemble_whitelist(
        source,
        include_unit_tests=unit,
        include_source_integration_tests=source_integration,
        include_target_integration_tests=target_integration,
    )
    tag = f"gbnf-prepare-e2e:{name}"
    docker.build(
        settings.prepare_docker_directory,
        tags=tag,
        build_args={"GBNF_COMMIT": settings.gbnf_commit, "RULES": rules},
        progress=False,
    )
    output = docker.run(tag, ["find", "/shared", "-type", "f"], remove=True)
    return name, sorted(line.removeprefix("/shared/") for line in output.splitlines())


def describe_the_prepare_image():
    def it_leaves_the_fixture_listing_in_shared(shared_listing):
        name, listing = shared_listing
        assert listing == (FIXTURES / f"{name}.txt").read_text().splitlines()
