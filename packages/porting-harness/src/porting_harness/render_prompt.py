from pathlib import Path


def render_prompt(prompt_path: Path, target_language: str) -> str:
    """The prompt template with the run's target language substituted in.

    Pure, so a template digest plus the arm's target language reconstructs the
    exact string the container was handed. One template renders to a different
    prompt in each arm.
    """
    return prompt_path.read_text().format(target_language=target_language)
