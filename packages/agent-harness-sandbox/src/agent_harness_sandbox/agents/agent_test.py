from pathlib import Path
from typing import get_protocol_members, get_type_hints

from .agent import Agent


def describe_agent():
    def it_declares_the_whole_contract_an_implementation_must_satisfy():
        assert get_protocol_members(Agent) == {
            "allow",
            "command",
            "dockerfile",
            "home",
            "image",
            "stage_auth",
            "transcripts",
        }

    def it_types_the_dockerfile_as_a_path():
        assert get_type_hints(Agent)["dockerfile"] is Path

    def it_types_the_egress_allowlist_as_a_tuple_of_hosts():
        assert get_type_hints(Agent)["allow"] == tuple[str, ...]
