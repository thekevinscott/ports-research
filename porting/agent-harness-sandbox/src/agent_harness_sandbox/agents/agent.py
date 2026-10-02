from pathlib import Path
from typing import Protocol


class Agent(Protocol):
    image: str
    stage: str
    home: str
    transcripts: str
    allow: tuple[str, ...]

    def command(self, prompt: str, *, effort: str, model: str) -> list[str]: ...

    def stage_auth(self, destination: Path) -> None: ...
