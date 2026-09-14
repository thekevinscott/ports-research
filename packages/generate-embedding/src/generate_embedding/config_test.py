import os
from unittest.mock import patch

import pytest

from generate_embedding.config import Settings


@pytest.fixture
def env_base_url():
    with patch.dict(os.environ, {"GENERATE_EMBEDDING_BASE_URL": "http://localhost:8080/v1"}):
        yield


@pytest.fixture
def env_api_key():
    with patch.dict(
        os.environ,
        {
            "GENERATE_EMBEDDING_BASE_URL": "http://localhost:8080/v1",
            "GENERATE_EMBEDDING_API_KEY": "sk-test",
        },
    ):
        yield


def describe_settings():
    def it_has_no_default_base_url():
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):
                Settings()

    def it_reads_the_base_url_from_the_env(env_base_url):
        assert Settings().base_url == "http://localhost:8080/v1"

    def it_defaults_the_api_key_to_none(env_base_url):
        assert Settings().api_key is None

    def it_reads_the_api_key_from_the_env(env_api_key):
        assert Settings().api_key.get_secret_value() == "sk-test"

    def it_does_not_leak_the_api_key_in_repr(env_api_key):
        assert "sk-test" not in repr(Settings())
