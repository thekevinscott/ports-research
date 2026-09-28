"""The composed rules, run through real rsync, against the tree at the pin.

The rule files mean whatever rsync says they mean, so rsync is the oracle,
not a mock. fixtures/<gbnf sha>.txt lists every file under packages/gbnf at
that commit once both integration suites are generated, node_modules omitted;
the shared fixtures are what the image's /shared must hold per condition.
"""

import subprocess
from itertools import product
from pathlib import Path

import pytest

from gbnf_experiment.config import settings

from .assemble_whitelist import assemble_whitelist

FIXTURES = Path(__file__).parent / "fixtures"
RSYNC = ["rsync", "-a", "--prune-empty-dirs"]
LANGUAGES = ("python", "javascript")
CONDITIONS = {
    f"{source}_unit-{unit}_source-integration-{source_integration}"
    f"_target-integration-{target_integration}".lower(): (
        source,
        unit,
        source_integration,
        target_integration,
    )
    for source, unit, source_integration, target_integration in product(
        LANGUAGES, (False, True), (False, True), (False, True)
    )
}


def tree_at_pin() -> list[str]:
    return (FIXTURES / f"{settings.gbnf_commit}.txt").read_text().splitlines()


def rsync_layout(rules: str, tmp_path: Path) -> list[str]:
    source = tmp_path / "gbnf"
    for path in tree_at_pin():
        (source / path).parent.mkdir(parents=True, exist_ok=True)
        (source / path).touch()
    shared = tmp_path / "shared"
    shared.mkdir()
    (tmp_path / "rules").write_text(rules)
    subprocess.run(
        [*RSYNC, f"--filter=merge {tmp_path / 'rules'}", f"{source}/", f"{shared}/"],
        check=True,
    )
    return sorted(str(p.relative_to(shared)) for p in shared.rglob("*") if p.is_file())


@pytest.fixture(params=CONDITIONS, ids=list(CONDITIONS))
def condition(request):
    return request.param, CONDITIONS[request.param]


def describe_the_shared_layout():
    def it_uses_the_rsync_invocation_the_dockerfile_uses():
        dockerfile = (settings.prepare_docker_directory / "Dockerfile").read_text()
        assert f'{" ".join(RSYNC)} --filter="merge ' in dockerfile

    def it_matches_the_fixture_for_the_condition(condition, tmp_path):
        name, (source, unit, source_integration, target_integration) = condition
        rules = assemble_whitelist(
            source,
            include_unit_tests=unit,
            include_source_integration_tests=source_integration,
            include_target_integration_tests=target_integration,
        )
        expected = (FIXTURES / "shared" / f"{name}.txt").read_text().splitlines()
        assert rsync_layout(rules, tmp_path) == expected
