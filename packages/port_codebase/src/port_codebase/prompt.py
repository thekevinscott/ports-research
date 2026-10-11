from pathlib import Path


class Prompt:
    """A prompt template plus the values its slots take.

    Pure: the template plus the variables reconstructs the exact string the
    container was handed. Only the template is formatted, so braces in a
    variable's text pass through untouched.
    """

    def __init__(self, prompt: str | Path, **variables: object) -> None:
        self.template = prompt.read_text() if isinstance(prompt, Path) else prompt
        self.variables = variables

    def format(self, **overrides: object) -> str:
        return self.template.format(**{**self.variables, **overrides})

    def __str__(self) -> str:
        return self.format()
