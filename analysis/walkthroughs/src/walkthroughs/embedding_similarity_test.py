import pytest

from walkthroughs.embedding_similarity import embedding_similarity

VECTORS = {"a": [1.0, 0.0], "b": [0.0, 2.0], "c": [3.0, 3.0]}


def describe_embedding_similarity():
    def it_scores_each_pair_by_the_cosine_of_its_embeddings():
        similarity = embedding_similarity(VECTORS.__getitem__)
        assert similarity(["a", "c"], ["b", "c"]) == [[0.0, pytest.approx(2**-0.5)], [pytest.approx(2**-0.5), pytest.approx(1.0)]]

    def it_embeds_each_distinct_text_once():
        seen = []
        similarity = embedding_similarity(lambda text: seen.append(text) or VECTORS[text])
        similarity(["a", "c"], ["c", "a"])
        similarity(["a"], ["b"])
        assert sorted(seen) == ["a", "b", "c"]
