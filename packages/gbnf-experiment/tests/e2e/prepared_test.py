"""What the workspace image a real run ran in actually holds.

The reference implementation the agent is handed is baked into that image.
Everything here is read back out of the image the manifest names, through
`docker run`, so a workspace the pipeline never built cannot pass.
"""

import json
import subprocess
from pathlib import Path

import pytest


def docker_run(image: str, *command: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "run", "--rm", image, *command], capture_output=True, text=True
    )


@pytest.fixture(scope="module")
def manifest(completed_run: Path) -> dict:
    return json.loads((completed_run / "manifest.json").read_text())


@pytest.fixture(scope="module")
def image(manifest: dict) -> str:
    return manifest["sandbox"]["image_id"]


@pytest.fixture(scope="module")
def workspace(image: str) -> list[str]:
    """Every file under /workspace, as the agent saw it, relative to /workspace."""
    listing = docker_run(image, "find", "/workspace", "-type", "f", "-printf", "%P\\n")
    assert listing.returncode == 0, listing.stderr
    return sorted(listing.stdout.split())


def describe_the_workspace_image():
    def it_holds_exactly_what_the_manifest_says_it_does(workspace, manifest):
        assert workspace == sorted(manifest["reference_implementation"]["included"])

    def it_holds_the_typescript_reference_and_no_other(workspace):
        """The default run ports typescript; python is the answer key and stays out."""
        assert "reference_implementation/typescript/package.json" in workspace
        assert "reference_implementation/typescript/src/index.ts" in workspace
        assert not any(path.startswith("reference_implementation/python/") for path in workspace)

    def it_withholds_the_colocated_tests(workspace):
        assert not any(path.endswith(".test.ts") for path in workspace)

    def it_withholds_the_generated_suites_by_default(workspace):
        assert not any(path.startswith("tests/") for path in workspace)

    def it_carries_no_installed_dependencies(workspace):
        assert not any("node_modules" in Path(path).parts for path in workspace)

    def it_is_readable_but_not_writable_by_the_agent(image):
        read = docker_run(image, "cat", "/workspace/reference_implementation/typescript/package.json")
        assert read.returncode == 0
        write = docker_run(
            image, "sh", "-c", "echo x >> /workspace/reference_implementation/typescript/package.json"
        )
        assert write.returncode != 0
        assert "Permission denied" in write.stderr


def describe_the_prepare_stage():
    @pytest.fixture(scope="module")
    def prepared(completed_run: Path) -> list[str]:
        """The listing the host selected from, read back off the prepare image."""
        listing = docker_run("gbnf-prepare:latest", "cat", "/prepared.list")
        assert listing.returncode == 0, listing.stderr
        return listing.stdout.split()

    def it_prepares_a_source_tree_for_both_languages(prepared):
        assert any(path.startswith("reference_implementation/typescript/src/") for path in prepared)
        assert any(path.startswith("reference_implementation/python/gbnf/") for path in prepared)

    def it_prepares_a_test_suite_for_both_languages(prepared):
        assert any(path.startswith("tests/typescript/") and path.endswith(".test.ts") for path in prepared)
        assert any(path.startswith("tests/python/") and path.endswith("_test.py") for path in prepared)

    def it_ships_grammar_fixtures_beside_the_python_suite(prepared):
        grammars = [p for p in prepared if p.startswith("tests/python/iteration/grammars/")]
        assert len([p for p in grammars if p.endswith(".gbnf")]) == 8
        assert len([p for p in grammars if p.endswith(".json")]) == 8

    def it_ships_the_runner_config_with_the_typescript_suite(prepared):
        assert "tests/typescript/vitest.config.unit.ts" in prepared

    def it_ships_no_readme_with_either_suite(prepared):
        assert "tests/typescript/README.md" not in prepared
        assert "tests/python/README.md" not in prepared
