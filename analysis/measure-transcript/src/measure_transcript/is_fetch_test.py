import pytest

from measure_transcript.is_fetch import is_fetch


def describe_is_fetch():
    @pytest.mark.parametrize("words", [
        ["curl", "-sL", "https://x"],
        ["wget", "https://x"],
        ["pip", "install", "pytest"],
        ["pip3", "install", "pytest"],
        ["python3", "-m", "pip", "install", "pytest"],
        ["uv", "pip", "install", "pytest"],
        ["npm", "install"],
        ["npm", "i", "vitest"],
        ["timeout", "30", "curl", "https://x"],
    ])
    def it_names_network_fetches(words):
        assert is_fetch(words) is True

    @pytest.mark.parametrize("words", [["pip", "list"], ["npm", "test"], ["python3", "-m", "pytest"], ["uv", "sync"], []])
    def it_ignores_other_commands(words):
        assert is_fetch(words) is False
