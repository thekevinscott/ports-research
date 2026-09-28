import pytest

from porting_harness.render_prompt import render_prompt

TEMPLATE = "Write the port to /target.\n\n{upstream}\n"


@pytest.fixture
def prompt_path(tmp_path):
    path = tmp_path / "prompt.txt"
    path.write_text(TEMPLATE)
    return path


def describe_render_prompt():
    def it_puts_the_upstream_prompt_in_the_slot(prompt_path):
        assert render_prompt(prompt_path, "Port /input/source to rust.") == (
            "Write the port to /target.\n\n"
            "Port /input/source to rust.\n"
        )

    def it_leaves_no_slot_behind(prompt_path):
        assert "{upstream}" not in render_prompt(prompt_path, "Port it.")

    def describe_when_the_upstream_prompt_contains_braces():
        def it_passes_them_through_untouched(prompt_path):
            rendered = render_prompt(prompt_path, "Match {a: 1} and {{b}}.")

            assert "Match {a: 1} and {{b}}." in rendered

    def describe_when_there_is_no_upstream_prompt():
        def it_renders_the_system_prompt_alone(prompt_path):
            assert render_prompt(prompt_path, "") == (
                "Write the port to /target.\n\n\n"
            )
