from pathlib import Path

PROMPT_PATH = Path(__file__).parent / "prompt.txt"


def render_prompt(*, source_language: str, target_language: str) -> str:
    """The prompt the container is handed, naming the layout the host assembled.

    Pure, so the template plus the arm's two languages reconstructs the exact
    string. porting-harness frames the task and names the container paths; this
    template describes the /input layout, which is the host's to describe.
    """
    return PROMPT_PATH.read_text().format(
        source_language=source_language,
        target_language=target_language,
    )
