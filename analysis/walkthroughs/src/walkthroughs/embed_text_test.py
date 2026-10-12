import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from walkthroughs.embed_text import MODEL, embed_text


@pytest.fixture
def calls():
    """Each generate-embedding call: its argv, its environment and the text of the file it was given."""
    recorded = []

    def run(command, **kwargs):
        path = Path(command[command.index("generate-embedding") + 1])
        recorded.append({"command": command, "env": kwargs["env"], "text": path.read_text()})
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps({"embedding": [0.1, 0.2]}), stderr="")

    with patch("walkthroughs.embed_text.subprocess.run", autospec=True, side_effect=run) as m:
        m.recorded = recorded
        yield m


def describe_embed_text():
    def it_embeds_the_text_through_the_generate_embedding_cli_at_the_url(calls):
        assert embed_text("a step", url="http://host/v1") == [0.1, 0.2]
        [call] = calls.recorded
        assert call["command"][-2:] == ["--model", MODEL]
        assert call["env"]["GENERATE_EMBEDDING_BASE_URL"] == "http://host/v1"
        assert call["text"] == "a step"

    def it_raises_with_stderr_when_the_cli_fails(calls):
        calls.side_effect = lambda command, **kwargs: subprocess.CompletedProcess(command, 1, stdout="", stderr="connection refused")
        with pytest.raises(RuntimeError, match="connection refused"):
            embed_text("a step", url="http://host/v1")
