import pytest

from gbnf_experiment.render_prompt import render_prompt


def describe_render_prompt():
    @pytest.mark.parametrize(
        ("source_language", "target_language"),
        [("javascript", "python"), ("python", "javascript")],
        ids=["javascript-to-python", "python-to-javascript"],
    )
    def it_names_the_directory_each_language_lives_in(
        source_language, target_language
    ):
        prompt = render_prompt(
            source_language=source_language, target_language=target_language
        )
        assert f"Port the {source_language} implementation under /input/{source_language}" in prompt
        assert f"to {target_language} in /workspace/ported_implementation" in prompt
        assert f"Where /input/{target_language} holds tests" in prompt

    @pytest.mark.parametrize(
        ("source_language", "target_language"),
        [("javascript", "python"), ("python", "javascript")],
        ids=["javascript-to-python", "python-to-javascript"],
    )
    def it_leaves_no_placeholder_unfilled(source_language, target_language):
        prompt = render_prompt(
            source_language=source_language, target_language=target_language
        )
        assert "{" not in prompt
        assert "}" not in prompt

    def it_points_the_agent_at_the_one_input_mount():
        prompt = render_prompt(source_language="javascript", target_language="python")
        assert prompt.startswith("/input holds the gbnf package")
