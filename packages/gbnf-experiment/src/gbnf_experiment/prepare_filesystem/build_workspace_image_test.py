import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.build_workspace_image import build_workspace_image

FILES = [Path("reference_implementation/typescript/package.json"), Path("tests/python/validate_test.py")]
AGENT_IMAGE = "agent-harness-sandbox-claude:latest"


@pytest.fixture
def settings(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.build_workspace_image.settings", autospec=True
    ) as m:
        m.workspace_docker_directory = tmp_path / "docker" / "gbnf-workspace"
        m.workspace_image_repository = "gbnf-workspace"
        m.gbnf_commit = "13f1aca"
        yield m


@pytest.fixture
def docker_module(settings):
    with patch(
        "gbnf_experiment.prepare_filesystem.build_workspace_image.docker", autospec=True
    ) as m:
        yield m


def build(**overrides) -> str:
    return build_workspace_image(
        **{"agent_image": AGENT_IMAGE, "files": FILES, "debug": False, **overrides}
    )


def describe_build_workspace_image():
    def it_returns_the_tag_it_built(docker_module):
        tag = build()
        assert docker_module.build.call_args.kwargs["tags"] == tag

    def it_tags_by_the_file_list(docker_module):
        digest = hashlib.sha256(
            b"reference_implementation/typescript/package.json\ntests/python/validate_test.py"
        ).hexdigest()[:16]
        assert build() == f"gbnf-workspace:{digest}"

    def it_gives_different_lists_different_tags(docker_module):
        assert build() != build(files=FILES[:1])

    def it_gives_the_same_list_the_same_tag(docker_module):
        assert build() == build()

    def it_builds_the_workspace_context(docker_module, settings):
        build()
        assert docker_module.build.call_args.args == (settings.workspace_docker_directory,)

    def it_layers_on_the_agent_image(docker_module):
        build(agent_image="agent-harness-sandbox-pi:latest")
        assert docker_module.build.call_args.kwargs["build_args"]["AGENT_IMAGE"] == (
            "agent-harness-sandbox-pi:latest"
        )

    def it_passes_the_pin_so_the_prepare_stage_matches(docker_module):
        build()
        assert docker_module.build.call_args.kwargs["build_args"]["GBNF_COMMIT"] == "13f1aca"

    def it_names_the_files_one_per_line(docker_module):
        build()
        assert docker_module.build.call_args.kwargs["build_args"]["FILES"] == (
            "reference_implementation/typescript/package.json\ntests/python/validate_test.py"
        )

    def it_builds_the_final_stage(docker_module):
        build()
        assert "target" not in docker_module.build.call_args.kwargs

    def it_builds_quietly_unless_debugging(docker_module):
        build()
        assert docker_module.build.call_args.kwargs["progress"] is False
        build(debug=True)
        assert docker_module.build.call_args.kwargs["progress"] == "tty"
