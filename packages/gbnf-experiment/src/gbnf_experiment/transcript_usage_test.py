import json
from pathlib import Path

import pytest

from gbnf_experiment.transcript_usage import transcript_usage


def assistant(message_id: str, **usage) -> str:
    return json.dumps({"type": "assistant", "message": {"id": message_id, "usage": usage}})


USAGE_A = dict(input_tokens=10, cache_creation_input_tokens=100, cache_read_input_tokens=1000, output_tokens=5)
USAGE_B = dict(input_tokens=20, cache_creation_input_tokens=0, cache_read_input_tokens=2000, output_tokens=7)


@pytest.fixture
def run(tmp_path: Path) -> Path:
    transcript = tmp_path / "transcript" / "-workspace"
    transcript.mkdir(parents=True)
    (transcript / "session.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"type": "user", "message": {"content": "port it"}}),
                assistant("msg_a", **USAGE_A),
                assistant("msg_a", **USAGE_A),
                "not json",
                assistant("msg_b", **USAGE_B),
            ]
        )
    )
    return tmp_path


def describe_transcript_usage():
    def it_sums_every_token_kind_across_distinct_api_calls(run):
        assert transcript_usage(run)["total_tokens"] == 1115 + 2027

    def it_counts_each_message_id_once(run):
        assert transcript_usage(run)["api_calls"] == 2

    def it_is_empty_when_the_run_has_no_transcript(tmp_path):
        assert transcript_usage(tmp_path) == {}
