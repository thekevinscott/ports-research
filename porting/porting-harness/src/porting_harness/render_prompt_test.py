import pytest

from porting_harness.render_prompt import render_prompt

TEMPLATE = "Port reference_implementation/ to {target_language}.\n"


@pytest.fixture
def prompt_path(tmp_path):
    path = tmp_path / "prompt.txt"
    path.write_text(TEMPLATE)
    return path


def describe_render_prompt():
    def it_substitutes_the_target_language(prompt_path):
        assert render_prompt(prompt_path, "python") == (
            "Port reference_implementation/ to python.\n"
        )

    def it_renders_each_direction_differently(prompt_path):
        assert render_prompt(prompt_path, "python") != render_prompt(
            prompt_path, "typescript"
        )

    def it_leaves_a_template_without_the_placeholder_alone(tmp_path):
        path = tmp_path / "prompt.txt"
        path.write_text("Port the reference implementation.\n")
        assert render_prompt(path, "python") == "Port the reference implementation.\n"

    def it_raises_on_a_placeholder_it_cannot_fill(tmp_path):
        path = tmp_path / "prompt.txt"
        path.write_text("Port to {target}.\n")
        with pytest.raises(KeyError):
            render_prompt(path, "python")
