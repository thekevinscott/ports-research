import pytest

from porting_harness.prompt import Prompt

TEMPLATE = "Write the port to /target.\n\n{upstream}\n"


@pytest.fixture
def prompt_path(tmp_path):
    path = tmp_path / "prompt.txt"
    path.write_text(TEMPLATE)
    return path


def describe_prompt():
    def describe_when_the_template_is_a_string():
        def it_fills_the_slots(prompt_path):
            assert str(Prompt(TEMPLATE, upstream="Port it.")) == (
                "Write the port to /target.\n\nPort it.\n"
            )

        def it_leaves_no_slot_behind():
            assert "{upstream}" not in str(Prompt(TEMPLATE, upstream="Port it."))

    def describe_when_the_template_is_a_path():
        def it_reads_the_file(prompt_path):
            assert str(Prompt(prompt_path, upstream="Port /input/python to rust.")) == (
                "Write the port to /target.\n\n"
                "Port /input/python to rust.\n"
            )

        def it_refuses_a_file_that_is_not_there(tmp_path):
            with pytest.raises(FileNotFoundError):
                Prompt(tmp_path / "gone.txt")

    def describe_format():
        def it_takes_the_variables_the_constructor_was_given(prompt_path):
            assert Prompt(prompt_path, upstream="Port it.").format() == str(
                Prompt(prompt_path, upstream="Port it.")
            )

        def it_overrides_a_constructor_variable(prompt_path):
            rendered = Prompt(prompt_path, upstream="Port it.").format(upstream="Port that.")

            assert "Port that." in rendered
            assert "Port it." not in rendered

        def it_supplies_a_variable_the_constructor_left_out(prompt_path):
            assert "Port it." in Prompt(prompt_path).format(upstream="Port it.")

    def describe_when_a_variable_contains_braces():
        def it_passes_them_through_untouched(prompt_path):
            rendered = str(Prompt(prompt_path, upstream="Match {a: 1} and {{b}}."))

            assert "Match {a: 1} and {{b}}." in rendered

    def describe_when_a_slot_has_no_variable():
        def it_raises(prompt_path):
            with pytest.raises(KeyError, match="upstream"):
                str(Prompt(prompt_path))
