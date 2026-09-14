from unittest.mock import MagicMock, patch

import pytest

from generate_embedding.embed_file import embed_file


@pytest.fixture
def httpx():
    with patch("generate_embedding.embed_file.httpx") as mock_httpx:
        yield mock_httpx


@pytest.fixture
def code_file(tmp_path):
    path = tmp_path / "add.py"
    path.write_text("def add(a, b):\n    return a + b\n")
    return path


@pytest.fixture
def client():
    client = MagicMock()
    client.post.return_value.json.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}],
        "model": "nomic-embed-text",
    }
    return client


def describe_embed_file():
    def it_posts_the_files_text_as_input(httpx, code_file, client):
        embed_file(code_file, model="m", base_url="http://host/v1", client=client)
        assert client.post.call_args.kwargs["json"] == {
            "model": "m",
            "input": "def add(a, b):\n    return a + b\n",
        }

    def it_posts_to_the_embeddings_path(httpx, code_file, client):
        embed_file(code_file, model="m", base_url="http://host/v1", client=client)
        assert client.post.call_args.args == ("http://host/v1/embeddings",)

    def it_strips_a_trailing_slash_from_the_base_url(httpx, code_file, client):
        embed_file(code_file, model="m", base_url="http://host/v1/", client=client)
        assert client.post.call_args.args == ("http://host/v1/embeddings",)

    def it_sends_no_authorization_header_without_an_api_key(httpx, code_file, client):
        embed_file(code_file, model="m", base_url="http://host/v1", client=client)
        assert client.post.call_args.kwargs["headers"] == {}

    def it_sends_the_api_key_as_a_bearer_token(httpx, code_file, client):
        embed_file(code_file, model="m", base_url="http://host/v1", api_key="sk", client=client)
        assert client.post.call_args.kwargs["headers"] == {"Authorization": "Bearer sk"}

    def it_returns_the_embedding_model_and_dimension(httpx, code_file, client):
        result = embed_file(code_file, model="m", base_url="http://host/v1", client=client)
        assert result == {
            "model": "nomic-embed-text",
            "dimension": 3,
            "embedding": [0.1, 0.2, 0.3],
        }

    def it_falls_back_to_the_requested_model_when_the_body_omits_one(httpx, code_file, client):
        client.post.return_value.json.return_value = {"data": [{"embedding": [0.1]}]}
        result = embed_file(code_file, model="m", base_url="http://host/v1", client=client)
        assert result["model"] == "m"

    def it_raises_when_the_response_is_an_error(httpx, code_file, client):
        client.post.return_value.raise_for_status.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            embed_file(code_file, model="m", base_url="http://host/v1", client=client)

    def it_leaves_a_caller_supplied_client_open(httpx, code_file, client):
        embed_file(code_file, model="m", base_url="http://host/v1", client=client)
        client.close.assert_not_called()

    def it_builds_its_own_client_when_none_is_given(httpx, code_file):
        embed_file(code_file, model="m", base_url="http://host/v1")
        httpx.Client.assert_called_once_with(timeout=60)

    def it_closes_the_client_it_built(httpx, code_file):
        embed_file(code_file, model="m", base_url="http://host/v1")
        httpx.Client.return_value.close.assert_called_once_with()

    def it_closes_the_client_it_built_when_the_response_is_an_error(httpx, code_file):
        httpx.Client.return_value.post.return_value.raise_for_status.side_effect = RuntimeError
        with pytest.raises(RuntimeError):
            embed_file(code_file, model="m", base_url="http://host/v1")
        httpx.Client.return_value.close.assert_called_once_with()
