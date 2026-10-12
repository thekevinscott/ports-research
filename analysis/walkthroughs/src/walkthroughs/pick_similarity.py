from functools import partial

from walkthroughs.embed_text import embed_text
from walkthroughs.embedding_similarity import embedding_similarity
from walkthroughs.jaccard_similarity import jaccard_similarity


def pick_similarity(*, url: str | None, no_embeddings: bool, threshold: float | None) -> dict:
    """Embedding cosine at url, threshold 0.8 by default; or, with no_embeddings, word-set Jaccard, threshold 0.5."""
    if no_embeddings:
        return {"name": "jaccard", "threshold": 0.5 if threshold is None else threshold, "score": jaccard_similarity}
    if url is None:
        raise ValueError("pass --embeddings-url or --no-embeddings")
    return {"name": "embeddings", "threshold": 0.8 if threshold is None else threshold, "score": embedding_similarity(partial(embed_text, url=url))}
