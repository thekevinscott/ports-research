from pathlib import Path

import pytest

from agent_harness_sandbox.build_setup_layer import build_setup_layer
from agent_harness_sandbox.errors import AgentHarnessSandboxError


@pytest.fixture
def setup_script(tmp_path: Path) -> Path:
    script = tmp_path / "setup.sh"
    script.write_text("#!/bin/sh\necho installing\n")
    return script


def describe_build_setup_layer():
    def it_builds_a_layer_and_returns_its_tag(docker, builds, setup_script):
        tag = build_setup_layer(base_image="an-agent:latest", setup_script=setup_script, debug=False)
        assert tag == "an-agent-setup:latest"
        assert builds == ["an-agent-setup:latest"]

    def it_derives_the_tag_from_whatever_base_image_the_caller_names(docker, builds, setup_script):
        tag = build_setup_layer(base_image="another-agent:v2", setup_script=setup_script, debug=False)
        assert tag == "another-agent-setup:v2"

    def it_refuses_a_setup_script_that_does_not_exist(docker, tmp_path):
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            build_setup_layer(base_image="an-agent:latest", setup_script=tmp_path / "gone.sh", debug=False)
