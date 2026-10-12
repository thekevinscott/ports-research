from unittest.mock import patch

import pytest

from walkthroughs.pick_similarity import pick_similarity


@pytest.fixture(autouse=True)
def embedding_server():
    with patch("walkthroughs.pick_similarity.embedding_server", side_effect=lambda url, model: {"url": url, "model": model, "server": None}) as m:
        yield m


@pytest.fixture
def embed_text():
    with patch("walkthroughs.pick_similarity.embed_text", side_effect=lambda text, url: [1.0, float(len(text))]) as m:
        yield m


def describe_pick_similarity():
    def it_uses_embeddings_at_the_url_with_a_default_threshold_of_0_8(embed_text):
        similarity = pick_similarity(url="http://host/v1", no_embeddings=False, threshold=None)
        assert (similarity["name"], similarity["threshold"]) == ("embeddings", 0.8)
        assert similarity["score"](["a"], ["a"]) == [[pytest.approx(1.0)]]
        embed_text.assert_called_once_with("a", url="http://host/v1")

    def it_describes_the_embedding_server_once_for_the_requested_model(embed_text, embedding_server):
        similarity = pick_similarity(url="http://host/v1", no_embeddings=False, threshold=None)
        assert similarity["embeddings"] == {"url": "http://host/v1", "model": "qwen3-embedding-0.6b-q8_0", "server": None}
        embedding_server.assert_called_once_with("http://host/v1", "qwen3-embedding-0.6b-q8_0")

    def it_falls_back_to_word_overlap_with_a_default_threshold_of_0_5(embed_text, embedding_server):
        similarity = pick_similarity(url=None, no_embeddings=True, threshold=None)
        assert (similarity["name"], similarity["threshold"]) == ("jaccard", 0.5)
        assert similarity["score"](["a b"], ["b c"]) == [[pytest.approx(1 / 3)]]
        assert similarity["embeddings"] is None
        embed_text.assert_not_called()
        embedding_server.assert_not_called()

    def it_takes_an_explicit_threshold(embed_text):
        assert pick_similarity(url="http://host/v1", no_embeddings=False, threshold=0.7)["threshold"] == 0.7

    def it_needs_a_url_or_the_fallback(embed_text):
        with pytest.raises(ValueError, match="--embeddings-url"):
            pick_similarity(url=None, no_embeddings=False, threshold=None)
