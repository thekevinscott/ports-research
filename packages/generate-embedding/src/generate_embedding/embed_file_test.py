import httpx
import pytest

from generate_embedding.embed_file import embed_file


@pytest.fixture
def code_file(tmp_path):
    path = tmp_path / "add.py"
    path.write_text("def add(a, b):\n    return a + b\n")
    return path


def mock_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def describe_embed_file():
    def it_posts_the_files_text_as_input(code_file):
        captured = {}

        def handler(request):
            captured["url"] = str(request.url)
            captured["body"] = request.content
            return httpx.Response(
                200, json={"data": [{"embedding": [0.1, 0.2, 0.3]}], "model": "nomic-embed-text"}
            )

        embed_file(
            code_file,
            model="nomic-embed-text",
            base_url="http://localhost:8080/v1",
            client=mock_client(handler),
        )
        assert captured["url"] == "http://localhost:8080/v1/embeddings"
        assert b"def add(a, b)" in captured["body"]

    def it_returns_the_embedding_model_and_dimension(code_file):
        client = mock_client(
            lambda request: httpx.Response(
                200, json={"data": [{"embedding": [0.1, 0.2, 0.3, 0.4]}], "model": "text-embed-3"}
            )
        )
        result = embed_file(
            code_file, model="text-embed-3", base_url="http://localhost:8080/v1", client=client
        )
        assert result == {
            "model": "text-embed-3",
            "dimension": 4,
            "embedding": [0.1, 0.2, 0.3, 0.4],
        }

    def it_sends_no_authorization_header_without_an_api_key(code_file):
        captured = {}

        def handler(request):
            captured["headers"] = request.headers
            return httpx.Response(200, json={"data": [{"embedding": [0.1]}]})

        embed_file(
            code_file, model="m", base_url="http://localhost:8080/v1", client=mock_client(handler)
        )
        assert "authorization" not in captured["headers"]

    def it_sends_the_api_key_as_a_bearer_token(code_file):
        captured = {}

        def handler(request):
            captured["headers"] = request.headers
            return httpx.Response(200, json={"data": [{"embedding": [0.1]}]})

        embed_file(
            code_file,
            model="m",
            base_url="http://localhost:8080/v1",
            api_key="sk-test",
            client=mock_client(handler),
        )
        assert captured["headers"]["authorization"] == "Bearer sk-test"

    def it_strips_a_trailing_slash_from_the_base_url(code_file):
        captured = {}

        def handler(request):
            captured["url"] = str(request.url)
            return httpx.Response(200, json={"data": [{"embedding": [0.1]}]})

        embed_file(
            code_file,
            model="m",
            base_url="http://localhost:8080/v1/",
            client=mock_client(handler),
        )
        assert captured["url"] == "http://localhost:8080/v1/embeddings"

    def it_raises_on_an_http_error(code_file):
        client = mock_client(lambda request: httpx.Response(500, text="boom"))
        with pytest.raises(httpx.HTTPStatusError):
            embed_file(code_file, model="m", base_url="http://localhost:8080/v1", client=client)
