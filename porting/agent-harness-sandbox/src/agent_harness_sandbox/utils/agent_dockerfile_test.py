import pytest

from agent_harness_sandbox.utils.agent_dockerfile import agent_dockerfile


@pytest.fixture
def shipped(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM base\n")
    return dockerfile


def describe_agent_dockerfile():
    def describe_when_modify_is_none():
        def it_yields_the_shipped_dockerfile(shipped):
            with agent_dockerfile(shipped, None) as dockerfile:
                assert dockerfile == shipped

    def describe_when_modify_is_supplied():
        def it_hands_over_the_dockerfiles_text(shipped):
            seen = []
            with agent_dockerfile(shipped, lambda text: seen.append(text) or text):
                pass
            assert seen == ["FROM base\n"]

        def it_yields_a_file_holding_what_modify_returned(shipped):
            with agent_dockerfile(shipped, lambda _: "FROM other\n") as dockerfile:
                assert dockerfile.read_text() == "FROM other\n"

        def it_keeps_the_dockerfiles_name(shipped):
            with agent_dockerfile(shipped, lambda text: text) as dockerfile:
                assert dockerfile.name == "Dockerfile"

        def it_yields_a_file_outside_the_shipped_directory(shipped):
            with agent_dockerfile(shipped, lambda text: text) as dockerfile:
                assert dockerfile.parent != shipped.parent

        def it_leaves_the_dockerfile_on_disk_untouched(shipped):
            with agent_dockerfile(shipped, lambda _: "FROM other\n"):
                pass
            assert shipped.read_text() == "FROM base\n"

        def it_discards_the_temporary_file_when_the_block_ends(shipped):
            with agent_dockerfile(shipped, lambda text: text) as dockerfile:
                written = dockerfile
            assert not written.exists()
