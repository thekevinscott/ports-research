from pathlib import Path


def render_prompt(prompt_path: Path, upstream: str) -> str:
    """The harness's system prompt with the caller's upstream prompt in its slot.

    Pure, so the template digest plus the upstream text reconstructs the exact
    string the container was handed. Only the template is formatted, so braces
    in the upstream text pass through untouched.
    """
    return prompt_path.read_text().format(upstream=upstream)
