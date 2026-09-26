from pathlib import Path

import httpx


def embed_file(
    path: Path,
    *,
    model: str,
    base_url: str,
    api_key: str | None = None,
    client: httpx.Client | None = None,
) -> dict:
    """Embed one code file's text against an OpenAI-compatible /v1/embeddings endpoint.

    `client` is caller-supplied so a test can swap in a transport instead of
    reaching the network; when omitted a real httpx.Client is built and closed here.
    """
    text = path.read_text()
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    owns_client = client is None
    client = client or httpx.Client(timeout=60)
    try:
        response = client.post(
            f"{base_url.rstrip('/')}/embeddings",
            json={"model": model, "input": text},
            headers=headers,
        )
        response.raise_for_status()
    finally:
        if owns_client:
            client.close()

    body = response.json()
    embedding = body["data"][0]["embedding"]
    return {
        "model": body.get("model", model),
        "dimension": len(embedding),
        "embedding": embedding,
    }
